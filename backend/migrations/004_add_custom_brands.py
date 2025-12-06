"""
Add custom brands (Seagale, Outlier) to the database.
"""

import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

def migrate():
    # Paths
    script_dir = Path(__file__).parent
    db_path = script_dir.parent / "data" / "vinted.db"

    print(f"Database: {db_path}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    brands_to_add = [
        {"vinted_id": "358956", "name": "Seagale"},
        {"vinted_id": "838445", "name": "Outlier"},
    ]

    try:
        count = 0
        for brand in brands_to_add:
            # Check if exists
            cursor.execute("SELECT id FROM brands WHERE vinted_id = ?", (brand["vinted_id"],))
            existing = cursor.fetchone()

            if existing:
                print(f"Brand {brand['name']} ({brand['vinted_id']}) already exists.")
            else:
                brand_id = str(uuid.uuid4())
                now = datetime.utcnow().isoformat()

                cursor.execute("""
                    INSERT INTO brands (id, vinted_id, name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (brand_id, brand["vinted_id"], brand["name"], now, now))
                
                print(f"Added brand: {brand['name']} ({brand['vinted_id']})")
                count += 1

        conn.commit()
        print(f"Successfully added {count} brands.")

    except Exception as e:
        conn.rollback()
        print(f"Error adding brands: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
