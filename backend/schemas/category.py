"""
Category Pydantic Schemas (Response Validation)

Schemas for hierarchical category tree responses.
Categories form a tree structure: Women > Accessories > Hats

Key features:
- Recursive structure (children contain CategoryResponse objects)
- Lightweight for tree views (no timestamps)
- Supports both flat search and hierarchical tree endpoints
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class CategoryResponse(BaseModel):
    """
    Schema for category data in tree responses.

    This is what the API returns for:
    - GET /api/categories?country_code=fr (root categories)
    - GET /api/categories/{category_id} (single category with children)
    - GET /api/categories/search?q=hats&country_code=fr (flat search)

    Used in frontend category picker (tree component or autocomplete).
    """
    id: str = Field(..., description="Internal UUID")
    vinted_id: str = Field(..., description="Vinted's category ID (used in search API)")
    name: str = Field(..., description="Category name for display")
    level: int = Field(..., description="Tree depth (0=root, 1=child, 2=grandchild, etc.)")
    item_count: Optional[int] = Field(None, description="Number of items in this category")
    has_children: bool = Field(..., description="Whether this category has subcategories")
    children: Optional[List['CategoryResponse']] = Field(None, description="Child categories (recursive)")

    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "vinted_id": "1193",
                "name": "Shoes",
                "level": 1,
                "item_count": 50234,
                "has_children": True,
                "children": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "vinted_id": "1194",
                        "name": "Sneakers",
                        "level": 2,
                        "item_count": 25678,
                        "has_children": False,
                        "children": None
                    },
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440002",
                        "vinted_id": "1195",
                        "name": "Boots",
                        "level": 2,
                        "item_count": 12345,
                        "has_children": False,
                        "children": None
                    }
                ]
            }
        }
    )


class CategorySearchQuery(BaseModel):
    """
    Schema for category search query parameters.

    Validates GET /api/categories/search query params.
    """
    q: str = Field(..., min_length=1, max_length=100, description="Search query")
    country_code: str = Field(..., min_length=2, max_length=2, description="Country code")
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "q": "shoes",
                "country_code": "fr",
                "limit": 20
            }
        }
    )


class CategoryTreeQuery(BaseModel):
    """
    Schema for category tree query parameters.

    Validates GET /api/categories query params for fetching root categories.
    """
    country_code: str = Field(..., min_length=2, max_length=2, description="Country code")
    include_children: bool = Field(default=True, description="Whether to include child categories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "country_code": "fr",
                "include_children": True
            }
        }
    )
