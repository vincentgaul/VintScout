"""
Vinted search operations.

Contains search methods for brands, categories, and items.
"""

import logging
from typing import Dict, List, Optional, Any

from .types import VintedAPIError
from .session import VintedSession


logger = logging.getLogger(__name__)


def search_brands(session: VintedSession, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for brands by name.

    Uses Vinted's brand search endpoint with keyword parameter.
    This endpoint provides partial matching - searching "nike" will match "Nike", etc.

    Args:
        session: Vinted HTTP session
        query: Brand name to search (e.g., "nike", "thursday")
        limit: Maximum results to return (default: 20)

    Returns:
        List of brand dictionaries with keys:
            - id: Brand ID (integer)
            - title: Brand name (string)
            - slug: URL-friendly brand name
            - path: Brand page URL path
            - item_count: Number of items for this brand
            - favourite_count: Number of users who favorited this brand

    Example:
        session = VintedSession("fr", "https://www.vinted.fr")
        brands = search_brands(session, "nike")
        # [{"id": 53, "title": "Nike", "slug": "nike", ...}]
    """
    try:
        # Use the /api/v2/brands endpoint with keyword parameter
        response = session.make_request(
            "GET",
            "/api/v2/brands",
            params={"keyword": query}
        )

        # Extract brands from response
        brands = response.get("brands", [])

        logger.info(f"Found {len(brands)} brands for query '{query}'")

        # Limit results
        return brands[:limit]

    except VintedAPIError as e:
        logger.error(f"Brand search failed for '{query}': {e}")
        # Return empty list on error rather than crashing
        return []
    except Exception as e:
        logger.error(f"Unexpected error in brand search: {e}")
        return []


def _normalize_category(category: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize category response by renaming 'catalogs' to 'children'.

    Vinted API uses 'catalogs' for nested categories, but we use 'children'
    for consistency with our data model.
    """
    # Make a copy to avoid mutating the original
    normalized = category.copy()

    # Rename 'catalogs' to 'children'
    if "catalogs" in normalized:
        children = normalized.pop("catalogs")
        # Recursively normalize children
        normalized["children"] = [_normalize_category(child) for child in children]

    return normalized


def get_categories(session: VintedSession) -> List[Dict[str, Any]]:
    """
    Get complete category tree for this country.

    Args:
        session: Vinted HTTP session

    Returns:
        List of root category dictionaries with keys:
            - id: Vinted's category ID (string)
            - title: Category name
            - item_count: Number of items
            - children: List of subcategories (nested structure)

    Example:
        session = VintedSession("fr", "https://www.vinted.fr")
        categories = get_categories(session)
        # [{"id": "1", "title": "Women", "children": [...]}, ...]
    """
    response = session.make_request("GET", "/api/v2/catalogs")

    catalogs = response.get("catalogs", [])
    logger.info(f"Fetched {len(catalogs)} root categories")

    # Normalize catalogs to use 'children' instead of 'catalogs'
    return [_normalize_category(cat) for cat in catalogs]


def search_items(
    session: VintedSession,
    search_text: Optional[str] = None,
    brand_ids: Optional[List[str]] = None,
    catalog_ids: Optional[List[str]] = None,
    size_ids: Optional[List[str]] = None,
    price_from: Optional[float] = None,
    price_to: Optional[float] = None,
    condition_ids: Optional[List[str]] = None,
    currency: str = "EUR",
    order: str = "newest_first",
    per_page: int = 20,
    page: int = 1
) -> Dict[str, Any]:
    """
    Search for items on Vinted.

    Args:
        session: Vinted HTTP session
        search_text: Free-text search query
        brand_ids: List of brand IDs to filter
        catalog_ids: List of category IDs to filter
        size_ids: List of size IDs to filter
        price_from: Minimum price
        price_to: Maximum price
        condition_ids: Condition/status IDs
        currency: Currency code (EUR, USD, etc.)
        order: Sort order (newest_first, price_low_to_high, price_high_to_low, relevance)
        per_page: Results per page (max 96)
        page: Page number (1-indexed)

    Returns:
        Dictionary with keys:
            - items: List of item dictionaries
            - pagination: Pagination info (total_entries, current_page, total_pages)

    Example:
        session = VintedSession("fr", "https://www.vinted.fr")
        results = search_items(
            session,
            search_text="sneakers",
            brand_ids=["53"],  # Nike
            price_from=20,
            price_to=100
        )
        # {"items": [...], "pagination": {...}}
    """
    params = {
        "per_page": min(per_page, 96),  # Vinted max is 96
        "page": page,
        "order": order,
        "currency": currency
    }

    if search_text:
        params["search_text"] = search_text

    if brand_ids:
        params["brand_ids[]"] = brand_ids

    if catalog_ids:
        params["catalog_ids[]"] = catalog_ids

    if size_ids:
        params["size_ids[]"] = size_ids

    if price_from is not None:
        params["price_from"] = price_from

    if price_to is not None:
        params["price_to"] = price_to

    if condition_ids:
        params["status_ids[]"] = condition_ids

    response = session.make_request("GET", "/api/v2/catalog/items", params=params)

    items = response.get("items", [])
    pagination = response.get("pagination", {})

    logger.info(
        f"Found {pagination.get('total_entries', 0)} items "
        f"(page {page}, showing {len(items)})"
    )

    return {
        "items": items,
        "pagination": pagination
    }
