"""
Alert API Routes (Core Feature)

Handles CRUD operations for user alerts - the main feature of the application.
Each alert represents a saved Vinted search that gets checked periodically.

Endpoints:
- POST /api/alerts - Create new alert
- GET /api/alerts - List all user's alerts
- GET /api/alerts/{alert_id} - Get single alert
- PUT /api/alerts/{alert_id} - Update alert
- DELETE /api/alerts/{alert_id} - Delete alert
- POST /api/alerts/{alert_id}/activate - Activate/deactivate alert
- POST /api/alerts/{alert_id}/run - Manually trigger alert check

All endpoints require authentication (JWT token).
Users can only access/modify their own alerts.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.api.dependencies import get_db, get_current_user
from backend.schemas import AlertCreate, AlertUpdate, AlertResponse
from backend.models import User, Alert
from backend.services.scheduler import get_scheduler
from .helpers import get_user_alert, handle_reactivation


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new alert.

    Creates a saved search that will be checked periodically for new Vinted items.

    Request body:
        {
            "name": "Nike Sneakers France",
            "country_code": "fr",
            "search_text": "sneakers",
            "brand_ids": "53",
            "brand_names": "Nike",
            "catalog_ids": "1193",
            "catalog_names": "Shoes",
            "price_min": 20.0,
            "price_max": 100.0,
            "currency": "EUR",
            "check_interval_minutes": 15,
            "notification_config": {"email": true},
            "is_active": true
        }

    Response:
        Alert object with id, timestamps, and all search parameters

    Raises:
        401 Unauthorized: If no valid JWT token provided
    """
    # Create new alert
    new_alert = Alert(
        user_id=user.id,
        name=alert_data.name,
        country_code=alert_data.country_code,
        search_text=alert_data.search_text,
        brand_ids=alert_data.brand_ids,
        brand_names=alert_data.brand_names,
        catalog_ids=alert_data.catalog_ids,
        catalog_names=alert_data.catalog_names,
        price_min=alert_data.price_min,
        price_max=alert_data.price_max,
        currency=alert_data.currency,
        sizes=alert_data.sizes,
        conditions=alert_data.conditions,
        colors=alert_data.colors,
        check_interval_minutes=alert_data.check_interval_minutes,
        notification_config=alert_data.notification_config,
        is_active=alert_data.is_active
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return AlertResponse.model_validate(new_alert)


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = False
):
    """
    List all alerts for the current user.

    Query parameters:
        - active_only: If true, only return active alerts (default: false)

    Response:
        Array of alert objects

    Raises:
        401 Unauthorized: If no valid JWT token provided
    """
    query = db.query(Alert).filter(Alert.user_id == user.id)

    if active_only:
        query = query.filter(Alert.is_active == True)

    alerts = query.order_by(Alert.created_at.desc()).all()

    return [AlertResponse.model_validate(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single alert by ID.

    Path parameters:
        - alert_id: Alert UUID

    Response:
        Alert object with all details

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    alert = get_user_alert(db, alert_id, user.id)
    return AlertResponse.model_validate(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing alert.

    Only provided fields will be updated (partial update supported).

    Path parameters:
        - alert_id: Alert UUID

    Request body (all fields optional):
        {
            "name": "Updated Name",
            "price_max": 150.0,
            "is_active": false
        }

    Response:
        Updated alert object

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    alert = get_user_alert(db, alert_id, user.id)

    # Update only provided fields
    update_data = alert_data.model_dump(exclude_unset=True)

    # Handle reactivation if is_active changed to true
    if 'is_active' in update_data:
        handle_reactivation(db, alert, update_data['is_active'])

    for field, value in update_data.items():
        setattr(alert, field, value)

    db.commit()
    db.refresh(alert)

    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert.

    This will also delete all associated item history (cascade delete).

    Path parameters:
        - alert_id: Alert UUID

    Response:
        204 No Content (empty response)

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    alert = get_user_alert(db, alert_id, user.id)

    db.delete(alert)
    db.commit()

    return None


@router.post("/{alert_id}/activate", response_model=AlertResponse)
def toggle_alert_status(
    alert_id: str,
    is_active: bool,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate an alert.

    Inactive alerts will not be checked by the scanner.

    Path parameters:
        - alert_id: Alert UUID

    Query parameters:
        - is_active: true to activate, false to deactivate

    Response:
        Updated alert object

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    alert = get_user_alert(db, alert_id, user.id)

    # Handle reactivation logic
    handle_reactivation(db, alert, is_active)

    alert.is_active = is_active
    db.commit()
    db.refresh(alert)

    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/run")
def run_alert_now(
    alert_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually trigger an alert to run immediately.

    Useful for testing alerts or getting immediate results without waiting
    for the scheduled check.

    Path parameters:
        - alert_id: Alert UUID

    Response:
        {
            "success": true/false,
            "new_items": number of new items found,
            "items": array of items (if successful),
            "error": error message (if failed)
        }

    Raises:
        401 Unauthorized: If no valid JWT token provided
        404 Not Found: If alert doesn't exist or doesn't belong to user
    """
    # Verify ownership
    alert = get_user_alert(db, alert_id, user.id)

    # Run the alert via scheduler service
    scheduler = get_scheduler()
    result = scheduler.run_alert_now(alert_id)

    return result
