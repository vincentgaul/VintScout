"""
Vinted API Client

HTTP client for interacting with Vinted's undocumented API.
This client mimics browser requests to avoid detection.

Key features:
- Automatic country-specific domain selection (vinted.fr, vinted.de, etc.)
- Proper headers to mimic browser requests
- Rate limiting and retry logic
- Response parsing and error handling

Vinted API endpoints (undocumented):
- GET /api/v2/catalog/brands - Search brands
- GET /api/v2/catalogs - Get category tree
- GET /api/v2/catalog/items - Search items

Note: Vinted's API is not officially documented. These endpoints are reverse-engineered
from browser requests and may change without notice.

Architecture:
This module now delegates to specialized submodules:
- vinted.types: Constants and exceptions
- vinted.session: HTTP session management
- vinted.search: Search operations (brands, categories, items)
"""

from typing import Dict, List, Optional, Any

from .vinted import DOMAINS, VintedAPIError, VintedRateLimitError, VintedSession
from .vinted import search as vinted_search


# Re-export exceptions for backward compatibility
__all__ = ["VintedClient", "VintedAPIError", "VintedRateLimitError"]


class VintedClient:
    """
    HTTP client for Vinted API.

    Handles country-specific domains, proper headers, and error handling.
    This is now a lightweight facade that delegates to specialized modules.
    """

    # Re-export DOMAINS for backward compatibility
    DOMAINS = DOMAINS

    def __init__(self, country_code: str = "fr"):
        """
        Initialize Vinted API client.

        Args:
            country_code: 2-letter country code (e.g., "fr", "de")

        Raises:
            ValueError: If country code is not supported
        """
        self.country_code = country_code.lower()
        if self.country_code not in DOMAINS:
            raise ValueError(f"Unsupported country code: {country_code}")

        self.base_url = DOMAINS[self.country_code]
        self._session = VintedSession(self.country_code, self.base_url)

    def search_brands(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for brands by name.

        Uses Vinted's brand search endpoint with keyword parameter.
        This endpoint provides partial matching - searching "nike" will match "Nike", etc.

        Args:
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
            client = VintedClient("fr")
            brands = client.search_brands("nike")
            # [{"id": 53, "title": "Nike", "slug": "nike", ...}]
        """
        return vinted_search.search_brands(self._session, query, limit)

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get complete category tree for this country.

        Returns:
            List of root category dictionaries with keys:
                - id: Vinted's category ID (string)
                - title: Category name
                - item_count: Number of items
                - children: List of subcategories (nested structure)

        Example:
            client = VintedClient("fr")
            categories = client.get_categories()
            # [{"id": "1", "title": "Women", "children": [...]}, ...]
        """
        return vinted_search.get_categories(self._session)

    def search_items(
        self,
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
            client = VintedClient("fr")
            results = client.search_items(
                search_text="sneakers",
                brand_ids=["53"],  # Nike
                price_from=20,
                price_to=100
            )
            # {"items": [...], "pagination": {...}}
        """
        return vinted_search.search_items(
            self._session,
            search_text=search_text,
            brand_ids=brand_ids,
            catalog_ids=catalog_ids,
            size_ids=size_ids,
            price_from=price_from,
            price_to=price_to,
            condition_ids=condition_ids,
            currency=currency,
            order=order,
            per_page=per_page,
            page=page
        )

    def close(self):
        """Close HTTP session."""
        self._session.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()
