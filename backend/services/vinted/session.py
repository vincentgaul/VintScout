"""
HTTP session management for Vinted API.

Handles cookie acquisition, headers, and low-level HTTP requests.
"""

import httpx
import time
import logging
from typing import Dict, Optional, Any

from ...config import settings
from .types import VintedAPIError, VintedRateLimitError


logger = logging.getLogger(__name__)


class VintedSession:
    """
    Manages HTTP session and communication with Vinted API.

    Handles:
    - Country-specific domain configuration
    - Browser-like headers to avoid detection
    - Cookie initialization
    - Retry logic and rate limiting
    """

    def __init__(self, country_code: str, base_url: str):
        """
        Initialize HTTP session for Vinted API.

        Args:
            country_code: 2-letter country code (e.g., "fr", "de")
            base_url: Vinted domain URL (e.g., "https://www.vinted.fr")
        """
        self.country_code = country_code
        self.base_url = base_url
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

    def make_request(
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

    def close(self):
        """Close HTTP session."""
        self.session.close()
