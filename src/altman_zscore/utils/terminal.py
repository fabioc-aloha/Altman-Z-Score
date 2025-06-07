"""
Terminal output formatting helpers for Altman Z-Score analysis.

Centralizes info, warning, error, and header print functions using Colors. All functions are deprecated in favor of logging.
"""

from .colors import Colors
import logging

def print_info(msg: str):
    """Deprecated. Use logging.info directly for informational messages.

    Args:
        msg (str): Message to log.
    """
    raise NotImplementedError("print_info is deprecated. Use logging.info directly.")

def print_warning(msg: str):
    """Deprecated. Use logging.warning directly for warning messages.

    Args:
        msg (str): Message to log.
    """
    raise NotImplementedError("print_warning is deprecated. Use logging.warning directly.")

def print_error(msg: str):
    """Deprecated. Use logging.error directly for error messages.

    Args:
        msg (str): Message to log.
    """
    raise NotImplementedError("print_error is deprecated. Use logging.error directly.")

def print_success(msg: str):
    """Deprecated. Use logging.info directly for success messages.

    Args:
        msg (str): Message to log.
    """
    raise NotImplementedError("print_success is deprecated. Use logging.info directly.")

def print_header(msg: str):
    """Deprecated. Use logging.info directly for header messages.

    Args:
        msg (str): Message to log.
    """
    raise NotImplementedError("print_header is deprecated. Use logging.info directly.")
