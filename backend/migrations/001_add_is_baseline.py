"""
Add is_baseline column to item_history table

This migration adds the is_baseline boolean column to track
items that are part of the initial baseline establishment.

Run this manually:
    python backend/migrations/001_add_is_baseline.py
"""

from sqlalchemy import create_engine, text
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add is_baseline column to item_history table."""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            # Add is_baseline column with default value False
            logger.info("Adding is_baseline column to item_history table...")
            conn.execute(text(
                "ALTER TABLE item_history "
                "ADD COLUMN is_baseline BOOLEAN NOT NULL DEFAULT 0"
            ))
            conn.commit()
            logger.info("✓ Successfully added is_baseline column")

        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                logger.info("✓ Column is_baseline already exists, skipping")
            else:
                logger.error(f"✗ Migration failed: {e}")
                raise

    logger.info("Migration complete!")


if __name__ == "__main__":
    migrate()
