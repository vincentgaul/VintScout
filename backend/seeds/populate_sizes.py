"""
Populate Sizes Table

Loads size data from vinted_sizes.json and populates the database.
Clears existing data first.

Run with: uv run python -m backend.seeds.populate_sizes
"""

import json
from pathlib import Path
from sqlalchemy.orm import Session

from backend.database import engine, SessionLocal
from backend.models import Size


def translate_size_name(french_name: str) -> str:
    """
    Translate French size names to English.
    (Same function as in sizes.py API route)
    """
    translations = [
        (' mois', ' months'),
        (' ans', ' years'),
        ('et +', 'and up'),
        ('jusqu\'à', 'up to'),
        ('Jusqu\'à', 'Up to'),
        ('Taille unique', 'One size'),
        ('Autre', 'Other'),
        ('Prématuré', 'Premature'),
        ('Nouveau né', 'Newborn'),
        ('Peu importe', 'Any'),
        ('Ajustable', 'Adjustable'),
        ('Universel', 'Universal'),
        ('Simple', 'Single'),
    ]

    translated = french_name
    for french, english in translations:
        translated = translated.replace(french, english)

    return translated


def populate_sizes():
    """Load sizes from JSON and populate database."""

    # Load JSON data
    json_path = Path(__file__).parent.parent / "data" / "vinted_sizes.json"

    print(f"Loading size data from: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        size_data = json.load(f)

    db: Session = SessionLocal()

    try:
        # Clear existing sizes
        print("Clearing existing sizes...")
        deleted_count = db.query(Size).delete()
        print(f"Deleted {deleted_count} existing sizes")

        # Populate from JSON
        total_added = 0

        for category in size_data:
            category_id = category.get('id')
            sizes = category.get('sizes', [])

            if not sizes:
                continue

            print(f"\nCategory {category_id}: {category.get('description')} - {len(sizes)} sizes")

            for size in sizes:
                # Translate French to English
                translated_title = translate_size_name(size['title'])

                # Create Size entry
                size_entry = Size(
                    id=size['id'],
                    title=translated_title,
                    category_id=category_id
                )

                db.add(size_entry)
                total_added += 1

        # Commit all changes
        db.commit()
        print(f"\n✓ Successfully added {total_added} sizes to database")

        # Verify
        count = db.query(Size).count()
        print(f"✓ Total sizes in database: {count}")

        # Show sample for verification
        print("\n=== Sample Sizes ===")
        mens_shoes = db.query(Size).filter(Size.category_id == 38).limit(5).all()
        print("Men's shoes (category 38):")
        for size in mens_shoes:
            print(f"  ID: {size.id:<5} Name: {size.title}")

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_sizes()
