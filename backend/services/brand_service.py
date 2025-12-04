"""
Brand Service (BROKEN BY DESIGN - MVP Phase 1)

TODO: This service is NON-FUNCTIONAL in Phase 1 MVP.
      Vinted's /api/v2/catalog/brands API endpoint is DEAD (returns 404).
      All search methods will return empty results.

      Brand filtering by ID still works in item search, but brand discovery
      is impossible through the API.

      Phase 2 TODO: Manually curate 100-200 popular brand IDs, create seed script,
                    populate database, then re-enable brand search with hardcoded list.

Caching strategy (BROKEN):
1. Check local database cache first
2. If not found, fetch from Vinted API ← ALWAYS RETURNS []
3. Cache the result ← CACHES NOTHING

This service exists for Phase 2 when we'll have seeded brand data.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.models import Brand
from backend.services.vinted_client import VintedClient, VintedAPIError
from backend.config import settings


logger = logging.getLogger(__name__)


class BrandService:
    """
    Service for brand search with intelligent caching.

    Handles database caching, TTL validation, and Vinted API fallback.
    """

    def __init__(self, db: Session):
        """
        Initialize brand service.

        Args:
            db: Database session for caching
        """
        self.db = db

    def search_brands(
        self,
        query: str,
        country_code: str,
        limit: int = 20,
        fetch_from_vinted: bool = True
    ) -> List[Brand]:
        """
        Search for brands by name (with caching).

        Search flow:
        1. Search local database cache
        2. If results found and fresh (within TTL), return them
        3. If no results or stale, fetch from Vinted API
        4. Cache new results and return

        Args:
            query: Brand name search query (e.g., "nike")
            country_code: 2-letter country code (e.g., "fr")
            limit: Maximum results to return
            fetch_from_vinted: If True, fetch from Vinted when cache misses/stale

        Returns:
            List of Brand model objects
        """
        country_code = country_code.lower()

        # Step 1: Search local cache
        cached_brands = Brand.search_query(self.db, query, country_code, limit)

        # Step 2: Check if cache is fresh
        if cached_brands:
            # Check if any brand is stale
            stale_count = sum(1 for b in cached_brands if b.is_stale(settings.BRAND_CACHE_TTL_DAYS))

            if stale_count == 0:
                logger.info(f"Cache HIT for '{query}' in {country_code} ({len(cached_brands)} brands)")
                return cached_brands

            logger.info(f"Cache STALE for '{query}' in {country_code} ({stale_count}/{len(cached_brands)} stale)")

        else:
            logger.info(f"Cache MISS for '{query}' in {country_code}")

        # Step 3: Fetch from Vinted API if enabled
        # TODO: Phase 1 MVP - Brand API is DEAD, always skip Vinted fetch
        # Vinted's /api/v2/catalog/brands returns 404 (deprecated/removed)
        # Even if we tried to fetch, VintedClient.search_brands() returns []
        if not fetch_from_vinted or True:  # Force disable API (always True)
            logger.warning(
                f"Skipping Vinted brand API (deprecated). "
                f"Returning cached results only: {len(cached_brands)} brands"
            )
            return cached_brands if cached_brands else []

        # This code is unreachable but kept for Phase 2 when we have seeded data
        try:
            with VintedClient(country_code) as client:
                vinted_brands = client.search_brands(query, limit=limit)

            logger.info(f"Fetched {len(vinted_brands)} brands from Vinted API")

            # Step 4: Cache results
            cached = self._cache_brands(vinted_brands, country_code)

            return cached

        except VintedAPIError as e:
            logger.error(f"Vinted API error: {e}")
            # Fall back to stale cache if available
            if cached_brands:
                logger.warning("Falling back to stale cache due to API error")
                return cached_brands
            raise

    def get_or_create_brand(
        self,
        vinted_id: str,
        country_code: str,
        name: Optional[str] = None
    ) -> Brand:
        """
        Get brand from cache or create it by fetching from Vinted.

        Args:
            vinted_id: Vinted's brand ID
            country_code: 2-letter country code
            name: Brand name (optional, used if creating)

        Returns:
            Brand model object

        Raises:
            VintedAPIError: If brand not in cache and API fetch fails
        """
        country_code = country_code.lower()

        # Check cache first
        brand = self.db.query(Brand).filter(
            Brand.vinted_id == vinted_id,
            Brand.country_code == country_code
        ).first()

        if brand:
            # Check if stale
            if not brand.is_stale(settings.BRAND_CACHE_TTL_DAYS):
                logger.debug(f"Brand {vinted_id} found in cache (fresh)")
                return brand
            logger.debug(f"Brand {vinted_id} found in cache (stale)")

        # Need to fetch from Vinted
        # If we have a name, search by name to update cache
        if name:
            brands = self.search_brands(name, country_code, limit=50)
            # Find matching brand
            for b in brands:
                if b.vinted_id == vinted_id:
                    return b

        # Brand not found even after search
        if brand:
            # Return stale brand rather than fail
            logger.warning(f"Could not refresh brand {vinted_id}, returning stale data")
            return brand

        raise VintedAPIError(f"Brand {vinted_id} not found")

    def _cache_brands(
        self,
        vinted_brands: List[dict],
        country_code: str,
        is_popular: bool = False
    ) -> List[Brand]:
        """
        Cache brands from Vinted API response.

        Updates existing brands or creates new ones.

        Args:
            vinted_brands: List of brand dicts from Vinted API
            country_code: 2-letter country code
            is_popular: Whether to mark as popular brand

        Returns:
            List of Brand model objects (cached)
        """
        cached_brands = []

        for vinted_brand in vinted_brands:
            vinted_id = str(vinted_brand.get("id"))
            name = vinted_brand.get("title")
            item_count = vinted_brand.get("item_count")

            # Check if brand already exists
            brand = self.db.query(Brand).filter(
                Brand.vinted_id == vinted_id,
                Brand.country_code == country_code
            ).first()

            if brand:
                # Update existing brand
                brand.name = name
                brand.item_count = item_count
                if is_popular:
                    brand.is_popular = True
                logger.debug(f"Updated brand: {name} ({vinted_id})")
            else:
                # Create new brand
                brand = Brand(
                    vinted_id=vinted_id,
                    name=name,
                    country_code=country_code,
                    item_count=item_count,
                    is_popular=is_popular
                )
                self.db.add(brand)
                logger.debug(f"Cached new brand: {name} ({vinted_id})")

            cached_brands.append(brand)

        # Commit all changes
        self.db.commit()

        # Refresh to get updated timestamps
        for brand in cached_brands:
            self.db.refresh(brand)

        logger.info(f"Cached {len(cached_brands)} brands for {country_code}")

        return cached_brands

    def seed_popular_brands(
        self,
        country_code: str,
        brand_queries: List[str]
    ) -> int:
        """
        Seed popular brands for a country.

        Fetches brands by common queries and marks them as popular.
        This pre-populates the cache for better UX.

        Args:
            country_code: 2-letter country code
            brand_queries: List of search queries (e.g., ["nike", "adidas", "zara"])

        Returns:
            Total number of brands seeded
        """
        total_seeded = 0

        for query in brand_queries:
            try:
                logger.info(f"Seeding brands for query: {query}")

                with VintedClient(country_code) as client:
                    vinted_brands = client.search_brands(query, limit=50)

                # Cache with is_popular=True
                brands = self._cache_brands(vinted_brands, country_code, is_popular=True)
                total_seeded += len(brands)

            except VintedAPIError as e:
                logger.error(f"Failed to seed brands for '{query}': {e}")
                continue

        logger.info(f"Seeded {total_seeded} popular brands for {country_code}")
        return total_seeded
