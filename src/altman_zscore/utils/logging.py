"""
Centralized logging setup for Altman Z-Score analysis.

Provides setup_logging() and get_logger() for consistent logger configuration across modules.
"""

import logging
import sys
from typing import Optional

_LOGGER_INITIALIZED = False

def setup_logging(level: int = logging.INFO, stream = sys.stdout, fmt: Optional[str] = None):
    """Set up root logger with a consistent format and level. Idempotent.

    Args:
        level (int, optional): Logging level (default: logging.INFO).
        stream (file-like, optional): Output stream for logs (default: sys.stdout).
        fmt (str, optional): Log message format string.
    """
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return
    fmt = fmt or "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt))
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    _LOGGER_INITIALIZED = True

def get_logger(name: Optional[str] = None, level: Optional[int] = None) -> logging.Logger:
    """Get a logger with the given name, ensuring centralized config is applied.

    Args:
        name (str, optional): Logger name.
        level (int, optional): Logging level to set for this logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    setup_logging()
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
