"""
Terminal output formatting helpers for Altman Z-Score analysis.
Centralizes info, warning, error, and header print functions using Colors.
"""
from .colors import Colors
import logging

def print_info(msg: str):
    raise NotImplementedError("print_info is deprecated. Use logging.info directly.")

def print_warning(msg: str):
    raise NotImplementedError("print_warning is deprecated. Use logging.warning directly.")

def print_error(msg: str):
    raise NotImplementedError("print_error is deprecated. Use logging.error directly.")

def print_success(msg: str):
    raise NotImplementedError("print_success is deprecated. Use logging.info directly.")

def print_header(msg: str):
    raise NotImplementedError("print_header is deprecated. Use logging.info directly.")
