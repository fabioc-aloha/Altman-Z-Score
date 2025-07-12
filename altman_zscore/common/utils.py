"""
Common utility functions for the Altman Z-Score package.

This module contains shared utilities used across multiple layers.
"""

import os
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def sanitize_for_logging(text: str) -> str:
    """
    Sanitize text for safe logging on Windows systems.
    
    Replaces emojis and problematic Unicode characters with safe alternatives.
    This is particularly important on Windows systems where the default console
    encoding (cp1252) cannot handle Unicode emojis.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for logging
    """
    if not text:
        return text
    
    # Replace common emojis that cause encoding issues
    emoji_replacements = {
        '📊': '[CHART]',
        '📈': '[UP_TREND]', 
        '📉': '[DOWN_TREND]',
        '💰': '[MONEY]',
        '⚠️': '[WARNING]',
        '✅': '[CHECK]',
        '❌': '[X]',
        '🚀': '[ROCKET]',
        '🔍': '[SEARCH]',
        '💡': '[IDEA]',
        '⭐': '[STAR]',
        '🎯': '[TARGET]',
        '📋': '[LIST]',
        '🔥': '[FIRE]',
        '⚡': '[LIGHTNING]',
        '🌟': '[SPARKLE]',
        '📱': '[PHONE]',
        '💻': '[LAPTOP]',
        '🖥️': '[DESKTOP]',
        '📝': '[MEMO]',
        '📄': '[PAGE]',
        '🎨': '[ART]',
        '🎭': '[THEATER]',
        '🎪': '[CIRCUS]',
        '🎯': '[DART]'
    }
    
    sanitized = text
    for emoji, replacement in emoji_replacements.items():
        sanitized = sanitized.replace(emoji, replacement)
    
    # Handle any remaining problematic characters by encoding/decoding
    try:
        # Try to encode/decode with cp1252 to catch other problematic chars
        sanitized = sanitized.encode('cp1252', errors='replace').decode('cp1252')
    except Exception:
        # If that fails, fall back to ASCII replacement
        sanitized = sanitized.encode('ascii', errors='replace').decode('ascii')
    
    return sanitized

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

def load_portfolio_from_file(file_path: Union[str, Path], validate_tickers: bool = True) -> List[str]:
    """
    Load ticker symbols from a portfolio file with robust inline comment support.
    
    This is the centralized portfolio reader used across all Altman Z-Score systems.
    
    Supported formats:
    - AAPL                    # Apple Inc.
    - MSFT # Microsoft Corp.
    - # Full line comments
    - IBE.MC                  # Iberdrola (Madrid exchange)
    - 000660.KS               # SK Hynix (Korean exchange)
    - BRK-B                   # Berkshire Hathaway Class B
    - NOVO-B.CO               # Novo Nordisk (Copenhagen)
    
    Args:
        file_path: Path to the portfolio file
        validate_tickers: Whether to validate ticker format (default: True)
        
    Returns:
        List of unique ticker symbols (cleaned and validated)
        
    Raises:
        FileNotFoundError: If the portfolio file doesn't exist
        ValueError: If no valid tickers found in file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {file_path}")
    
    tickers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                original_line = line
                line = line.strip()
                
                # Skip empty lines and full-line comments
                if not line or line.startswith('#'):
                    continue
                
                # Split on first '#' to handle inline comments
                parts = line.split('#', 1)
                ticker = parts[0].strip()
                comment = parts[1].strip() if len(parts) > 1 else ""
                
                # Skip if no ticker after comment removal
                if not ticker:
                    continue
                
                if validate_tickers:
                    # Enhanced ticker validation for international and complex formats
                    # Supports: AAPL, IBE.MC, 000660.KS, BRK-B, NOVO-B.CO, etc.
                    ticker_pattern = r'^[A-Z0-9.-]{1,12}$'
                    
                    if re.match(ticker_pattern, ticker, re.IGNORECASE):
                        # Convert to uppercase for consistency
                        ticker = ticker.upper()
                        tickers.append(ticker)
                    else:
                        # Log invalid tickers for debugging
                        logger.warning(f"Invalid ticker '{ticker}' on line {line_num} in {file_path}: {original_line.strip()}")
                else:
                    # No validation - just clean and add
                    ticker = ticker.upper()
                    tickers.append(ticker)
                    
    except Exception as e:
        logger.error(f"Error reading portfolio file {file_path}: {str(e)}")
        raise
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)
    
    if not unique_tickers:
        raise ValueError(f"No valid tickers found in portfolio file: {file_path}")
    
    logger.info(f"Loaded {len(unique_tickers)} unique tickers from {file_path}")
    return unique_tickers


def parse_tickers_from_content(content: str, validate_tickers: bool = True) -> List[str]:
    """
    Parse ticker symbols from content string with robust inline comment support.
    
    This function provides the same parsing logic as load_portfolio_from_file
    but works directly with content strings instead of files.
    
    Supported formats:
    - AAPL                    # Apple Inc.
    - MSFT # Microsoft Corp.
    - # Full line comments
    - IBE.MC                  # Iberdrola (Madrid exchange)
    - 000660.KS               # SK Hynix (Korean exchange)
    - BRK-B                   # Berkshire Hathaway Class B
    - NOVO-B.CO               # Novo Nordisk (Copenhagen)
    
    Args:
        content: String content containing ticker symbols
        validate_tickers: Whether to validate ticker format (default: True)
        
    Returns:
        List of unique ticker symbols (cleaned and validated)
    """
    if not content:
        return []
    
    tickers = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        original_line = line
        line = line.strip()
        
        # Skip empty lines and full-line comments
        if not line or line.startswith('#'):
            continue
        
        # Split on first '#' to handle inline comments
        parts = line.split('#', 1)
        ticker = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else ""
        
        # Skip if no ticker after comment removal
        if not ticker:
            continue
        
        if validate_tickers:
            # Enhanced ticker validation for international and complex formats
            # Supports: AAPL, IBE.MC, 000660.KS, BRK-B, NOVO-B.CO, etc.
            ticker_pattern = r'^[A-Z0-9.-]{1,12}$'
            
            if re.match(ticker_pattern, ticker, re.IGNORECASE):
                # Convert to uppercase for consistency
                ticker = ticker.upper()
                tickers.append(ticker)
            else:
                # Log invalid tickers for debugging
                logger.warning(f"Invalid ticker '{ticker}' on line {line_num}: {original_line.strip()}")
        else:
            # No validation - just clean and add
            ticker = ticker.upper()
            tickers.append(ticker)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)
    
    return unique_tickers


def is_valid_ticker_format(ticker: str) -> bool:
    """
    Validate if a string matches valid ticker format.
    
    Supports international exchanges and complex formats:
    - US: AAPL, BRK-B, BF-B
    - European: IBE.MC, ASML.AS, NESN.SW
    - Asian: 000660.KS, 9984.T
    - Special: NOVO-B.CO
    
    Args:
        ticker: String to validate
        
    Returns:
        True if valid ticker format, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Length check
    if len(ticker) < 1 or len(ticker) > 12:
        return False
    
    # Pattern check for valid ticker characters
    ticker_pattern = r'^[A-Z0-9.-]+$'
    
    return bool(re.match(ticker_pattern, ticker.upper()))

# This file will be expanded during refactoring with additional utilities
