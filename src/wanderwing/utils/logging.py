"""Structured logging configuration."""

import json
import logging
import sys
from datetime import datetime
from typing import Any

from .config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "trip_id"):
            log_data["trip_id"] = record.trip_id
        if hasattr(record, "llm_provider"):
            log_data["llm_provider"] = record.llm_provider
        if hasattr(record, "llm_tokens"):
            log_data["llm_tokens"] = record.llm_tokens
        if hasattr(record, "llm_cost"):
            log_data["llm_cost"] = record.llm_cost

        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Create root logger
    logger = logging.getLogger("wanderwing")
    logger.setLevel(settings.log_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on config
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"wanderwing.{name}")
