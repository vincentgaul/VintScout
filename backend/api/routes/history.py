"""
Item History API Routes (Found Items)

Displays Vinted items that were found by user's alerts.
Each record represents a product that matched an alert's search criteria.

Endpoints:
- GET /api/history - Get all found items across all user's alerts
- GET /api/alerts/{alert_id}/history - Get found items for specific alert

All endpoints require authentication (JWT token).
Users can only view items found by their own alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db, get_current_user
from backend.schemas import ItemHistoryResponse
from backend.models import User, Alert, ItemHistory


router = APIRouter(tags=["Item History"])


@router.get("/history", response_model=List[ItemHistoryResponse])
def get_all_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200, description="Max results per page"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    notified_only: bool = Query(default=False, description="Only show items that were notified")
):
    """
    Get all found items across all user's alerts.

    Returns items sorted by found_at timestamp (newest first).
    Supports pagination and filtering.

    Query parameters:
        - limit: Maximum results to return (default: 50, max: 200)
        - offset: Number of results to skip for pagination (default: 0)
        - notified_only: If true, only show items where notification was sent (default: false)

    Response:
        Array of item history objects:
        [
            {
                "id": "550e8400-...",
                "alert_id": "660e8400-...",
                "item_id": "3456789012",
                "title": "Nike Air Max 90 White - Size 42",
                "price": 65.0,
                "currency": "EUR",
                "url": "https://www.vinted.fr/items/3456789012",
                "image_url": "https://images.vinted.net/...",
                "brand_name": "Nike",
                "size": "42",
                "condition": "Good",
                "found_at": "2024-01-15T08:30:00Z",
                "notified_at": "2024-01-15T08:30:15Z"
            },
            ...
        ]

    Example:
        GET /api/history?limit=20&offset=0&notified_only=false

    Raises:
        401 Unauthorized: If no valid JWT token provided
    """
    # Get all alert IDs for this user
    user_alert_ids = db.query(Alert.id).filter(Alert.user_id == user.id).all()
    user_alert_ids = [alert_id for (alert_id,) in user_alert_ids]

    # Query item history for user's alerts
    query = db.query(ItemHistory).filter(ItemHistory.alert_id.in_(user_alert_ids))

    if notified_only:
        query = query.filter(ItemHistory.notified_at.isnot(None))

    # Apply pagination and sorting
    items = query\
        .order_by(ItemHistory.found_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    return [ItemHistoryResponse.model_validate(item) for item in items]


@router.get("/alerts/{alert_id}/history", response_model=List[ItemHistoryResponse])
def get_alert_history(
    alert_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200, description="Max results per page"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    notified_only: bool = Query(default=False, description="Only show items that were notified")
):
    """
    Get found items for a specific alert.

    Returns items sorted by found_at timestamp (newest first).
    Supports pagination and filtering.

    Path parameters:
        - alert_id: Alert UUID

    Query parameters:
        - limit: Maximum results to return (default: 50, max: 200)
        - offset: Number of results to skip for pagination (default: 0)
        - notified_only: If true, only show items where notification was sent (default: false)

    Response:
        Array of item history objects for this alert

    Example:
        GET /api/alerts/550e8400-.../history?limit=20&offset=0

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    # Verify alert exists and belongs to user
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user.id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Query item history for this alert
    query = db.query(ItemHistory).filter(ItemHistory.alert_id == alert_id)

    if notified_only:
        query = query.filter(ItemHistory.notified_at.isnot(None))

    # Apply pagination and sorting
    items = query\
        .order_by(ItemHistory.found_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    return [ItemHistoryResponse.model_validate(item) for item in items]
