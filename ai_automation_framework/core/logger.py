"""Logging utilities for the AI Automation Framework."""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from ai_automation_framework.core.config import get_config


def setup_logger(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "1 week",
) -> None:
    """
    Setup logger with file and console output.

    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: When to rotate the log file
        retention: How long to keep old log files
    """
    # Remove default handler
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler if log_file is provided
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
        )


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance.

    Args:
        name: Name for the logger (usually __name__)

    Returns:
        Logger instance
    """
    # Initialize logger if not already done
    if not logger._core.handlers:
        config = get_config()
        setup_logger(
            log_file=config.log_file,
            log_level=config.log_level,
        )

    if name:
        return logger.bind(name=name)
    return logger


# Auto-initialize logger
get_logger()
