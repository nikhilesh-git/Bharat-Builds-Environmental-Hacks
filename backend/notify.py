"""
backend/notify.py
Notification stub for Kabadi Connect.
Replace the body of notify() with real logic (SNS, SES, FCM, SMS, etc.)
without changing the signature.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def notify(event: str, request: dict[str, Any]) -> None:
    """
    Send a notification for the given lifecycle event.

    Parameters
    ----------
    event : str
        Event name, e.g. "request_created", "status_updated".
    request : dict
        The full PickupRequest dict at the time of the event.

    This is a stub — it only logs. Wire up real transport here.
    """
    logger.info(
        "NOTIFY stub | event=%s | request_id=%s | status=%s",
        event,
        request.get("id"),
        request.get("status"),
    )
