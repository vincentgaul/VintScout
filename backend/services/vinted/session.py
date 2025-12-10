"""
HTTP session management for Vinted API.

Handles cookie acquisition, headers, and low-level HTTP requests.
Uses CloudScraper to bypass Cloudflare protection.
"""

import cloudscraper
import time
import logging
import random
from typing import Dict, Optional, Any

from ...config import settings
from .types import VintedAPIError, VintedRateLimitError


logger = logging.getLogger(__name__)


# Rotate user agents to avoid fingerprinting
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
]


class VintedSession:
    """
    Manages HTTP session and communication with Vinted API.

    Handles:
    - Country-specific domain configuration
    - Browser-like headers to avoid detection
    - Cookie initialization
    - Retry logic and rate limiting
    """

    def __init__(self, country_code: str, base_url: str, skip_init: bool = False):
        """
        Initialize HTTP session for Vinted API with CloudScraper.

        CloudScraper automatically handles Cloudflare challenges.

        Args:
            country_code: 2-letter country code (e.g., "fr", "de")
            base_url: Vinted domain URL (e.g., "https://www.vinted.fr")
            skip_init: Skip homepage cookie initialization (default: False)
                      Set to True if getting 403 errors during session init
        """
        self.country_code = country_code
        self.base_url = base_url

        # Create CloudScraper session that can bypass Cloudflare
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'mobile': False
            }
        )

        # Set timeout
        self.session.timeout = settings.VINTED_API_TIMEOUT

        # Set headers
        self.session.headers.update(self._get_headers())

        # Initialize session with cookies (can be skipped if causing 403s)
        if not skip_init:
            self._initialize_session()
        else:
            logger.info(f"Skipping session initialization for {self.base_url} (trying API directly)")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers that mimic a real browser.

        Vinted may block requests without proper headers.
        Uses rotating user agents to avoid fingerprinting.
        """
        return {
            "User-Agent": random.choice(USER_AGENTS),
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

        If this fails with 403, consider setting VINTED_SKIP_SESSION_INIT=true
        in your .env file.
        """
        try:
            logger.debug(f"Initializing session with {self.base_url}")

            # Make initial request to homepage to get cookies
            response = self.session.get(self.base_url)

            if response.status_code == 200:
                logger.debug(f"Session initialized, cookies: {len(self.session.cookies)}")
            elif response.status_code == 403:
                logger.warning(
                    f"Session init returned 403 (bot detection). "
                    f"Set VINTED_SKIP_SESSION_INIT=true in .env to skip this step."
                )
                # Check if HTML response (CAPTCHA page)
                if "html" in response.text.lower()[:100]:
                    logger.error("Vinted returned HTML/CAPTCHA page instead of allowing session")
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

        CloudScraper will automatically solve Cloudflare challenges.

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
        import requests

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
                    logger.error(f"Vinted API error: {response.status_code} {response.text[:200]}")
                    raise VintedAPIError(f"HTTP {response.status_code}: {response.text[:200]}")

                # Parse JSON
                data = response.json()
                logger.debug(f"Response: {response.status_code} (keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'})")

                return data

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise VintedAPIError("Request timed out")

            except requests.exceptions.RequestException as e:
                logger.error(f"HTTP error: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise VintedAPIError(f"HTTP error: {e}")

        raise VintedAPIError("Max retries exceeded")

    def close(self):
        """Close HTTP session."""
        self.session.close()
