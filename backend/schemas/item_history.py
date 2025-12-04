"""
ItemHistory Pydantic Schemas (Response Validation)

Schemas for displaying found Vinted items to users.
Each item represents a product that matched an alert's search criteria.

Key features:
- Rich metadata for display (title, image, price, brand, size, condition)
- Links to Vinted product page (url)
- Tracking info (when found, when notified)
"""

from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import Optional


class ItemHistoryResponse(BaseModel):
    """
    Schema for item history data in responses.

    This is what the API returns for:
    - GET /api/alerts/{alert_id}/history (all items found for an alert)
    - GET /api/history (all items found across all user's alerts)

    Used in frontend to show users what items were found.
    """
    id: str = Field(..., description="History record UUID")
    alert_id: str = Field(..., description="Alert that found this item")
    item_id: str = Field(..., description="Vinted's item ID")
    title: str = Field(..., description="Item title/description")
    price: float = Field(..., description="Item price")
    currency: str = Field(..., description="Currency code")
    url: str = Field(..., description="Link to item on Vinted")
    image_url: Optional[str] = Field(None, description="Main product image URL")
    brand_name: Optional[str] = Field(None, description="Brand name")
    size: Optional[str] = Field(None, description="Size (e.g., 'M', '42', 'US 10')")
    condition: Optional[str] = Field(None, description="Item condition (e.g., 'New', 'Good', 'Satisfactory')")
    found_at: datetime = Field(..., description="When this item was first found")
    notified_at: Optional[datetime] = Field(None, description="When user was notified (null = notification pending/failed)")

    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "alert_id": "660e8400-e29b-41d4-a716-446655440001",
                "item_id": "3456789012",
                "title": "Nike Air Max 90 White - Size 42",
                "price": 65.0,
                "currency": "EUR",
                "url": "https://www.vinted.fr/items/3456789012",
                "image_url": "https://images.vinted.net/t/...",
                "brand_name": "Nike",
                "size": "42",
                "condition": "Good",
                "found_at": "2024-01-15T08:30:00Z",
                "notified_at": "2024-01-15T08:30:15Z"
            }
        }
    )


class ItemHistoryListQuery(BaseModel):
    """
    Schema for item history list query parameters.

    Validates query params for GET /api/alerts/{alert_id}/history.
    Supports pagination and filtering.
    """
    limit: int = Field(default=50, ge=1, le=200, description="Max results per page")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    notified_only: bool = Field(default=False, description="Only show items that were notified")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "limit": 50,
                "offset": 0,
                "notified_only": False
            }
        }
    )
