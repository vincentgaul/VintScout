"""
Brand API Routes

Brand search using local database cache of 12,632+ brands.
Provides partial/fuzzy matching for brand autocomplete.

Endpoints:
- GET /api/brands/search - Search brands by keyword (e.g., "nike" → "Nike")

Authentication: Optional (works for both authenticated and anonymous users)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db
from backend.schemas import BrandResponse
from backend.models import Brand


router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("/search", response_model=List[BrandResponse])
def search_brands(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    country_code: str = Query(..., min_length=2, max_length=5, description="Country code (e.g., 'fr')"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search brands by name using Vinted's brand API.

    This endpoint provides partial/fuzzy matching - searching "nike" will match "Nike",
    "thursday" will match "Thursday Boot Company", etc.

    Query parameters:
        - q: Search query (e.g., "nike", "thursday")
        - country_code: 2-letter country code (e.g., "fr")
        - limit: Maximum results to return (default: 20, max: 100)

    Response:
        List of brand objects with id, title, and other metadata

    Example:
        GET /api/brands/search?q=nike&country_code=fr&limit=10
        Returns: [{"id": 53, "title": "Nike", ...}]
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Brand search requested: '{q}'")

    try:
        # Search brands from database (brand IDs are universal across countries)
        brands = Brand.search_query(db, q, limit=limit)

        # Convert to response schema
        return [
            BrandResponse(
                id=brand.id,
                vinted_id=brand.vinted_id,
                name=brand.name
            )
            for brand in brands
        ]

    except Exception as e:
        logger.error(f"Brand search failed: {e}")
        # Return empty list on error rather than crashing
        return []
