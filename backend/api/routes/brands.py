"""
Brand API Routes (CURRENTLY DISABLED - MVP Phase 1)

TODO: Brand search is NOT WORKING in Phase 1 MVP due to Vinted API limitations.
      Vinted's /api/v2/catalog/brands endpoint returns 404 (deprecated/removed).

      These endpoints return empty results with helpful error messages.
      Users should use text search instead (e.g., "Nike sneakers").

      Phase 2 TODO: Manually curate 100-200 popular brand IDs and seed database,
                    then re-enable these endpoints with hardcoded brand list.

Endpoints:
- GET /api/brands/search - Returns empty (brand API unavailable)
- GET /api/brands/popular - Returns empty (no brands seeded)

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
    country_code: str = Query(..., min_length=2, max_length=2, description="Country code (e.g., 'fr')"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search brands by name (CURRENTLY UNAVAILABLE - MVP Phase 1).

    **IMPORTANT**: Brand search is not available in this version.
    Vinted's brand search API endpoint has been deprecated/removed (returns 404).

    **Workaround**: Use text search instead!
    Instead of searching for brand "Nike" and getting ID "53",
    just type "Nike sneakers" directly in the alert search text field.

    This approach works for 90% of use cases and is simpler for users.

    TODO Phase 2: Manually curate popular brands and seed database.
                  Then this endpoint will return hardcoded brand list.

    Query parameters:
        - q: Search query (e.g., "nike")
        - country_code: 2-letter country code (e.g., "fr")
        - limit: Maximum results to return (default: 20, max: 100)

    Response:
        Empty array (brand search unavailable)

    Example:
        GET /api/brands/search?q=nike&country_code=fr&limit=10
        Returns: []
    """
    # TODO: Phase 1 MVP - Brand search is broken by design (Vinted API deprecated)
    # Always return empty array without querying database or calling API
    # Frontend should detect empty response and show helpful message

    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        f"Brand search requested for '{q}' in {country_code}, "
        f"but brand API is unavailable. Returning empty list."
    )

    return []  # Always empty - brand search not available


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
