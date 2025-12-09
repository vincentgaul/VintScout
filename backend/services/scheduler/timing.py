"""
Alert timing calculations.

Determines when alerts should be scanned based on their intervals.
"""

from datetime import datetime, timedelta
from backend.models import Alert


def is_alert_due(alert: Alert) -> bool:
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


def get_next_check_time(alert: Alert) -> datetime:
    """
    Get the datetime when this alert will next be checked.

    Args:
        alert: Alert to calculate next check time for

    Returns:
        DateTime of next scheduled check
    """
    if not alert.last_checked_at:
        return datetime.utcnow()

    return alert.last_checked_at + timedelta(minutes=alert.check_interval_minutes)
