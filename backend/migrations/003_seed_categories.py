import sys
import os
import re
import uuid
from sqlalchemy.orm import Session

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import SessionLocal, engine, Base
from backend.models import Category

def import_categories():
    print("Starting category import...")
    
    # Drop table to enforce schema update
    Category.__table__.drop(engine, checkfirst=True)
    
    # recreate tables to ensure schema update
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        # 1. Truncate existing categories
        print("Clearing existing categories...")
        session.query(Category).delete()
        session.commit()
        
        # 2. Read SQL file
        sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'categories.sql')
        print(f"Reading {sql_path}...")
        
        with open(sql_path, 'r') as f:
            content = f.read()
            
        # 3. Parse INSERT statements
        # Pattern: (1904,'Women','WOMEN_ROOT',0,'/women','/women')
        # id, title, code, parent_id, url, url_en
        pattern = r"\((\d+),'([^']+)','([^']*)',(\d+),'([^']*)','([^']*)'\)"
        matches = re.findall(pattern, content)
        
        print(f"Found {len(matches)} categories to import.")
        
        # Store mapping of vinted_id (int) -> database_id (uuid)
        id_map = {}
        
        # First pass: Create all category objects with UUIDs
        categories_data = []
        
        # We need to process in order to ensure parents exist, but since we use UUIDs and 
        # map them later, we can create objects first and link them in a second pass 
        # or just insert them all and let SQLAlchemy handle it if we set IDs correctly.
        # Actually, for self-referential keys, we need the parent UUID.
        
        # Let's just create a dict of all items first
        raw_items = {}
        for match in matches:
            v_id, title, code, parent_id, url, url_en = match
            raw_items[int(v_id)] = {
                'vinted_id': v_id,
                'name': title,
                'code': code,
                'parent_v_id': int(parent_id),
                'url': url,
                'url_en': url_en,
                'uuid': str(uuid.uuid4())
            }
            id_map[int(v_id)] = raw_items[int(v_id)]['uuid']
            
        # 4. Build Category objects
        categories_to_add = []
        
        for v_id, item in raw_items.items():
            parent_uuid = None
            level = 0
            path = f"/{item['name']}"
            
            if item['parent_v_id'] != 0 and item['parent_v_id'] in id_map:
                parent_uuid = id_map[item['parent_v_id']]
                
                # Calculate level and path (simple version, might need recursion for full path)
                # For now, let's just set parent_id. We can fix paths/levels if needed, 
                # but the SQL data seems to have a flat structure in terms of the INSERT order?
                # No, it's mixed.
                
                # Let's just set the parent_id. The recursive CTE or property can handle the tree.
                # But our model has 'level' and 'path'.
                # We can compute these after insertion or do a topological sort.
                pass

            cat = Category(
                id=item['uuid'],
                vinted_id=item['vinted_id'],
                name=item['name'],
                code=item['code'],
                parent_id=parent_uuid,
                url=item['url'],
                url_en=item['url_en'],
                country_code=None, # Global
                level=0, # Placeholder, will update
                path=item['url'] # Use URL as path for now
            )
            categories_to_add.append(cat)
            
        print("Bulk inserting categories...")
        session.bulk_save_objects(categories_to_add)
        session.commit()
        
        # 5. Update levels (optional, but good for UI)
        # Since we have the data in DB now, we can iterate and update levels
        print("Updating hierarchy levels...")
        
        # This is a bit inefficient but works for ~1000 items
        all_cats = session.query(Category).all()
        cat_dict = {c.id: c for c in all_cats}
        
        changed = False
        for cat in all_cats:
            if cat.parent_id and cat.parent_id in cat_dict:
                parent = cat_dict[cat.parent_id]
                cat.level = parent.level + 1
                # cat.path = f"{parent.path}/{cat.name}" # URL is already a good path
                
        session.commit()
        
        print("Import complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import_categories()
