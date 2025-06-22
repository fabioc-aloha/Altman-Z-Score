"""
Common utility functions for the Altman Z-Score package.

This module contains shared utilities used across multiple layers.
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Constants and configuration
DEFAULT_CACHE_DIR = ".cache"
OUTPUT_DIR = "output"

# File I/O utilities
def ensure_dir_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to check/create
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def safe_json_write(filepath: str, data: Any) -> bool:
    """
    Safely write data to a JSON file with error handling.
    
    Args:
        filepath: Path to write the JSON file
        data: Data to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        ensure_dir_exists(directory)
        
        # Write data atomically
        temp_filepath = f"{filepath}.tmp"
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        # Atomic rename
        if os.path.exists(filepath):
            os.replace(temp_filepath, filepath)
        else:
            os.rename(temp_filepath, filepath)
        
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {filepath}: {str(e)}")
        return False

def safe_json_read(filepath: str, default: Any = None) -> Any:
    """
    Safely read data from a JSON file with error handling.
    
    Args:
        filepath: Path to read the JSON file from
        default: Default value to return if file doesn't exist or is invalid
        
    Returns:
        Data from the JSON file or the default value
    """
    try:
        if not os.path.exists(filepath):
            return default
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON file {filepath}: {str(e)}")
        return default

# Date and time utilities
def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in various formats into a datetime object.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If the date string cannot be parsed
    """
    # Try various date formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_string}")

def format_date(date_obj: Union[datetime, str], output_format: str = "%Y-%m-%d") -> str:
    """
    Format a date object or string into a standardized string format.
    
    Args:
        date_obj: Date object or string to format
        output_format: Output format string
        
    Returns:
        str: Formatted date string
    """
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
    
    return date_obj.strftime(output_format)

# Type conversion utilities
def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float with error handling.
    
    Args:
        value: Value to convert
        default: Default value to return if conversion fails
        
    Returns:
        float: Converted value or default
    """
    if value is None:
        return default
        
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int with error handling.
    
    Args:
        value: Value to convert
        default: Default value to return if conversion fails
        
    Returns:
        int: Converted value or default
    """
    if value is None:
        return default
        
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Dictionary utilities
def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to extract value from
        path: Dot-separated path to the value (e.g., "facts.us-gaap.Assets.value")
        default: Default value to return if path doesn't exist
        
    Returns:
        Value at the path or the default value
    """
    if not data or not path:
        return default
        
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    
    return current

# This file will be expanded during refactoring with additional utilities
