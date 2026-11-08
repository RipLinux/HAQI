"""Logging setup for the API process."""

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure a concise, process-wide log format."""

    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
