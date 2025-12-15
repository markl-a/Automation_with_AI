"""Logging utilities for the AI Automation Framework."""

import sys
import os
import json
import time
import uuid
from pathlib import Path
from typing import Optional, Any, Dict, Callable
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps
from loguru import logger
from ai_automation_framework.core.config import get_config


# Context variable for correlation ID tracking
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def _json_serializer(record: Dict[str, Any]) -> str:
    """
    Serialize log record to JSON format.

    Args:
        record: Log record dictionary

    Returns:
        JSON formatted string
    """
    # Extract correlation ID if available
    correlation_id = _correlation_id.get()

    # Build structured log entry
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }

    # Add correlation ID if present
    if correlation_id:
        log_entry["correlation_id"] = correlation_id

    # Add extra fields from record
    if "extra" in record and record["extra"]:
        log_entry["extra"] = record["extra"]

    # Add exception info if present
    if record["exception"]:
        log_entry["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
        }

    return json.dumps(log_entry)


def setup_logger(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    use_json: bool = False,
) -> None:
    """
    Setup logger with file and console output.

    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, reads from LOG_LEVEL environment variable or defaults to INFO
        rotation: When to rotate the log file
        retention: How long to keep old log files
        use_json: If True, use JSON format for logging
    """
    # Get log level from environment if not specified
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Validate log level
    valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        log_level = "INFO"

    # Remove default handler
    logger.remove()

    if use_json:
        # JSON format for structured logging
        def json_sink(message):
            """Custom sink for JSON logging to stderr."""
            record = message.record
            json_output = _json_serializer(record) + "\n"
            sys.stderr.write(json_output)
            sys.stderr.flush()

        logger.add(
            json_sink,
            level=log_level,
        )

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            def json_file_sink(message):
                """Custom sink for JSON logging to file."""
                record = message.record
                json_output = _json_serializer(record) + "\n"
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json_output)

            logger.add(
                json_file_sink,
                level=log_level,
            )
    else:
        # Human-readable format (backward compatible)
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


def get_logger(name: Optional[str] = None) -> Any:
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

        # Check if JSON logging is enabled via environment
        use_json = os.getenv("LOG_FORMAT", "").upper() == "JSON"

        setup_logger(
            log_file=config.log_file,
            log_level=config.log_level,
            use_json=use_json,
        )

    if name:
        return logger.bind(name=name)
    return logger


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set correlation ID for request tracing.

    Args:
        correlation_id: Custom correlation ID. If None, generates a new UUID

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _correlation_id.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID.

    Returns:
        Current correlation ID or None if not set
    """
    return _correlation_id.get()


def clear_correlation_id() -> None:
    """Clear the current correlation ID."""
    _correlation_id.set(None)


@contextmanager
def log_context(**kwargs):
    """
    Context manager for temporarily adding extra fields to log messages.

    Args:
        **kwargs: Extra fields to add to log context

    Example:
        with log_context(user_id="123", request_id="abc"):
            logger.info("Processing request")  # Will include user_id and request_id
    """
    # Add correlation ID to context if present
    correlation_id = get_correlation_id()
    if correlation_id:
        kwargs["correlation_id"] = correlation_id

    token = logger.contextualize(**kwargs)
    try:
        yield
    finally:
        # Context is automatically removed when exiting
        pass


def log_performance(func: Optional[Callable] = None, *, level: str = "INFO"):
    """
    Decorator to log function execution time.

    Args:
        func: Function to decorate
        level: Log level to use (default: INFO)

    Example:
        @log_performance
        def my_function():
            pass

        @log_performance(level="DEBUG")
        def another_function():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = f.__name__
            module_name = f.__module__

            # Get correlation ID if present
            correlation_id = get_correlation_id()

            try:
                # Log function start
                extra = {
                    "function": func_name,
                    "module": module_name,
                    "phase": "start",
                }
                if correlation_id:
                    extra["correlation_id"] = correlation_id

                logger.bind(**extra).log(level, f"Starting {func_name}")

                # Execute function
                result = f(*args, **kwargs)

                # Log successful completion
                duration = time.time() - start_time
                extra["phase"] = "complete"
                extra["duration_ms"] = round(duration * 1000, 2)

                logger.bind(**extra).log(
                    level,
                    f"Completed {func_name} in {duration:.2f}s"
                )

                return result

            except Exception as e:
                # Log error with timing
                duration = time.time() - start_time
                extra = {
                    "function": func_name,
                    "module": module_name,
                    "phase": "error",
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                }
                if correlation_id:
                    extra["correlation_id"] = correlation_id

                logger.bind(**extra).error(
                    f"Failed {func_name} after {duration:.2f}s: {e}"
                )
                raise

        return wrapper

    # Handle both @log_performance and @log_performance() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


# Auto-initialize logger
get_logger()
