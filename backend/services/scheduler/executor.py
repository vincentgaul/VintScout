"""
Alert execution logic.

Handles running individual alerts and notifying on new items.
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models import Alert
from backend.services.scanner_service import ScannerService
from backend.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)


def run_alert(db: Session, alert: Alert, notifier):
    """
    Run scanner for a single alert.

    Args:
        db: Database session
        alert: Alert to scan
        notifier: Notification service instance
    """
    try:
        logger.info(f"Scanning alert: {alert.name}")

        # Create scanner with db session
        scanner = ScannerService(db)

        # Run scanner
        new_items = scanner.check_alert(alert)

        # Update alert metadata
        alert.last_checked_at = datetime.utcnow()
        alert.last_found_count = len(new_items)

        logger.info(
            f"Alert '{alert.name}' scan complete - "
            f"found {len(new_items)} new items"
        )

        # Send notifications for new items
        if new_items:
            try:
                notifier.notify(alert, new_items)
                logger.info(f"Notifications sent for {len(new_items)} new items")
            except Exception as e:
                logger.error(f"Failed to send notifications: {e}", exc_info=True)

    except Exception as e:
        logger.error(
            f"Error scanning alert '{alert.name}' (ID: {alert.id}): {e}",
            exc_info=True
        )
        # Don't raise - we want to continue checking other alerts


def run_alert_now(alert_id: str, db: Session) -> dict:
    """
    Manually trigger an alert to run immediately (for testing/manual runs).

    Args:
        alert_id: UUID of alert to run
        db: Database session

    Returns:
        Dictionary with results: {"success": bool, "new_items": int, "error": str}
    """
    try:
        # Get alert
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            return {
                "success": False,
                "new_items": 0,
                "error": f"Alert {alert_id} not found"
            }

        logger.info(f"Manually running alert: {alert.name}")

        # Create scanner with db session
        scanner = ScannerService(db)

        # Run scanner
        new_items = scanner.check_alert(alert)

        # Update metadata
        alert.last_checked_at = datetime.utcnow()
        alert.last_found_count = len(new_items)

        logger.info(f"Manual scan complete - found {len(new_items)} new items")

        return {
            "success": True,
            "new_items": len(new_items),
            "items": new_items
        }

    except Exception as e:
        logger.error(f"Error in manual alert run: {e}", exc_info=True)

        return {
            "success": False,
            "new_items": 0,
            "error": str(e)
        }
