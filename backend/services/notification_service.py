"""
Notification Service

Sends notifications when new Vinted items are found.

Supports multiple notification channels:
- Email (SMTP)
- Slack (Webhooks)
- Telegram (Bot API)

Each alert can configure which channels to use via notification_config JSON field.

Example notification_config:
{
    "email": {
        "enabled": true,
        "to": "user@example.com"
    },
    "slack": {
        "enabled": true,
        "webhook_url": "https://hooks.slack.com/services/..."
    },
    "telegram": {
        "enabled": true,
        "chat_id": "123456789"
    }
}

For MVP, we'll log notifications instead of actually sending them.
Actual implementation will be added in Phase 2.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.models import Alert
from backend.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications about new Vinted items.

    Currently logs notifications. Email/Slack/Telegram will be implemented in Phase 2.
    """

    def __init__(self):
        """Initialize notification service."""
        self.telegram_enabled = bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', None))

        logger.info(
            f"Notification service initialized - "
            f"Telegram: {self.telegram_enabled}"
        )

    def notify(self, alert: Alert, items: List[Dict[str, Any]]):
        """
        Send notifications for new items found in an alert.

        Args:
            alert: Alert that found the items
            items: List of new item dictionaries from Vinted

        The notification config is stored in alert.notification_config as JSON.
        """
        if not items:
            logger.debug(f"No items to notify for alert '{alert.name}'")
            return

        # Get notification config from alert
        config = alert.notification_config or {}

        logger.info(
            f"Sending notifications for alert '{alert.name}' - "
            f"{len(items)} new items found"
        )

        # Send to each enabled channel
        if config.get("telegram", {}).get("enabled"):
            self._send_telegram(alert, items, config["telegram"])

        # If no channels configured, just log
        if not config.get("telegram", {}).get("enabled"):
            logger.warning(
                f"Alert '{alert.name}' has no notification channels configured. "
                f"Items found but not sent anywhere!"
            )
            self._log_items(alert, items)

    def _send_telegram(self, alert: Alert, items: List[Dict[str, Any]], config: dict):
        """
        Send Telegram notification via bot API.
        """
        chat_id = config.get("chat_id") or settings.TELEGRAM_CHAT_ID
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        if not chat_id or not bot_token:
            logger.warning(f"Telegram enabled for alert '{alert.name}' but chat_id or bot_token missing.")
            return

        logger.info(f"[TELEGRAM] Sending to chat {chat_id} for alert '{alert.name}' - {len(items)} items")

        try:
            import httpx

            base_url = f"https://api.telegram.org/bot{bot_token}"

            # Send header message
            message = (
                f"🔔 *Vinted Alert: {alert.name}*\n\n"
                f"Found {len(items)} new items!\n\n"
            )

            # Add each item (limit to 10)
            for i, item in enumerate(items[:10], 1):
                price = f"{item['price']} {item.get('currency', '')}"
                # Escape markdown special chars if needed, but for now simple format
                message += (
                    f"{i}. [{item['title']}]({item['url']})\n"
                    f"   💰 {price}\n\n"
                )

            if len(items) > 10:
                message += f"... and {len(items) - 10} more items\n"

            # Send via Telegram API
            response = httpx.post(
                f"{base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }
            )
            response.raise_for_status()
            
            logger.info(f"[TELEGRAM] Successfully sent notification")

        except Exception as e:
            logger.error(f"[TELEGRAM] Failed to send notification: {e}")

    def _log_items(self, alert: Alert, items: List[Dict[str, Any]]):
        """Log items to console (fallback when no notification channels configured)."""
        logger.info(f"=== New items for alert '{alert.name}' ===")

        for i, item in enumerate(items, 1):
            logger.info(
                f"{i}. {item['title']} - "
                f"{item['price']} {item.get('currency', '')} - "
                f"{item['url']}"
            )

        logger.info(f"=== End of {len(items)} items ===")


# Global notification service instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance (singleton)."""
    global _notification_service

    if _notification_service is None:
        _notification_service = NotificationService()

    return _notification_service
