"""
backend/notify.py
Notification handler for Kabadi Connect.
Logs locally when NOTIFY=log, publishes to SNS when NOTIFY=sns.
"""

import os
import logging
from typing import Any

logger = logging.getLogger("kabadi.notify")


def notify(event: str, request: dict[str, Any]) -> None:
    """
    Send a notification for the given lifecycle event.
    """
    mode = os.environ.get("NOTIFY", "log").lower()
    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if mode == "sns" and topic_arn:
        try:
            import boto3  # noqa: PLC0415
            sns = boto3.client("sns", region_name=region)
            sns.publish(
                TopicArn=topic_arn,
                Subject=f"Kabadi Connect: {event}",
                Message=f"Event: {event}\nRequest ID: {request.get('id')}\nStatus: {request.get('status')}\nLocality: {request.get('locality')}"
            )
            return
        except Exception as e:
            logger.warning("SNS publish failed, falling back to log: %s", e)

    logger.info(
        "NOTIFY | event=%s | request_id=%s | status=%s",
        event,
        request.get("id"),
        request.get("status"),
    )
