"""
Category Model (Hierarchical Cache)

This model stores Vinted's category tree (hierarchical taxonomy of item types).
Categories are organized in a tree structure: Women > Accessories > Hats

Why cache categories?
- Vinted's category tree rarely changes (maybe monthly)
- Loading the tree on every page load would be slow
- We cache the entire tree and refresh periodically (weekly cron job)

Tree structure:
- parent_id creates the hierarchy (self-referencing foreign key)
- level tracks depth (0 = root, 1 = subcategory, 2 = sub-subcategory)
- path stores full path for easy display ("/Women/Accessories/Hats")

This enables:
- Fast category picker UI (tree view)
- Search by category name
- Hierarchical filtering (select "Women" to include all subcategories)
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database import Base


class Category(Base):
    """
    Category cache table with hierarchical tree structure.

    Stores Vinted's catalog/category tree. Categories are country-specific
    and organized hierarchically (parent-child relationships).
    """
    __tablename__ = "categories"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Vinted's category ID (used in API calls)
    vinted_id = Column(String(50), nullable=False)

    # Category information
    name = Column(String(255), nullable=False, index=True)  # e.g., "Hats"
    code = Column(String(80), nullable=True)  # e.g., "WOMEN_ROOT"
    country_code = Column(String(2), nullable=True, index=True)  # Null for global categories

    # Hierarchy - Self-referencing for tree structure
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True, index=True)
    level = Column(Integer, default=0, nullable=False)  # 0 = root, 1 = child, 2 = grandchild, etc.

    # Full path for display and search
    # e.g., "/Women/Accessories/Hats"
    path = Column(Text, nullable=False)

    # URLs
    url = Column(String(256), nullable=True)
    url_en = Column(String(256), nullable=True)

    # Metadata from Vinted
    item_count = Column(Integer, nullable=True)  # Number of items in this category

    # Cache management
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    # One category can have many children - configured for self-referential tree
    # parent = One-to-one relationship to parent category (many-to-one from child perspective)
    # children = One-to-many relationship to child categories
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all"
    )

    # Composite indexes for fast queries
    __table_args__ = (
        Index('idx_category_country_vinted_id', 'country_code', 'vinted_id'),
        Index('idx_category_country_parent', 'country_code', 'parent_id'),
        Index('idx_category_country_name', 'country_code', 'name'),
    )

    def __repr__(self):
        return f"<Category {self.path} ({self.country_code})>"

    @property
    def has_children(self):
        """Check if this category has subcategories"""
        return self.children is not None and len(self.children) > 0

    def to_dict(self, include_children=True):
        """
        Convert category to dictionary (for JSON responses).

        Args:
            include_children: Whether to recursively include child categories

        Returns:
            Dictionary representation of category and its children
        """
        result = {
            "id": self.id,
            "vinted_id": self.vinted_id,
            "name": self.name,
            "level": self.level,
            "item_count": self.item_count,
            "has_children": self.has_children
        }

        if include_children and self.has_children:
            result["children"] = [
                child.to_dict(include_children=True)
                for child in sorted(self.children, key=lambda c: c.name)
            ]

        return result

    @classmethod
    def get_root_categories(cls, session, country_code=None):
        """
        Get all root-level categories.
        
        Args:
            session: Database session
            country_code: Optional country code (ignored for global categories)

        Returns:
            List of root Category objects (level=0, parent_id=None)
        """
        query = session.query(cls).filter(cls.parent_id == None)
        
        # If we still have country-specific categories mixed in, filter by it
        # But for global migration, we mostly ignore it or look for null
        # query = query.filter(or_(cls.country_code == country_code, cls.country_code == None))
        
        return query.order_by(cls.name).all()

    @classmethod
    def search_by_name(cls, session, query, country_code=None, limit=20):
        """
        Search categories by name (flat search, not hierarchical).

        Args:
            session: Database session
            query: Search string
            country_code: Ignored for global categories
            limit: Max results

        Returns:
            List of Category objects matching the query
        """
        return session.query(cls)\
            .filter(cls.name.ilike(f"%{query}%"))\
            .order_by(cls.level, cls.name)\
            .limit(limit)\
            .all()
