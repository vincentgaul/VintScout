"""Condition model storing Vinted status ids."""

from sqlalchemy import Column, Integer, String

from backend.database import Base


class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Condition {self.id} {self.name}>"
