"""
Configuration Management Using Environment Variables

This file reads settings from the .env file (or environment variables).
It's like a central control panel for the entire application.

Instead of hardcoding values like database passwords or API keys,
we store them in a .env file and read them here. This keeps secrets
safe and makes it easy to use different settings for development vs production.

The Settings class defines all available configuration options with:
- Default values (used if not set in .env)
- Type hints (str, int, bool) so Python knows what to expect
- Organized by category (Database, Authentication, Notifications, etc.)

Example: If your .env has "JWT_SECRET=abc123", this file reads it
and makes it available as settings.JWT_SECRET throughout the app.
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    APP_NAME: str = "VintedScanner Web"
    DEPLOYMENT_MODE: str = "self-hosted"  # or "cloud"
    DEBUG: bool = False

    # Database
    # Use absolute path to ensure we always find the DB, regardless of where the app is started
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL: str = f"sqlite:///{os.path.join(_BASE_DIR, 'data', 'vinted.db')}"

    # Authentication
    REQUIRE_AUTH: bool = False  # Set to True for cloud mode, False for self-hosted
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Telegram Notifications (Optional)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Brand/Category Cache
    BRAND_CACHE_TTL_DAYS: int = 30
    SEED_POPULAR_BRANDS_ON_STARTUP: bool = True
    VINTED_API_TIMEOUT: int = 30
    MAX_BRAND_SEARCH_RESULTS: int = 50
    CATEGORY_CACHE_REFRESH_DAYS: int = 7

    # Scanner Settings
    MIN_CHECK_INTERVAL_MINUTES: int = 5
    MAX_CHECK_INTERVAL_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Create settings instance
settings = Settings()
