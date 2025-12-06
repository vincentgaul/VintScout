"""
API Routes Package

Exports all API routers for registration in main.py.

Each route module handles a specific resource:
- auth: User authentication (register, login)
- alerts: Alert CRUD operations
- brands: Brand search/autocomplete
- categories: Category tree navigation
- history: Item history viewing
- sizes: Size options for categories
"""

from backend.api.routes.auth import router as auth_router
from backend.api.routes.alerts import router as alerts_router
from backend.api.routes.brands import router as brands_router
from backend.api.routes.categories import router as categories_router
from backend.api.routes.history import router as history_router
from backend.api.routes.sizes import router as sizes_router

__all__ = [
    "auth_router",
    "alerts_router",
    "brands_router",
    "categories_router",
    "history_router",
    "sizes_router"
]
