"""
Brand API Routes

Brand search using Vinted's /api/v2/brands endpoint with keyword parameter.
Provides partial/fuzzy matching for brand autocomplete.

Endpoints:
- GET /api/brands/search - Search brands by keyword (e.g., "nike" → "Nike")
- GET /api/brands/popular - Returns empty (not implemented yet)

Authentication: Optional (works for both authenticated and anonymous users)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db
from backend.schemas import BrandResponse
from backend.models import Brand
from backend.services.brand_service import BrandService


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
                name=brand.name,
                is_popular=brand.is_popular
            )
            for brand in brands
        ]

    except Exception as e:
        logger.error(f"Brand search failed: {e}")
        # Return empty list on error rather than crashing
        return []


@router.get("/popular", response_model=List[BrandResponse])
def get_popular_brands(
    country_code: str = Query(..., min_length=2, max_length=2, description="Country code"),
    limit: int = Query(default=100, ge=1, le=200, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Get popular brands for a country (CURRENTLY EMPTY - MVP Phase 1).

    **IMPORTANT**: No brands are seeded in Phase 1 MVP.
    This endpoint always returns an empty array.

    **Workaround**: Use text search instead!
    Type the brand name directly in your alert search text field.

    TODO Phase 2: Manually curate top 100-200 brands with their IDs,
                  seed database, then this will return actual popular brands.

    Query parameters:
        - country_code: 2-letter country code (e.g., "fr")
        - limit: Maximum results to return (default: 100, max: 200)

    Response:
        Empty array (no brands seeded yet)

    Example:
        GET /api/brands/popular?country_code=fr&limit=50
        Returns: []
    """
    # TODO: Phase 1 MVP - No brands seeded, always return empty without querying
    # Database table may not exist yet, so don't query to avoid crashes
    # Phase 2: After seeding brands, re-enable the query below

    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        f"Popular brands requested for {country_code}, "
        f"but no brands are seeded. Returning empty list."
    )

    # Always return empty for Phase 1 MVP
    return []

    # TODO: Phase 2 - Uncomment this when brands are seeded:
    # brands = db.query(Brand)\
    #     .filter(
    #         Brand.country_code == country_code.lower(),
    #         Brand.is_popular == True
    #     )\
    #     .order_by(Brand.item_count.desc())\
    #     .limit(limit)\
    #     .all()
    # return [BrandResponse.model_validate(brand) for brand in brands]
