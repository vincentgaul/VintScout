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

    def get_category_tree(self, country_code: str):
        """
        Get the category tree.
        
        Now uses the global static category tree imported from SQL.
        Country code is ignored as categories are standardized.
        """
        return Category.get_root_categories(self.db, country_code)

    def search_categories(self, query: str, country_code: str, limit: int = 20):
        """
        Search categories by name.
        """
        return Category.search_by_name(self.db, query, country_code, limit)
