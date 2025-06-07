"""
Centralized error handling utilities and custom exception classes for Altman Z-Score pipeline.

Defines custom exceptions for data validation, fetching, and output errors, and provides a utility for raising exceptions with context and logging.
"""

import logging

logger = logging.getLogger(__name__)

class AltmanZScoreError(Exception):
    """Base exception for Altman Z-Score pipeline errors."""
    pass

class DataValidationError(AltmanZScoreError):
    """Exception for data validation errors."""
    pass

class DataFetchingError(AltmanZScoreError):
    """Exception for data fetching errors (e.g., API failures)."""
    pass

class OutputWriteError(AltmanZScoreError):
    """Exception for output writing errors (e.g., file I/O)."""
    pass

def raise_with_context(exc_class, message, context=None):
    """Raise an exception with additional context and log the error.

    Args:
        exc_class (Exception): Exception class to raise.
        message (str): Error message.
        context (Any, optional): Additional context to include in the log and exception message.

    Raises:
        exc_class: The exception with the provided message and context.
    """
    if context:
        logger.error(f"{exc_class.__name__}: {message} | Context: {context}")
        raise exc_class(f"{message} | Context: {context}")
    else:
        logger.error(f"{exc_class.__name__}: {message}")
        raise exc_class(message)
