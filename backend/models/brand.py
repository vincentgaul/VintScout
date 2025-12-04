"""
Brand Model (Cache Table)

This model caches brand information from Vinted to enable fast brand search.
Instead of hitting Vinted's API every time a user types in the brand search,
we cache results locally for 30 days.

Three-tier caching strategy:
1. Pre-seeded popular brands (top 100 per country) - instant lookup
2. Dynamic brands fetched from Vinted API - cached after first search
3. 30-day TTL - automatically refresh stale data

This dramatically improves UX:
- Cached lookups: < 100ms
- API fallback: < 500ms
- Target: >80% cache hit rate
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index
from datetime import datetime, timedelta
import uuid

from backend.database import Base


class Brand(Base):
    """
    Brand cache table for fast autocomplete lookups.

    Stores brand information fetched from Vinted API with TTL-based invalidation.
    Brands are country-specific (Nike in France may have different ID than Nike in Ireland).
    """
    __tablename__ = "brands"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Vinted's brand ID (the actual ID used in API calls)
    # This is what we need to pass to Vinted's search endpoint
    vinted_id = Column(String(50), nullable=False)

    # Brand information
    name = Column(String(255), nullable=False, index=True)  # e.g., "Nike"
    country_code = Column(String(2), nullable=False, index=True)  # e.g., "fr"

    # Metadata from Vinted
    item_count = Column(Integer, nullable=True)  # Number of items for this brand
    is_popular = Column(Boolean, default=False, nullable=False)  # Pre-seeded popular brand

    # Cache management
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Composite index for fast lookups: search by name within a country
    __table_args__ = (
        Index('idx_brand_country_name', 'country_code', 'name'),
        Index('idx_brand_country_vinted_id', 'country_code', 'vinted_id'),
    )

    def __repr__(self):
        return f"<Brand {self.name} ({self.country_code}) - ID:{self.vinted_id}>"

    def is_stale(self, ttl_days=30):
        """
        Check if this cache entry is stale (older than TTL).

        Args:
            ttl_days: Time to live in days (default: 30)

        Returns:
            True if cache entry should be refreshed
        """
        if not self.updated_at:
            return True
        age = datetime.utcnow() - self.updated_at
        return age > timedelta(days=ttl_days)

    @classmethod
    def search_query(cls, session, query, country_code, limit=10):
        """
        Search brands by name prefix (for autocomplete).

        Args:
            session: Database session
            query: Search string (e.g., "nik")
            country_code: Country code (e.g., "fr")
            limit: Max results to return

        Returns:
            List of Brand objects matching the query
        """
        return session.query(cls)\
            .filter(cls.country_code == country_code)\
            .filter(cls.name.ilike(f"{query}%"))\
            .order_by(cls.is_popular.desc(), cls.item_count.desc())\
            .limit(limit)\
            .all()
