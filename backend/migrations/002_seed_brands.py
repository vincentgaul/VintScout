"""
Seed brands table from brands.sql

Imports brand IDs and names from the pre-scraped brands.sql file.
Brand IDs are universal across all Vinted countries.
"""

import re
import sqlite3
from pathlib import Path

def migrate():
    """Import brands from brands.sql into SQLite database."""

    # Paths
    script_dir = Path(__file__).parent
    brands_sql = script_dir.parent.parent / "brands.sql"
    db_path = script_dir.parent / "data" / "vinted.db"

    print(f"Reading brands from: {brands_sql}")
    print(f"Database: {db_path}")

    if not brands_sql.exists():
        print(f"ERROR: {brands_sql} not found")
        return

    # Read and parse brands.sql
    with open(brands_sql, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all brand entries: (id , 'title' , 'url')
    pattern = r"\((\d+)\s*,\s*'([^']+)'\s*,\s*'[^']+'\)"
    matches = re.findall(pattern, content)

    print(f"Found {len(matches)} brands to import")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create brands table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                vinted_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand_name ON brands(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_brand_vinted_id ON brands(vinted_id)")

        # Clear existing brands
        cursor.execute("DELETE FROM brands")
        print("Cleared existing brands")

        # Import brands (brand IDs are universal across all countries)
        import_count = 0
        for vinted_id, name in matches:
            # Generate UUID for primary key
            import uuid
            brand_id = str(uuid.uuid4())

            from datetime import datetime
            now = datetime.utcnow().isoformat()

            cursor.execute("""
                INSERT INTO brands (id, vinted_id, name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (brand_id, vinted_id, name, now, now))

            import_count += 1

            if import_count % 1000 == 0:
                print(f"Imported {import_count} brands...")

        conn.commit()
        print(f"✓ Successfully imported {import_count} brands")

        # Show stats
        cursor.execute("SELECT COUNT(*) FROM brands")
        total = cursor.fetchone()[0]
        print(f"Total brands: {total}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
