"""
Brand Pydantic Schemas (Response Validation)

Schemas for brand autocomplete responses.
Brands are cached from Vinted API for fast lookups when creating alerts.

Key features:
- Lightweight response for autocomplete (only essential fields)
- No timestamps exposed to clients (internal cache management)
- vinted_id is what gets sent to Vinted API when searching
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BrandResponse(BaseModel):
    """
    Schema for brand data in autocomplete responses.

    This is what the API returns for:
    - GET /api/brands/search?q=nike&country_code=fr

    Used in frontend autocomplete component when user types brand names.
    """
    id: str = Field(..., description="Internal UUID (for database relationships)")
    vinted_id: str = Field(..., description="Vinted's brand ID (used in search API)")
    name: str = Field(..., description="Brand name for display")

    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "vinted_id": "53",
                "name": "Nike"
            }
        }
    )


class BrandSearchQuery(BaseModel):
    """
    Schema for brand search query parameters.

    Validates GET /api/brands/search query params.
    """
    q: str = Field(..., min_length=1, max_length=100, description="Search query")
    country_code: str = Field(..., min_length=2, max_length=2, description="Country code")
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "q": "nike",
                "country_code": "fr",
                "limit": 20
            }
        }
    )
