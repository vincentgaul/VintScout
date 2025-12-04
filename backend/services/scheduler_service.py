"""
Alert Scheduler Service

Runs alerts periodically to check for new Vinted items.

This service uses APScheduler to run background jobs that:
1. Check all active alerts
2. Search Vinted for new items matching alert criteria
3. Store found items in history (for deduplication)
4. Send notifications for new items

Key features:
- Runs every minute (checks which alerts are due)
- Respects each alert's check_interval_minutes setting
- Prevents duplicate notifications (via ItemHistory)
- Graceful error handling (one alert failure doesn't stop others)
- Thread-safe database access
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.database import SessionLocal
from backend.models import Alert, ItemHistory
from backend.services.scanner_service import ScannerService
from backend.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Background scheduler for running alerts periodically.

    Uses APScheduler to check alerts every minute and scan those that are due.
    """

    def __init__(self):
        """Initialize scheduler (not started yet)."""
        self.scheduler = BackgroundScheduler()
        self.scanner = ScannerService()
        self.notifier = get_notification_service()
        logger.info("Scheduler service initialized")

    def start(self):
        """
        Start the scheduler.

        Adds a job that runs every minute to check for alerts that need scanning.
        """
        if not self.scheduler.running:
            # Add job to run every minute
            self.scheduler.add_job(
                func=self.check_alerts,
                trigger=IntervalTrigger(minutes=1),
                id='check_alerts',
                name='Check all active alerts',
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Scheduler started - checking alerts every minute")
        else:
            logger.warning("Scheduler already running")

    def stop(self):
        """Stop the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
        else:
            logger.warning("Scheduler not running")

    def check_alerts(self):
        """
        Check all active alerts and run those that are due.

        This method is called every minute by the scheduler.
        It:
        1. Finds all active alerts
        2. Checks which ones are due (based on last_checked_at + check_interval)
        3. Runs scanner for each due alert
        4. Updates last_checked_at timestamp
        """
        logger.debug("Checking for alerts that need scanning")

        # Create database session
        db = SessionLocal()

        try:
            # Get all active alerts
            alerts = db.query(Alert)\
                .filter(Alert.is_active == True)\
                .all()

            if not alerts:
                logger.debug("No active alerts found")
                return

            logger.info(f"Found {len(alerts)} active alerts")

            # Check each alert
            for alert in alerts:
                if self._is_alert_due(alert):
                    logger.info(f"Alert '{alert.name}' (ID: {alert.id}) is due for checking")
                    self._run_alert(db, alert)
                else:
                    # Calculate when alert will be due
                    next_check = self._get_next_check_time(alert)
                    logger.debug(
                        f"Alert '{alert.name}' not due yet "
                        f"(next check at {next_check.strftime('%H:%M:%S')})"
                    )

            db.commit()

        except Exception as e:
            logger.error(f"Error in check_alerts: {e}", exc_info=True)
            db.rollback()

        finally:
            db.close()

    def _is_alert_due(self, alert: Alert) -> bool:
        """
        Check if an alert is due for scanning.

        Args:
            alert: Alert to check

        Returns:
            True if alert should be scanned now
        """
        # If never checked, it's due
        if not alert.last_checked_at:
            return True

        # Calculate when next check is due
        next_check = alert.last_checked_at + timedelta(minutes=alert.check_interval_minutes)

        # Check if we're past the next check time
        return datetime.utcnow() >= next_check

    def _get_next_check_time(self, alert: Alert) -> datetime:
        """Get the datetime when this alert will next be checked."""
        if not alert.last_checked_at:
            return datetime.utcnow()

        return alert.last_checked_at + timedelta(minutes=alert.check_interval_minutes)

    def _run_alert(self, db: Session, alert: Alert):
        """
        Run scanner for a single alert.

        Args:
            db: Database session
            alert: Alert to scan
        """
        try:
            logger.info(f"Scanning alert: {alert.name}")

            # Run scanner
            new_items = self.scanner.check_alert(alert)

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
                    self.notifier.notify(alert, new_items)
                    logger.info(f"Notifications sent for {len(new_items)} new items")
                except Exception as e:
                    logger.error(f"Failed to send notifications: {e}", exc_info=True)

        except Exception as e:
            logger.error(
                f"Error scanning alert '{alert.name}' (ID: {alert.id}): {e}",
                exc_info=True
            )
            # Don't raise - we want to continue checking other alerts

    def run_alert_now(self, alert_id: str) -> dict:
        """
        Manually trigger an alert to run immediately (for testing/manual runs).

        Args:
            alert_id: UUID of alert to run

        Returns:
            Dictionary with results: {"success": bool, "new_items": int, "error": str}
        """
        db = SessionLocal()

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

            # Run scanner
            new_items = self.scanner.check_alert(alert)

            # Update metadata
            alert.last_checked_at = datetime.utcnow()
            alert.last_found_count = len(new_items)

            db.commit()

            logger.info(f"Manual scan complete - found {len(new_items)} new items")

            return {
                "success": True,
                "new_items": len(new_items),
                "items": new_items
            }

        except Exception as e:
            logger.error(f"Error in manual alert run: {e}", exc_info=True)
            db.rollback()

            return {
                "success": False,
                "new_items": 0,
                "error": str(e)
            }

        finally:
            db.close()


# Global scheduler instance
_scheduler = None


def get_scheduler() -> SchedulerService:
    """Get global scheduler instance (singleton pattern)."""
    global _scheduler

    if _scheduler is None:
        _scheduler = SchedulerService()

    return _scheduler


def start_scheduler():
    """Start the global scheduler instance."""
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Global scheduler started")


def stop_scheduler():
    """Stop the global scheduler instance."""
    global _scheduler

    if _scheduler:
        _scheduler.stop()
        _scheduler = None
        logger.info("Global scheduler stopped")
