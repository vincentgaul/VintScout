"""
Size Model

Stores available sizes for different categories.
Size categories from Vinted's size system:
- 4: Women's clothing (Tailles)
- 7: Women's shoes (Chaussures)
- 14: Men's clothing (Tailles hommes)
- 38: Men's shoes (Chaussures hommes)
- 31: Children's shoes
- 32: Children's/baby clothing
- 53: Bras
- 52/56: Rings
- 55: Bedding
"""

from sqlalchemy import Column, Integer, String
from backend.database import Base


class Size(Base):
    """
    Size entry for a specific category.

    Note: category_id here refers to Vinted's SIZE CATEGORY (not catalog category)
    Examples:
    - category_id=38 → Men's shoes (sizes 38, 39, 40, 41, 42...)
    - category_id=4 → Women's clothing (sizes XS, S, M, L, XL...)
    """
    __tablename__ = "sizes"

    id = Column(Integer, primary_key=True)  # Vinted size ID (e.g., 784 for size 42)
    title = Column(String(80), nullable=False)  # Size name (e.g., "42", "M", "XL")
    category_id = Column(Integer, nullable=False, index=True)  # Size category ID

    def __repr__(self):
        return f"<Size {self.title} (category={self.category_id})>"
