"""
Scanner Service (Alert Checking)

Core service that checks alerts for new Vinted items.

Flow:
1. Get active alerts that need checking (based on check_interval_minutes)
2. For each alert, search Vinted with alert's parameters
3. Check each found item against ItemHistory for deduplication
4. Add new items to history
5. Return new items for notification

This service is meant to be called periodically by a background scheduler.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.models import Alert, ItemHistory
from backend.services.vinted_client import VintedClient, VintedAPIError


logger = logging.getLogger(__name__)


class ScannerService:
    """
    Service for scanning alerts and finding new items.

    Handles item search, deduplication, and history tracking.
    """

    def __init__(self, db: Session):
        """
        Initialize scanner service.

        Args:
            db: Database session
        """
        self.db = db

    def get_alerts_to_check(self) -> List[Alert]:
        """
        Get all alerts that need checking now.

        An alert needs checking if:
        - It's active (is_active=True)
        - It hasn't been checked recently (last_checked_at + check_interval_minutes < now)

        Returns:
            List of Alert objects ready to be checked
        """
        now = datetime.utcnow()

        # Get all active alerts
        alerts = self.db.query(Alert).filter(Alert.is_active == True).all()

        # Filter by check interval
        alerts_to_check = []
        for alert in alerts:
            if alert.last_checked_at is None:
                # Never checked, needs checking
                alerts_to_check.append(alert)
            else:
                # Check if enough time has passed
                next_check = alert.last_checked_at + timedelta(minutes=alert.check_interval_minutes)
                if now >= next_check:
                    alerts_to_check.append(alert)

        logger.info(f"Found {len(alerts_to_check)} alerts ready to check (out of {len(alerts)} active)")

        return alerts_to_check

    def check_alert(self, alert: Alert) -> List[Dict[str, Any]]:
        """
        Check a single alert for new items.

        Args:
            alert: Alert to check

        Returns:
            List of new item dictionaries (not yet in history)
        """
        logger.info(f"Checking alert: {alert.name} (ID: {alert.id})")

        try:
            # Build search parameters from alert
            brand_ids = alert.brand_list if alert.brand_ids else None
            catalog_ids = alert.catalog_list if alert.catalog_ids else None

            # Search Vinted
            with VintedClient(alert.country_code) as client:
                results = client.search_items(
                    search_text=alert.search_text,
                    brand_ids=brand_ids,
                    catalog_ids=catalog_ids,
                    price_from=alert.price_min,
                    price_to=alert.price_max,
                    currency=alert.currency,
                    order="newest_first",  # Always check newest first
                    per_page=20  # Check first page only for performance
                )

            items = results.get("items", [])
            logger.info(f"Found {len(items)} items for alert {alert.id}")

            # Check for duplicates and filter new items
            new_items = []
            for item in items:
                item_id = str(item.get("id"))

                # Check if already in history
                if ItemHistory.exists(self.db, alert.id, item_id):
                    logger.debug(f"Item {item_id} already in history, skipping")
                    continue

                # New item!
                new_items.append(item)
                logger.debug(f"New item found: {item.get('title')} ({item_id})")

                # Add to history
                ItemHistory.record(self.db, alert.id, item)

            # Update alert stats
            alert.last_checked_at = datetime.utcnow()
            alert.last_found_count = len(new_items)
            alert.total_found_count += len(new_items)

            self.db.commit()

            logger.info(f"Alert {alert.id}: Found {len(new_items)} new items")

            return new_items

        except VintedAPIError as e:
            logger.error(f"Failed to check alert {alert.id}: {e}")
            # Update last_checked_at anyway to avoid hammering API
            alert.last_checked_at = datetime.utcnow()
            alert.last_found_count = 0
            self.db.commit()
            return []

    def check_all_alerts(self) -> Dict[str, Any]:
        """
        Check all alerts that need checking.

        This is the main entry point for the background scanner job.

        Returns:
            Dictionary with scan statistics:
                - alerts_checked: Number of alerts checked
                - total_new_items: Total new items found
                - alerts_with_new_items: Number of alerts that found new items
        """
        alerts_to_check = self.get_alerts_to_check()

        total_new_items = 0
        alerts_with_new_items = 0

        for alert in alerts_to_check:
            new_items = self.check_alert(alert)

            if new_items:
                total_new_items += len(new_items)
                alerts_with_new_items += 1

        logger.info(
            f"Scan complete: Checked {len(alerts_to_check)} alerts, "
            f"found {total_new_items} new items across {alerts_with_new_items} alerts"
        )

        return {
            "alerts_checked": len(alerts_to_check),
            "total_new_items": total_new_items,
            "alerts_with_new_items": alerts_with_new_items
        }

    def check_alert_now(self, alert_id: str) -> Dict[str, Any]:
        """
        Manually check a specific alert (bypass interval check).

        Useful for "check now" button in UI.

        Args:
            alert_id: Alert UUID

        Returns:
            Dictionary with:
                - new_items_count: Number of new items found
                - new_items: List of new item dicts
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        new_items = self.check_alert(alert)

        return {
            "new_items_count": len(new_items),
            "new_items": new_items
        }
