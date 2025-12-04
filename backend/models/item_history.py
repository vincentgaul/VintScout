"""
Item History Model (Deduplication)

This model prevents sending duplicate notifications about the same Vinted items.

The problem:
- Scanner runs every X minutes
- Same items appear in multiple scans
- Without deduplication, user gets spammed with repeat notifications

The solution:
- Track every item we've seen for each alert
- Before sending notification, check if item_id exists in history
- Only notify about truly NEW items

Performance consideration:
- This table grows quickly (every found item is recorded)
- Indexed on (alert_id, item_id) for fast lookups
- Consider TTL cleanup job (delete records older than 30 days)
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database import Base


class ItemHistory(Base):
    """
    Item history for deduplication and tracking.

    Records every Vinted item found by an alert to prevent duplicate notifications.
    Also provides history view for users to see what was found.
    """
    __tablename__ = "item_history"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    alert_id = Column(String(36), ForeignKey("alerts.id"), nullable=False, index=True)

    # Vinted item information
    item_id = Column(String(50), nullable=False, index=True)  # Vinted's item ID
    title = Column(String(500), nullable=False)  # Item title
    price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")

    # URLs for user to click through
    url = Column(Text, nullable=False)  # Link to item on Vinted
    image_url = Column(Text, nullable=True)  # Main product image

    # Additional metadata (optional, for richer notifications)
    brand_name = Column(String(255), nullable=True)
    size = Column(String(50), nullable=True)
    condition = Column(String(50), nullable=True)

    # Tracking
    found_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When we first saw it
    notified_at = Column(DateTime, nullable=True)  # When we sent notification (null = not notified)

    # Relationships
    alert = relationship("Alert", back_populates="item_history")

    # Composite index for fast duplicate checking
    __table_args__ = (
        Index('idx_alert_item', 'alert_id', 'item_id', unique=True),  # Prevent true duplicates
        Index('idx_found_at', 'found_at'),  # For time-based queries
    )

    def __repr__(self):
        return f"<ItemHistory {self.title} - ${self.price}>"

    @classmethod
    def exists(cls, session, alert_id, item_id):
        """
        Check if an item has already been seen for this alert.

        Args:
            session: Database session
            alert_id: Alert UUID
            item_id: Vinted item ID

        Returns:
            True if item exists in history (duplicate), False if new
        """
        return session.query(cls)\
            .filter(cls.alert_id == alert_id)\
            .filter(cls.item_id == item_id)\
            .first() is not None

    @classmethod
    def record(cls, session, alert_id, item_data):
        """
        Record a new item in history.

        Args:
            session: Database session
            alert_id: Alert UUID
            item_data: Dictionary with item information from Vinted API

        Returns:
            ItemHistory object (newly created)
        """
        history = cls(
            alert_id=alert_id,
            item_id=item_data["id"],
            title=item_data["title"],
            price=item_data["price"],
            currency=item_data.get("currency", "EUR"),
            url=item_data["url"],
            image_url=item_data.get("photo", {}).get("url"),
            brand_name=item_data.get("brand_title"),
            size=item_data.get("size_title"),
            condition=item_data.get("status")
        )
        session.add(history)
        return history
