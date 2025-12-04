"""
Popular Brands Seed Script (Phase 2 TODO)

TODO: This script is NOT USED in Phase 1 MVP.
      Brand search API is dead, so we can't populate this dynamically.

      Phase 2 Implementation Plan:
      1. Manually curate top 100-200 brand IDs by inspecting Vinted URLs
      2. Build POPULAR_BRANDS dictionary with {name: vinted_id} pairs
      3. Run this script to seed database
      4. Re-enable brand search endpoints to return seeded data

Usage (Phase 2):
    python -m backend.seeds.popular_brands
"""

from backend.database import SessionLocal
from backend.models import Brand
import logging

logger = logging.getLogger(__name__)


# TODO: Phase 2 - Manually curate these brand IDs by inspecting Vinted search URLs
# Example: Searching "Nike" on vinted.fr shows brand_ids[]=53 in URL
# We need to manually build this list by testing common brands
POPULAR_BRANDS = {
    # Format: "Brand Name": "vinted_id"

    # TODO: Add top sportswear brands (Nike=53, Adidas=14, etc.)
    # "Nike": "53",
    # "Adidas": "14",
    # "Puma": "167",
    # "New Balance": "145",

    # TODO: Add fast fashion (Zara=12, H&M=21, etc.)
    # "Zara": "12",
    # "H&M": "21",
    # "Mango": "98",
    # "Uniqlo": "276",

    # TODO: Add luxury brands (Louis Vuitton=417, etc.)
    # "Louis Vuitton": "417",
    # "Gucci": "89",
    # "Chanel": "67",
    # "Hermès": "104",

    # ... add 100-200 total brands
}


def seed_popular_brands(country_code: str = "fr") -> int:
    """
    Seed popular brands for a country.

    TODO: Phase 2 - This is currently a stub (POPULAR_BRANDS is empty).
          Need to manually curate brand IDs before running.

    Args:
        country_code: 2-letter country code (default: "fr")

    Returns:
        Number of brands seeded
    """
    if not POPULAR_BRANDS:
        logger.warning(
            "POPULAR_BRANDS dictionary is empty. "
            "This script cannot run until brands are manually curated. "
            "See TODO comments in backend/seeds/popular_brands.py"
        )
        return 0

    db = SessionLocal()
    count = 0

    try:
        for name, vinted_id in POPULAR_BRANDS.items():
            # Check if brand already exists
            existing = db.query(Brand).filter(
                Brand.vinted_id == vinted_id,
                Brand.country_code == country_code
            ).first()

            if existing:
                # Update existing brand
                existing.name = name
                existing.is_popular = True
                logger.debug(f"Updated existing brand: {name} ({vinted_id})")
            else:
                # Create new brand
                brand = Brand(
                    vinted_id=vinted_id,
                    name=name,
                    country_code=country_code,
                    is_popular=True,
                    item_count=0  # We don't know item counts without API
                )
                db.add(brand)
                logger.debug(f"Seeded new brand: {name} ({vinted_id})")

            count += 1

        db.commit()
        logger.info(f"Successfully seeded {count} popular brands for {country_code}")
        return count

    except Exception as e:
        logger.error(f"Error seeding brands: {e}", exc_info=True)
        db.rollback()
        return 0

    finally:
        db.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Popular Brands Seed Script (Phase 2 TODO)")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This script is NOT ready to run!")
    print()
    print("TODO before running:")
    print("1. Manually curate 100-200 brand IDs by inspecting Vinted URLs")
    print("2. Update POPULAR_BRANDS dictionary in this file")
    print("3. Run: python -m backend.seeds.popular_brands")
    print()
    print("=" * 60)

    # Attempt to seed (will do nothing if POPULAR_BRANDS is empty)
    result = seed_popular_brands(country_code="fr")

    if result == 0:
        print()
        print("❌ No brands seeded (POPULAR_BRANDS is empty)")
        print("   See instructions above.")
    else:
        print()
        print(f"✅ Successfully seeded {result} brands!")
