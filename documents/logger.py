"""
📦 documents/logger.py

🧠 CENTRAL LOGGING SYSTEM
"""

import logging

logger = logging.getLogger("identiflow")


def log_event(event, data=None, level="info"):
    message = f"{event} | {data}"

    if level == "debug":
        logger.debug(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)