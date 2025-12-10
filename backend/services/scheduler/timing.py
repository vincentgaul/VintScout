"""
Alert timing calculations.

Determines when alerts should be scanned based on their intervals.
Adds randomness (+/- 20%) to intervals to avoid detection patterns.
"""

import random
from datetime import datetime, timedelta
from backend.models import Alert


def _get_randomized_interval(base_minutes: int) -> int:
    """
    Add +/- 20% randomness to check interval.

    This helps avoid bot detection by making request timing unpredictable.

    Args:
        base_minutes: Base interval in minutes

    Returns:
        Randomized interval between 0.8x and 1.2x of base
    """
    variance = base_minutes * 0.2  # 20% variance
    min_minutes = int(base_minutes - variance)
    max_minutes = int(base_minutes + variance)
    return random.randint(min_minutes, max_minutes)


def is_alert_due(alert: Alert) -> bool:
    """
    Check if an alert is due for scanning.

    Uses randomized intervals (+/- 20%) to avoid predictable patterns.

    Args:
        alert: Alert to check

    Returns:
        True if alert should be scanned now
    """
    # If never checked, it's due
    if not alert.last_checked_at:
        return True

    # Calculate when next check is due with randomness
    randomized_interval = _get_randomized_interval(alert.check_interval_minutes)
    next_check = alert.last_checked_at + timedelta(minutes=randomized_interval)

    # Check if we're past the next check time
    return datetime.utcnow() >= next_check


def get_next_check_time(alert: Alert) -> datetime:
    """
    Get the datetime when this alert will next be checked.

    Uses randomized intervals for display purposes.

    Args:
        alert: Alert to calculate next check time for

    Returns:
        DateTime of next scheduled check (approximate due to randomness)
    """
    if not alert.last_checked_at:
        return datetime.utcnow()

    # Use base interval for display (actual will vary +/- 20%)
    return alert.last_checked_at + timedelta(minutes=alert.check_interval_minutes)
