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
"""

import httpx
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import logging

from backend.config import settings


logger = logging.getLogger(__name__)


class VintedAPIError(Exception):
    """Raised when Vinted API returns an error."""
    pass


class VintedRateLimitError(Exception):
    """Raised when rate limited by Vinted."""
    pass


class VintedClient:
    """
    HTTP client for Vinted API.

    Handles country-specific domains, proper headers, and error handling.
    """

    # Country code to domain mapping
    DOMAINS = {
        "fr": "https://www.vinted.fr",
        "de": "https://www.vinted.de",
        "uk": "https://www.vinted.co.uk",
        "pl": "https://www.vinted.pl",
        "es": "https://www.vinted.es",
        "it": "https://www.vinted.it",
        "be": "https://www.vinted.be",
        "nl": "https://www.vinted.nl",
        "at": "https://www.vinted.at",
        "cz": "https://www.vinted.cz",
        "lt": "https://www.vinted.lt",
        "lu": "https://www.vinted.lu",
        "pt": "https://www.vinted.pt",
        "se": "https://www.vinted.se",
        "us": "https://www.vinted.com",
        "ro": "https://www.vinted.ro",
        "gr": "https://www.vinted.gr",
        "hr": "https://www.vinted.hr",
        "hu": "https://www.vinted.hu",
        "sk": "https://www.vinted.sk",
        "si": "https://www.vinted.si",
        "fi": "https://www.vinted.fi",
        "dk": "https://www.vinted.dk",
        "ee": "https://www.vinted.ee",
        "lv": "https://www.vinted.lv",
        "ie": "https://www.vinted.ie"
    }

    def __init__(self, country_code: str = "fr"):
        """
        Initialize Vinted API client.

        Args:
            country_code: 2-letter country code (e.g., "fr", "de")

        Raises:
            ValueError: If country code is not supported
        """
        self.country_code = country_code.lower()
        if self.country_code not in self.DOMAINS:
            raise ValueError(f"Unsupported country code: {country_code}")

        self.base_url = self.DOMAINS[self.country_code]
        self.session = httpx.Client(
            timeout=settings.VINTED_API_TIMEOUT,
            headers=self._get_headers(),
            follow_redirects=True
        )

        # Initialize session with cookies (required by Vinted)
        self._initialize_session()

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers that mimic a real browser.

        Vinted may block requests without proper headers.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"{self.base_url}/",
            "Origin": self.base_url,
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

    def _initialize_session(self):
        """
        Initialize session with Vinted to get required cookies.

        Vinted requires a valid session with cookies before API calls work.
        This mimics the original VintedScanner behavior.
        """
        try:
            logger.debug(f"Initializing session with {self.base_url}")

            # Make initial request to homepage to get cookies
            response = self.session.get(self.base_url)

            if response.status_code == 200:
                logger.debug(f"Session initialized, cookies: {len(self.session.cookies)}")
            else:
                logger.warning(f"Session init returned {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            # Don't raise - we'll try to continue anyway

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Vinted API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., "/api/v2/catalog/brands")
            params: Query parameters
            retries: Number of retries on failure

        Returns:
            Parsed JSON response

        Raises:
            VintedAPIError: If API returns error
            VintedRateLimitError: If rate limited
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries):
            try:
                logger.debug(f"Request: {method} {url} params={params}")

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited by Vinted. Retry after {retry_after}s")
                    if attempt < retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise VintedRateLimitError(f"Rate limited. Retry after {retry_after}s")

                # Handle errors
                if response.status_code >= 400:
                    logger.error(f"Vinted API error: {response.status_code} {response.text}")
                    raise VintedAPIError(f"HTTP {response.status_code}: {response.text}")

                # Parse JSON
                data = response.json()
                logger.debug(f"Response: {response.status_code} (keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'})")

                return data

            except httpx.TimeoutException:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise VintedAPIError("Request timed out")

            except httpx.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise VintedAPIError(f"HTTP error: {e}")

        raise VintedAPIError("Max retries exceeded")

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
        try:
            # Use the /api/v2/brands endpoint with keyword parameter
            response = self._make_request(
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

    def _normalize_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
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
            normalized["children"] = [self._normalize_category(child) for child in children]

        return normalized

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
        response = self._make_request("GET", "/api/v2/catalogs")

        catalogs = response.get("catalogs", [])
        logger.info(f"Fetched {len(catalogs)} root categories")

        # Normalize catalogs to use 'children' instead of 'catalogs'
        return [self._normalize_category(cat) for cat in catalogs]

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

        response = self._make_request("GET", "/api/v2/catalog/items", params=params)

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

    def close(self):
        """Close HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()
