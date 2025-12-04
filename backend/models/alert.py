"""
Alert Model

This is the core model that stores user alert configurations. Each alert represents
a saved search on Vinted with specific criteria (brands, categories, price range, etc.).

The scanner service periodically checks these alerts and sends notifications when
new items matching the criteria are found.

Key design decisions:
- Store both IDs and names for brands/categories (IDs for API calls, names for display)
- Use comma-separated strings for multiple brands/categories (simple, works well for 1-10 items)
- JSON column for notification preferences (flexible for different channels)
- Track last check time and found count for monitoring
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database import Base


class Alert(Base):
    """
    User alert configuration for Vinted marketplace monitoring.

    Each alert represents a saved search that gets checked periodically.
    When new items are found, notifications are sent via configured channels.
    """
    __tablename__ = "alerts"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to user (optional for self-hosted mode)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    # Basic configuration
    name = Column(String(255), nullable=False)  # User-friendly name like "Nike Sneakers"
    country_code = Column(String(2), nullable=False, index=True)  # e.g., "fr", "ie", "de"

    # Search parameters
    search_text = Column(String(500), nullable=True)  # Free text search (e.g., "vintage jacket")

    # Brands - Store both IDs and names
    # IDs are used for Vinted API calls, names for display in UI
    brand_ids = Column(Text, nullable=True)  # Comma-separated: "53,14,92"
    brand_names = Column(Text, nullable=True)  # Comma-separated: "Nike,Adidas,Puma"

    # Categories - Store both IDs and names
    catalog_ids = Column(Text, nullable=True)  # Comma-separated: "1193,1920"
    catalog_names = Column(Text, nullable=True)  # Comma-separated: "Hats,Accessories"

    # Price range
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    currency = Column(String(3), nullable=False, default="EUR")  # ISO 4217 currency code

    # Size filters (future enhancement)
    sizes = Column(Text, nullable=True)  # Comma-separated size IDs

    # Condition filters (future enhancement)
    # Vinted has: New with tags, New without tags, Very good, Good, Satisfactory
    conditions = Column(Text, nullable=True)  # Comma-separated condition IDs

    # Color filters (future enhancement)
    colors = Column(Text, nullable=True)  # Comma-separated color IDs

    # Notification configuration
    # JSON format: {"email": true, "slack": false, "telegram": true, "webhook_url": "..."}
    notification_config = Column(JSON, nullable=False, default=dict)

    # Scanning configuration
    check_interval_minutes = Column(Integer, nullable=False, default=15)  # How often to check
    is_active = Column(Boolean, default=True, nullable=False)  # Can pause without deleting

    # Tracking metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_checked_at = Column(DateTime, nullable=True)  # When scanner last ran this alert
    last_found_count = Column(Integer, default=0, nullable=False)  # Items found in last check
    total_found_count = Column(Integer, default=0, nullable=False)  # Total items found (all time)

    # Relationships
    user = relationship("User", back_populates="alerts")
    item_history = relationship("ItemHistory", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Alert {self.name} ({self.country_code})>"

    @property
    def brand_list(self):
        """Convert comma-separated brand_ids to list"""
        return [b.strip() for b in self.brand_ids.split(",")] if self.brand_ids else []

    @property
    def catalog_list(self):
        """Convert comma-separated catalog_ids to list"""
        return [c.strip() for c in self.catalog_ids.split(",")] if self.catalog_ids else []
