"""
Schemas Package

This package contains all Pydantic schemas for request/response validation.

Pydantic v2 automatically validates:
- Data types (str, int, float, datetime, etc.)
- Constraints (min/max length, ranges, regex patterns)
- Business logic (custom validators)

Import all schemas here for easy importing elsewhere.
"""

# User schemas
from backend.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse
)

# Alert schemas
from backend.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse
)

# Brand schemas
from backend.schemas.brand import (
    BrandResponse,
    BrandSearchQuery
)

# Category schemas
from backend.schemas.category import (
    CategoryResponse,
    CategorySearchQuery,
    CategoryTreeQuery
)

# ItemHistory schemas
from backend.schemas.item_history import (
    ItemHistoryResponse,
    ItemHistoryListQuery
)

# Export all schemas
__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    # Alert
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    # Brand
    "BrandResponse",
    "BrandSearchQuery",
    # Category
    "CategoryResponse",
    "CategorySearchQuery",
    "CategoryTreeQuery",
    # ItemHistory
    "ItemHistoryResponse",
    "ItemHistoryListQuery",
]
