"""
Alert Pydantic Schemas (Request/Response Validation)

Schemas for alert configuration - the core feature of the application.
Each alert represents a saved search that gets checked periodically.

Key design decisions:
- brand_ids and brand_names are both optional (user can search without brands)
- catalog_ids and catalog_names are both optional (user can search without categories)
- We store both IDs and names for better UX (IDs for API, names for display)
- notification_config is a dict that can be extended without schema changes
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, Dict, Any


class AlertBase(BaseModel):
    """
    Base schema with common alert fields.

    This is inherited by AlertCreate and AlertUpdate to avoid duplication.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable alert name")
    country_code: str = Field(..., min_length=2, max_length=2, description="Vinted country code (e.g., 'fr', 'de')")
    search_text: Optional[str] = Field(None, max_length=500, description="Free-text search query")
    brand_ids: Optional[str] = Field(None, description="Comma-separated brand IDs from Vinted")
    brand_names: Optional[str] = Field(None, description="Comma-separated brand names for display")
    catalog_ids: Optional[str] = Field(None, description="Comma-separated category IDs from Vinted")
    catalog_names: Optional[str] = Field(None, description="Comma-separated category names for display")
    price_min: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    price_max: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code (ISO 4217)")
    sizes: Optional[str] = Field(None, description="Comma-separated size filters (future feature)")
    conditions: Optional[str] = Field(None, description="Comma-separated condition filters (future feature)")
    colors: Optional[str] = Field(None, description="Comma-separated color filters (future feature)")
    check_interval_minutes: int = Field(default=15, ge=5, le=1440, description="How often to check for new items (5-1440 minutes)")
    notification_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Notification settings (email, webhook, etc.)"
    )

    @field_validator('price_max')
    @classmethod
    def validate_price_range(cls, v, info):
        """Ensure price_max is greater than price_min if both are set."""
        price_min = info.data.get('price_min')
        if price_min is not None and v is not None and v < price_min:
            raise ValueError('price_max must be greater than price_min')
        return v

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v):
        """Ensure country code is lowercase."""
        return v.lower()


class AlertCreate(AlertBase):
    """
    Schema for creating a new alert.

    This is what the client sends to POST /api/alerts.
    The user_id will be extracted from JWT token, not from request body.
    """
    is_active: bool = Field(default=True, description="Whether alert is active")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Nike Sneakers France",
                "country_code": "fr",
                "search_text": "sneakers",
                "brand_ids": "53",
                "brand_names": "Nike",
                "catalog_ids": "1193",
                "catalog_names": "Shoes",
                "price_min": 20.0,
                "price_max": 100.0,
                "currency": "EUR",
                "check_interval_minutes": 15,
                "notification_config": {
                    "email": True,
                    "webhook_url": "https://hooks.slack.com/..."
                },
                "is_active": True
            }
        }
    )


class AlertUpdate(BaseModel):
    """
    Schema for updating an existing alert.

    All fields are optional - only provided fields will be updated.
    This is what the client sends to PUT /api/alerts/{alert_id}.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    search_text: Optional[str] = Field(None, max_length=500)
    brand_ids: Optional[str] = None
    brand_names: Optional[str] = None
    catalog_ids: Optional[str] = None
    catalog_names: Optional[str] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    sizes: Optional[str] = None
    conditions: Optional[str] = None
    colors: Optional[str] = None
    check_interval_minutes: Optional[int] = Field(None, ge=5, le=1440)
    notification_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Alert Name",
                "price_max": 150.0,
                "is_active": False
            }
        }
    )


class AlertResponse(BaseModel):
    """
    Schema for alert data in responses.

    This is what the API returns for:
    - POST /api/alerts (after creation)
    - GET /api/alerts (list all)
    - GET /api/alerts/{alert_id} (get one)
    - PUT /api/alerts/{alert_id} (after update)
    """
    id: str = Field(..., description="Alert UUID")
    user_id: Optional[str] = Field(None, description="Owner user UUID (null for self-hosted)")
    name: str = Field(..., description="Alert name")
    country_code: str = Field(..., description="Country code")
    search_text: Optional[str] = Field(None, description="Free-text search query")
    brand_ids: Optional[str] = Field(None, description="Comma-separated brand IDs")
    brand_names: Optional[str] = Field(None, description="Comma-separated brand names")
    catalog_ids: Optional[str] = Field(None, description="Comma-separated category IDs")
    catalog_names: Optional[str] = Field(None, description="Comma-separated category names")
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")
    currency: str = Field(..., description="Currency code")
    sizes: Optional[str] = Field(None, description="Size filters")
    conditions: Optional[str] = Field(None, description="Condition filters")
    colors: Optional[str] = Field(None, description="Color filters")
    check_interval_minutes: int = Field(..., description="Check interval in minutes")
    notification_config: Dict[str, Any] = Field(..., description="Notification settings")
    is_active: bool = Field(..., description="Whether alert is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_checked_at: Optional[datetime] = Field(None, description="Last scan timestamp")
    last_found_count: int = Field(..., description="Items found in last scan")
    total_found_count: int = Field(..., description="Total items found across all scans")

    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Nike Sneakers France",
                "country_code": "fr",
                "search_text": "sneakers",
                "brand_ids": "53",
                "brand_names": "Nike",
                "catalog_ids": "1193",
                "catalog_names": "Shoes",
                "price_min": 20.0,
                "price_max": 100.0,
                "currency": "EUR",
                "sizes": None,
                "conditions": None,
                "colors": None,
                "check_interval_minutes": 15,
                "notification_config": {"email": True},
                "is_active": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "last_checked_at": "2024-01-15T08:30:00Z",
                "last_found_count": 5,
                "total_found_count": 42
            }
        }
    )
