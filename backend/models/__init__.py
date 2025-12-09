"""
Models Package

This package contains all SQLAlchemy database models.

Import all models here so Alembic can detect them for migrations.
When you run 'alembic revision --autogenerate', it scans this package
to find model definitions and compare them with the current database schema.

Important: Always import Base first, then import models.
"""

from backend.database import Base

# Import all models so Alembic can see them
from backend.models.user import User
from backend.models.alert import Alert
from backend.models.brand import Brand
from backend.models.category import Category
from backend.models.item_history import ItemHistory
from backend.models.size import Size
from backend.models.condition import Condition

# Export all models for easy importing elsewhere
__all__ = [
    "Base",
    "User",
    "Alert",
    "Brand",
    "Category",
    "ItemHistory",
    "Size",
    "Condition"
]
