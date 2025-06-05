"""
Centralized logging setup for Altman Z-Score analysis.
Provides a get_logger() function for consistent logger configuration across modules.
"""

import logging
import sys
from typing import Optional

_LOGGER_INITIALIZED = False

def setup_logging(level: int = logging.INFO, stream = sys.stdout, fmt: Optional[str] = None):
    """
    Set up root logger with a consistent format and level. Idempotent.
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
    """
    Get a logger with the given name, ensuring centralized config is applied.
    """
    setup_logging()
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
