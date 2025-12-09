"""
Helper functions for alert operations.

Contains reusable logic for alert management.
"""

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models import Alert, ItemHistory

logger = logging.getLogger(__name__)


def get_user_alert(db: Session, alert_id: str, user_id: str) -> Alert:
    """
    Retrieve an alert by ID and verify ownership.

    Args:
        db: Database session
        alert_id: Alert UUID
        user_id: Owner user ID

    Returns:
        Alert object if found and owned by user

    Raises:
        HTTPException 404: If alert not found or doesn't belong to user
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    return alert


def handle_reactivation(db: Session, alert: Alert, new_active_status: bool):
    """
    Handle alert reactivation logic.

    When an alert transitions from inactive to active, this clears
    the old item history and resets the baseline check timestamp.

    Args:
        db: Database session
        alert: Alert object to check/update
        new_active_status: New is_active value

    Side effects:
        - Deletes all ItemHistory for the alert
        - Sets alert.last_checked_at to None
        - Logs reactivation event
    """
    # Check if transitioning from inactive to active (reactivation)
    if not alert.is_active and new_active_status:
        # Clear old history and reset last_checked_at for fresh baseline
        db.query(ItemHistory).filter(ItemHistory.alert_id == alert.id).delete()
        alert.last_checked_at = None
        logger.info(f"Alert {alert.id} reactivated - cleared history and resetting baseline")
