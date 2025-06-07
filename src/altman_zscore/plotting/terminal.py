"""
Terminal output utilities for plotting modules in Altman Z-Score analysis.

Provides print_info, print_warning, and print_error functions that wrap Python logging for consistent terminal output.
"""
import logging
from .colors import ColorScheme

def print_info(msg):
    """
    Print an info message using logging.info.
    
    Args:
        msg: Message string to log.
    """
    logging.info(msg)

def print_warning(msg):
    """
    Print a warning message using logging.warning.
    
    Args:
        msg: Message string to log.
    """
    logging.warning(msg)

def print_error(msg):
    """
    Print an error message using logging.error.
    
    Args:
        msg: Message string to log.
    """
    logging.error(msg)
