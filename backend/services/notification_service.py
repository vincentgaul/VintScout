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
        self.email_enabled = bool(settings.SMTP_HOST)
        self.slack_enabled = bool(getattr(settings, 'SLACK_WEBHOOK_URL', None))
        self.telegram_enabled = bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', None))

        logger.info(
            f"Notification service initialized - "
            f"Email: {self.email_enabled}, "
            f"Slack: {self.slack_enabled}, "
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
        if config.get("email", {}).get("enabled"):
            self._send_email(alert, items, config["email"])

        if config.get("slack", {}).get("enabled"):
            self._send_slack(alert, items, config["slack"])

        if config.get("telegram", {}).get("enabled"):
            self._send_telegram(alert, items, config["telegram"])

        # If no channels configured, just log
        if not any([
            config.get("email", {}).get("enabled"),
            config.get("slack", {}).get("enabled"),
            config.get("telegram", {}).get("enabled")
        ]):
            logger.warning(
                f"Alert '{alert.name}' has no notification channels configured. "
                f"Items found but not sent anywhere!"
            )
            self._log_items(alert, items)

    def _send_email(self, alert: Alert, items: List[Dict[str, Any]], config: dict):
        """
        Send email notification.

        TODO: Implement actual email sending in Phase 2.
        For now, just log.
        """
        to_email = config.get("to", "unknown@example.com")

        logger.info(
            f"[EMAIL] Would send to {to_email} for alert '{alert.name}' - "
            f"{len(items)} items"
        )

        # Log each item
        for item in items:
            logger.info(
                f"[EMAIL] - {item['title']} | {item['price']} {item.get('currency', '')} | "
                f"{item['url']}"
            )

        # TODO: Phase 2 implementation
        # import smtplib
        # from email.mime.text import MIMEText
        # from email.mime.multipart import MIMEMultipart
        #
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = f"Vinted Alert: {alert.name} - {len(items)} new items"
        # msg['From'] = settings.SMTP_FROM
        # msg['To'] = to_email
        #
        # # Create HTML email body
        # html = self._render_email_template(alert, items)
        # msg.attach(MIMEText(html, 'html'))
        #
        # # Send via SMTP
        # with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        #     server.starttls()
        #     server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        #     server.send_message(msg)

    def _send_slack(self, alert: Alert, items: List[Dict[str, Any]], config: dict):
        """
        Send Slack notification via webhook.

        TODO: Implement actual Slack sending in Phase 2.
        For now, just log.
        """
        webhook_url = config.get("webhook_url", "not configured")

        logger.info(
            f"[SLACK] Would send to {webhook_url} for alert '{alert.name}' - "
            f"{len(items)} items"
        )

        # Log each item
        for item in items:
            logger.info(
                f"[SLACK] - {item['title']} | {item['price']} {item.get('currency', '')} | "
                f"{item['url']}"
            )

        # TODO: Phase 2 implementation
        # import httpx
        #
        # # Build Slack message blocks
        # blocks = [
        #     {
        #         "type": "header",
        #         "text": {
        #             "type": "plain_text",
        #             "text": f"🔔 Vinted Alert: {alert.name}"
        #         }
        #     },
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": f"Found *{len(items)}* new items!"
        #         }
        #     }
        # ]
        #
        # # Add each item
        # for item in items[:10]:  # Limit to 10 to avoid Slack limits
        #     blocks.append({
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn",
        #             "text": (
        #                 f"*<{item['url']}|{item['title']}>*\n"
        #                 f"💰 {item['price']} {item['currency']}"
        #             )
        #         },
        #         "accessory": {
        #             "type": "image",
        #             "image_url": item['image_url'],
        #             "alt_text": item['title']
        #         }
        #     })
        #
        # # Send to Slack
        # response = httpx.post(webhook_url, json={"blocks": blocks})
        # response.raise_for_status()

    def _send_telegram(self, alert: Alert, items: List[Dict[str, Any]], config: dict):
        """
        Send Telegram notification via bot API.

        TODO: Implement actual Telegram sending in Phase 2.
        For now, just log.
        """
        chat_id = config.get("chat_id", "unknown")

        logger.info(
            f"[TELEGRAM] Would send to chat {chat_id} for alert '{alert.name}' - "
            f"{len(items)} items"
        )

        # Log each item
        for item in items:
            logger.info(
                f"[TELEGRAM] - {item['title']} | {item['price']} {item.get('currency', '')} | "
                f"{item['url']}"
            )

        # TODO: Phase 2 implementation
        # import httpx
        #
        # bot_token = settings.TELEGRAM_BOT_TOKEN
        # base_url = f"https://api.telegram.org/bot{bot_token}"
        #
        # # Send header message
        # message = (
        #     f"🔔 *Vinted Alert: {alert.name}*\n\n"
        #     f"Found {len(items)} new items!\n\n"
        # )
        #
        # # Add each item (limit to 10)
        # for i, item in enumerate(items[:10], 1):
        #     message += (
        #         f"{i}. [{item['title']}]({item['url']})\n"
        #         f"   💰 {item['price']} {item['currency']}\n\n"
        #     )
        #
        # if len(items) > 10:
        #     message += f"... and {len(items) - 10} more items\n"
        #
        # # Send via Telegram API
        # response = httpx.post(
        #     f"{base_url}/sendMessage",
        #     json={
        #         "chat_id": chat_id,
        #         "text": message,
        #         "parse_mode": "Markdown",
        #         "disable_web_page_preview": True
        #     }
        # )
        # response.raise_for_status()

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
