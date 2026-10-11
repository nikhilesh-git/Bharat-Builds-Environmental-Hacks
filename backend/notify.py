"""
Notification Handler (Stub for AWS SNS / Local Logger)
Owned by Teammate C on the 'c-aws' branch.
"""

import os
import logging

logger = logging.getLogger("kabadi.notify")

def notify(event: str, request_data: dict):
    """
    Publish notification. When NOTIFY=sns, publishes to SNS_TOPIC_ARN.
    When NOTIFY=log, logs locally.
    """
    mode = os.environ.get("NOTIFY", "log").lower()
    if mode == "sns":
        # Overwritten by C with boto3 sns.publish
        logger.info(f"[SNS STUB] Event: {event} | Request ID: {request_data.get('id')}")
    else:
        logger.info(f"[LOCAL NOTIFY LOG] Event: {event} | Request ID: {request_data.get('id')}")
