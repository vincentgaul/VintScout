"""
Category API Routes (Hierarchical Tree)

Provides category tree and search for alert creation.
Categories form a hierarchical structure (Women > Accessories > Hats).

Endpoints:
- GET /api/categories - Get root categories (with optional tree)
- GET /api/categories/{category_id} - Get single category with children
- GET /api/categories/search - Search categories by name

Authentication: Optional (works for both authenticated and anonymous users)
This allows self-hosted users to browse categories without logging in.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db
from backend.schemas import CategoryResponse
from backend.models import Category
from backend.services.category_service import CategoryService


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_root_categories(
    country_code: str = Query(default="global", description="Country code (ignored for global categories)"),
    include_children: bool = Query(default=True, description="Include child categories in tree"),
    db: Session = Depends(get_db)
):
    """
    Get root-level categories for a country.

    Returns top-level categories (level=0) with optional children.
    Automatically fetches from Vinted if cache is stale (> 7 days).

    Query parameters:
        - country_code: 2-letter country code (e.g., "fr")
        - include_children: Whether to include child categories (default: true)

    Response:
        Array of root category objects with nested children:
        [
            {
                "id": "550e8400-...",
                "vinted_id": "1",
                "name": "Women",
                "level": 0,
                "item_count": 500000,
                "has_children": true,
                "children": [
                    {
                        "id": "660e8400-...",
                        "vinted_id": "2",
                        "name": "Accessories",
                        "level": 1,
                        "item_count": 50000,
                        "has_children": true,
                        "children": [...]
                    }
                ]
            },
            ...
        ]

    Example:
        GET /api/categories?country_code=fr&include_children=true
    """
    # Use CategoryService for intelligent caching
    service = CategoryService(db)
    categories = service.get_category_tree(country_code.lower())

    # Convert to response schema (uses to_dict method for nested children)
    return [
        CategoryResponse.model_validate(cat.to_dict(include_children=include_children))
        for cat in categories
    ]


@router.get("/search", response_model=List[CategoryResponse])
def search_categories(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    country_code: str = Query(default="global", description="Country code (ignored)"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search categories by name (flat search).

    Searches across all category levels for matching names.
    Ensures cache is fresh before searching.

    Query parameters:
        - q: Search query (e.g., "shoes")
        - country_code: 2-letter country code (e.g., "fr")
        - limit: Maximum results to return (default: 20, max: 100)

    Response:
        Array of category objects (without children):
        [
            {
                "id": "550e8400-...",
                "vinted_id": "1193",
                "name": "Shoes",
                "level": 1,
                "item_count": 50234,
                "has_children": true,
                "children": null
            },
            ...
        ]

    Example:
        GET /api/categories/search?q=shoes&country_code=fr&limit=10
    """
    # Use CategoryService to ensure fresh cache
    service = CategoryService(db)
    categories = service.search_categories(q, country_code.lower(), limit)

    # Convert to response schema (without children for flat search)
    return [
        CategoryResponse.model_validate(cat.to_dict(include_children=False))
        for cat in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: str,
    include_children: bool = Query(default=True, description="Include child categories"),
    db: Session = Depends(get_db)
):
    """
    Get a single category by ID.

    Returns category details with optional children.
    Useful for expanding tree nodes on demand.

    Path parameters:
        - category_id: Category UUID

    Query parameters:
        - include_children: Whether to include child categories (default: true)

    Response:
        Category object with nested children:
        {
            "id": "550e8400-...",
            "vinted_id": "1",
            "name": "Women",
            "level": 0,
            "item_count": 500000,
            "has_children": true,
            "children": [...]
        }

    Raises:
        404 Not Found: If category doesn't exist
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return CategoryResponse.model_validate(
        category.to_dict(include_children=include_children)
    )
