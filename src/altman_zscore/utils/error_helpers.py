import logging

"""
Centralized error handling utilities and custom exception classes for Altman Z-Score pipeline.
"""

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

# Utility function for raising with context
def raise_with_context(exc_class, message, context=None):
    if context:
        logger.error(f"{exc_class.__name__}: {message} | Context: {context}")
        raise exc_class(f"{message} | Context: {context}")
    else:
        logger.error(f"{exc_class.__name__}: {message}")
        raise exc_class(message)
