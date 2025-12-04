"""
Category Service (Tree Caching)

Manages hierarchical category data with caching.

Categories form a tree structure that rarely changes, so we cache
the entire tree per country and refresh periodically (weekly).

Caching strategy:
1. Check if we have any categories for this country
2. Check if the newest category is stale (> 7 days old)
3. If missing or stale, fetch entire tree from Vinted
4. Cache the tree for future lookups
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from backend.models import Category
from backend.services.vinted_client import VintedClient, VintedAPIError
from backend.config import settings


logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service for category management with tree caching.

    Handles fetching, parsing, and caching hierarchical category trees.
    """

    def __init__(self, db: Session):
        """
        Initialize category service.

        Args:
            db: Database session for caching
        """
        self.db = db

    def get_category_tree(
        self,
        country_code: str,
        force_refresh: bool = False
    ) -> List[Category]:
        """
        Get root categories for a country (with caching).

        Args:
            country_code: 2-letter country code
            force_refresh: If True, bypass cache and fetch from Vinted

        Returns:
            List of root Category objects with children loaded
        """
        country_code = country_code.lower()

        # Check if cache needs refresh
        needs_refresh = force_refresh or self._needs_refresh(country_code)

        if needs_refresh:
            logger.info(f"Refreshing category tree for {country_code}")
            self._refresh_categories(country_code)
        else:
            logger.info(f"Using cached category tree for {country_code}")

        # Return root categories from database
        return Category.get_root_categories(self.db, country_code)

    def _needs_refresh(self, country_code: str) -> bool:
        """
        Check if category cache needs refresh.

        Cache is stale if:
        - No categories exist for this country
        - Newest category is older than CATEGORY_CACHE_REFRESH_DAYS

        Args:
            country_code: 2-letter country code

        Returns:
            True if cache needs refresh
        """
        # Check if any categories exist
        count = self.db.query(Category).filter(
            Category.country_code == country_code
        ).count()

        if count == 0:
            logger.debug(f"No categories found for {country_code}")
            return True

        # Check if newest category is stale
        newest = self.db.query(Category).filter(
            Category.country_code == country_code
        ).order_by(Category.updated_at.desc()).first()

        if not newest:
            return True

        age = datetime.utcnow() - newest.updated_at
        stale_threshold = timedelta(days=settings.CATEGORY_CACHE_REFRESH_DAYS)

        is_stale = age > stale_threshold
        logger.debug(f"Category cache age: {age.days} days (stale: {is_stale})")

        return is_stale

    def _refresh_categories(self, country_code: str):
        """
        Fetch and cache category tree from Vinted.

        Completely replaces existing categories for this country.

        Args:
            country_code: 2-letter country code

        Raises:
            VintedAPIError: If fetch fails
        """
        try:
            # Fetch category tree from Vinted
            with VintedClient(country_code) as client:
                vinted_categories = client.get_categories()

            logger.info(f"Fetched {len(vinted_categories)} root categories from Vinted")

            # Delete existing categories for this country
            deleted = self.db.query(Category).filter(
                Category.country_code == country_code
            ).delete()
            logger.info(f"Deleted {deleted} old categories for {country_code}")

            # Cache new categories
            self._cache_category_tree(vinted_categories, country_code)

            self.db.commit()
            logger.info(f"Successfully refreshed category tree for {country_code}")

        except VintedAPIError as e:
            self.db.rollback()
            logger.error(f"Failed to refresh categories: {e}")
            raise

    def _cache_category_tree(
        self,
        vinted_categories: List[Dict[str, Any]],
        country_code: str,
        parent_id: Optional[str] = None,
        level: int = 0,
        parent_path: str = ""
    ):
        """
        Recursively cache category tree.

        Args:
            vinted_categories: List of category dicts from Vinted
            country_code: 2-letter country code
            parent_id: Parent category UUID (None for root)
            level: Tree depth (0 = root)
            parent_path: Parent path for building full paths
        """
        for vinted_cat in vinted_categories:
            vinted_id = str(vinted_cat.get("id"))
            name = vinted_cat.get("title", "Unknown")
            item_count = vinted_cat.get("item_count")

            # Build full path
            path = f"{parent_path}/{name}" if parent_path else f"/{name}"

            # Create category
            category = Category(
                vinted_id=vinted_id,
                name=name,
                country_code=country_code,
                parent_id=parent_id,
                level=level,
                path=path,
                item_count=item_count
            )

            self.db.add(category)
            self.db.flush()  # Get ID for children

            logger.debug(f"Cached category: {path} (level {level})")

            # Recursively cache children
            children = vinted_cat.get("children", [])
            if children:
                self._cache_category_tree(
                    children,
                    country_code,
                    parent_id=category.id,
                    level=level + 1,
                    parent_path=path
                )

    def search_categories(
        self,
        query: str,
        country_code: str,
        limit: int = 20
    ) -> List[Category]:
        """
        Search categories by name (flat search).

        Ensures cache is fresh before searching.

        Args:
            query: Search string
            country_code: 2-letter country code
            limit: Maximum results

        Returns:
            List of matching Category objects
        """
        country_code = country_code.lower()

        # Ensure cache is fresh
        if self._needs_refresh(country_code):
            logger.info(f"Cache stale, refreshing before search")
            self._refresh_categories(country_code)

        # Search in database
        return Category.search_by_name(self.db, query, country_code, limit)
