"""
Sizes API Endpoint

Provides available size options based on selected categories.
Uses real Vinted size data stored in the database.

Data source: https://github.com/0AlphaZero0/Vinted-data
Populated via: backend/seeds/populate_sizes.py
"""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.database import get_db
from backend.models import Size

router = APIRouter(prefix="/sizes", tags=["sizes"])


def detect_size_category(catalog_names: str) -> int | None:
    """
    Detect appropriate size category based on catalog names.

    Returns the category ID from the Vinted size data, or None if not applicable.

    Size category IDs:
    - 4: General clothing (Tailles) - Women's clothing
    - 7: Women's shoes (Chaussures)
    - 14: Men's clothing (Tailles hommes)
    - 38: Men's shoes (Chaussures hommes)
    - 31: Children's shoes
    - 32: Children's/baby clothing
    - 53: Bras (Soutiens-gorge)
    - 52/56: Rings (Bagues)
    - 55: Bedding (Literie)

    Args:
        catalog_names: Comma-separated category names

    Returns:
        Size category ID or None if sizes don't apply to this category
    """
    names_lower = catalog_names.lower()

    # Categories that should NOT have sizes
    non_sizeable = [
        'clock', 'horloge',
        'book', 'livre',
        'decor', 'decoration',
        'furniture', 'meuble',
        'toy', 'jouet', 'jeu',
        'electronic', 'électronique',
        'kitchen', 'cuisine',
        'bathroom', 'salle de bain',
        'storage', 'rangement',
        'lighting', 'éclairage',
        'garden', 'jardin',
        'pet', 'animal',
    ]

    if any(keyword in names_lower for keyword in non_sizeable):
        return None

    # Footwear detection (multi-language)
    footwear_keywords = [
        # English
        'boot', 'shoe', 'sneaker', 'sandal', 'heel', 'loafer', 'trainer', 'slipper', 'footwear',
        # French
        'chaussure', 'botte', 'basket', 'sandale', 'talon', 'chausson',
        # German
        'schuh', 'stiefel', 'turnschuh',
        # Spanish
        'zapato', 'bota', 'zapatilla',
        # Italian
        'scarpa', 'stivale',
    ]

    is_footwear = any(keyword in names_lower for keyword in footwear_keywords)

    if is_footwear:
        # Check if it's men's, women's, or children's
        # Check for women FIRST to avoid "women" matching "men"
        womens_keywords = ['women', 'femme', 'frauen', 'donna', 'mujer']
        mens_keywords = ["men's", 'homme', 'männer', 'uomo', 'hombre', ' men ', '-men-']
        kids_keywords = ['kid', 'child', 'enfant', 'bébé', 'baby', 'kinder', 'bambino', 'niño']

        if any(keyword in names_lower for keyword in kids_keywords):
            return 31  # Children's shoes
        elif any(keyword in names_lower for keyword in womens_keywords):
            return 7   # Women's shoes
        elif any(keyword in names_lower for keyword in mens_keywords):
            return 38  # Men's shoes
        else:
            return 7   # Women's shoes (default for footwear)

    # Clothing detection (multi-language)
    clothing_keywords = [
        # English
        'shirt', 't-shirt', 'dress', 'jacket', 'coat', 'pants', 'jeans', 'sweater', 'top', 'bottom',
        'clothing', 'clothes', 'apparel', 'wear', 'garment', 'hoodie', 'sweatshirt', 'blazer',
        # French
        'chemise', 'robe', 'veste', 'manteau', 'pantalon', 'pull', 'vêtement', 'haut', 'bas',
        # German
        'kleidung', 'hemd', 'kleid', 'jacke', 'hose',
        # Spanish
        'ropa', 'camisa', 'vestido', 'chaqueta', 'pantalón',
        # Italian
        'abbigliamento', 'camicia', 'vestito', 'giacca', 'pantalone',
    ]

    is_clothing = any(keyword in names_lower for keyword in clothing_keywords)

    if is_clothing:
        # Check for women FIRST to avoid "women" matching "men"
        womens_keywords = ['women', 'femme', 'frauen', 'donna', 'mujer']
        mens_keywords = ["men's", 'homme', 'männer', 'uomo', 'hombre', ' men ', '-men-']
        kids_keywords = ['kid', 'child', 'enfant', 'bébé', 'baby', 'kinder', 'bambino', 'niño']

        if any(keyword in names_lower for keyword in kids_keywords):
            return 32  # Children's/baby clothing
        elif any(keyword in names_lower for keyword in womens_keywords):
            return 4   # Women's clothing
        elif any(keyword in names_lower for keyword in mens_keywords):
            return 14  # Men's clothing
        else:
            return 4   # Women's clothing (default)

    # Special categories with sizes
    if any(keyword in names_lower for keyword in ['bra', 'soutien', 'gorge']):
        return 53  # Bras

    if any(keyword in names_lower for keyword in ['ring', 'bague', 'anello', 'anneau']):
        return 52  # Rings

    # Bedding
    if any(keyword in names_lower for keyword in ['bedding', 'literie', 'bed', 'sheet', 'duvet']):
        return 55  # Bedding

    # Accessories that typically have sizes
    sizeable_accessories = [
        'hat', 'cap', 'beanie', 'chapeau', 'bonnet', 'casquette',  # Hats
        'glove', 'gant', 'handschuh',  # Gloves
        'scarf', 'écharpe', 'foulard', 'schal',  # Scarves
        'belt', 'ceinture', 'gürtel', 'cintura',  # Belts
    ]

    if any(keyword in names_lower for keyword in sizeable_accessories):
        # Check gender for accessories
        womens_keywords = ['women', 'femme', 'frauen', 'donna', 'mujer']
        mens_keywords = ["men's", 'homme', 'männer', 'uomo', 'hombre', ' men ', '-men-']
        kids_keywords = ['kid', 'child', 'enfant', 'bébé', 'baby', 'kinder', 'bambino', 'niño']

        if any(keyword in names_lower for keyword in kids_keywords):
            return 32  # Children's sizing
        elif any(keyword in names_lower for keyword in womens_keywords):
            return 4   # Women's clothing sizes
        elif any(keyword in names_lower for keyword in mens_keywords):
            return 14  # Men's clothing sizes
        else:
            return 4   # Default to women's sizes

    # Safe fallback: If we don't recognize it, assume it's wearable/sizeable
    # This errs on the side of showing sizes rather than hiding them
    # Users can always ignore the size filter if not applicable
    return 4  # Default to women's clothing sizes


@router.get("", response_model=List[Dict[str, Any]])
def get_sizes(
    catalog_ids: str = Query(..., description="Comma-separated category IDs"),
    catalog_names: str = Query(..., description="Comma-separated category names"),
    db: Session = Depends(get_db)
):
    """
    Get available sizes for selected categories.

    Uses real Vinted size data from database to return appropriate sizes based on category type.

    Args:
        catalog_ids: Comma-separated category IDs (e.g., "1233,1920")
        catalog_names: Comma-separated category names (e.g., "Men's Boots,Sneakers")
        db: Database session (injected)

    Returns:
        List of size objects with id and name fields

    Example:
        GET /api/sizes?catalog_ids=1233&catalog_names=Men's Boots
        Returns: [{"id": "784", "name": "42"}, {"id": "785", "name": "42.5"}, ...]
    """
    # Detect appropriate size category
    size_category_id = detect_size_category(catalog_names)

    # If no size category applies, return empty list
    if size_category_id is None:
        return []

    # Query sizes from database for this category
    size_entries = db.query(Size).filter(
        Size.category_id == size_category_id
    ).order_by(Size.id).all()

    if not size_entries:
        return []  # No sizes available for this category

    # Convert to API format
    sizes = []
    for size in size_entries:
        sizes.append({
            "id": str(size.id),
            "name": size.title
        })

    return sizes
