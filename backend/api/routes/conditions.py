"""Conditions API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.condition import Condition
from backend.schemas.condition import ConditionResponse

router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("", response_model=List[ConditionResponse])
def list_conditions(db: Session = Depends(get_db)):
    return db.query(Condition).order_by(Condition.sort_order, Condition.id).all()
