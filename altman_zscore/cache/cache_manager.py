"""
Cache Manager - FMP Financial Data Cache Layer

This module manages the persistence, validation, and versioning of FMP financial data cache.
It provides a clean interface for storing and loading financial data from FMP API.

Key Features:
- Financial data cache persistence with atomic writes
- Version management and compatibility checking
- Cache integrity validation
- TTL-based cache expiration
- Thread-safe operations
- Support for FMP API endpoints (income statement, balance sheet, cash flow, ratios)

Usage:
    from altman_zscore.cache.cache_manager import store_financial_data, load_financial_data
    
    # Store FMP financial data
    success = store_financial_data(symbol, financial_data, cache_dir)
    
    # Load FMP financial data
    financial_data = load_financial_data(symbol, cache_dir)
"""

import os
import json
import threading
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import hashlib

# Import shared infrastructure
from ..common.logging_config import get_logger
from ..common.config import get_config
from ..common.utils import ensure_dir_exists, safe_json_read, safe_json_write
from ..common.exceptions import CacheError, ValidationError

logger = get_logger(__name__)

# Thread lock for cache operations
_cache_lock = threading.Lock()

# Cache file names for FMP data
INCOME_STATEMENT_CACHE_FILE = "income_statement.json"
BALANCE_SHEET_CACHE_FILE = "balance_sheet.json" 
CASH_FLOW_CACHE_FILE = "cash_flow.json"
FINANCIAL_RATIOS_CACHE_FILE = "financial_ratios.json"
FINANCIAL_METADATA_FILE = "financial_metadata.json"

# Cache version compatibility
SUPPORTED_CACHE_VERSIONS = ["1.0.0"]
CURRENT_CACHE_VERSION = "1.0.0"

# Default cache TTL (48 hours = 2 days)
DEFAULT_CACHE_TTL_HOURS = 48


def store_financial_data(
    symbol: str,
    financial_data: Dict[str, Any], 
    cache_dir: Optional[str] = None,
    validate_before_store: bool = True
) -> bool:
    """
    Store FMP financial data to cache with atomic write and validation.
    
    Args:
        symbol: Stock ticker symbol
        financial_data: Financial data dict with keys: income_statement, balance_sheet, cash_flow, ratios
        cache_dir: Optional custom cache directory path
        validate_before_store: Whether to validate data before storing
        
    Returns:
        bool: True if successfully stored, False otherwise
        
    Raises:
        CacheError: If unable to store cache
        ValidationError: If financial data validation fails
    """
    with _cache_lock:
        try:
            logger.info(f"Storing financial data for {symbol} to cache")
            
            # Validate financial data if requested
            if validate_before_store:
                from .validation import validate_financial_data
                validation_result = validate_financial_data(financial_data)
                if not validation_result.is_valid:
                    raise ValidationError(f"Financial data validation failed: {validation_result.errors}")
            
            # Get cache directory
            if cache_dir is None:
                cache_dir = get_default_cache_dir(symbol)
            
            # Ensure directory exists
            ensure_dir_exists(cache_dir)
            
            # Store each financial statement separately
            success_count = 0
            total_files = 0
            
            for statement_type, cache_file in [
                ('income_statement', INCOME_STATEMENT_CACHE_FILE),
                ('balance_sheet', BALANCE_SHEET_CACHE_FILE),
                ('cash_flow', CASH_FLOW_CACHE_FILE),
                ('ratios', FINANCIAL_RATIOS_CACHE_FILE)
            ]:
                if statement_type in financial_data:
                    file_path = os.path.join(cache_dir, cache_file)
                    
                    # Add storage metadata
                    enhanced_data = _add_storage_metadata(financial_data[statement_type], symbol, statement_type)
                    
                    # Store with atomic write
                    if safe_json_write(file_path, enhanced_data):
                        success_count += 1
                        logger.debug(f"Successfully stored {statement_type} for {symbol}")
                    else:
                        logger.error(f"Failed to store {statement_type} for {symbol}")
                    
                    total_files += 1
            
            # Store metadata summary
            if success_count > 0:
                _store_financial_metadata(cache_dir, symbol, financial_data, success_count, total_files)
            
            success = success_count == total_files and total_files > 0
            
            if success:
                logger.info(f"Successfully stored all financial data for {symbol}")
            else:
                logger.warning(f"Partial success storing financial data for {symbol}: {success_count}/{total_files}")
                
            return success
                
        except Exception as e:
            logger.error(f"Error storing financial data for {symbol}: {e}")
            raise CacheError(f"Failed to store financial data for {symbol}: {e}")


def load_financial_data(
    symbol: str, 
    cache_dir: Optional[str] = None,
    required_statements: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Load financial data from cache with validation and compatibility checking.
    
    Args:
        symbol: Stock ticker symbol
        cache_dir: Optional custom cache directory path
        required_statements: List of required statements (income_statement, balance_sheet, cash_flow, ratios)
        
    Returns:
        Dict containing financial data, or None if not available/valid
        
    Raises:
        CacheError: If cache exists but is corrupted
        ValidationError: If cache validation fails
    """
    with _cache_lock:
        try:
            # Get cache directory
            if cache_dir is None:
                cache_dir = get_default_cache_dir(symbol)
            
            # Check if cache directory exists
            if not os.path.exists(cache_dir):
                logger.debug(f"Cache directory not found: {cache_dir}")
                return None
            
            logger.info(f"Loading financial data for {symbol} from {cache_dir}")
            
            # Load each financial statement
            financial_data = {}
            
            for statement_type, cache_file in [
                ('income_statement', INCOME_STATEMENT_CACHE_FILE),
                ('balance_sheet', BALANCE_SHEET_CACHE_FILE), 
                ('cash_flow', CASH_FLOW_CACHE_FILE),
                ('ratios', FINANCIAL_RATIOS_CACHE_FILE)
            ]:
                file_path = os.path.join(cache_dir, cache_file)
                
                if os.path.exists(file_path):
                    statement_data = safe_json_read(file_path)
                    if statement_data:
                        # Validate cache structure
                        if _validate_financial_statement_structure(statement_data, statement_type):
                            # Check cache freshness
                            if _is_cache_expired(statement_data):
                                logger.warning(f"Cache for {symbol} {statement_type} has expired")
                            
                            financial_data[statement_type] = statement_data
                        else:
                            logger.warning(f"Invalid cache structure for {symbol} {statement_type}")
                    else:
                        logger.warning(f"Empty or corrupted cache file: {file_path}")
                else:
                    logger.debug(f"Cache file not found: {file_path}")
            
            # Check if we have required statements
            if required_statements:
                missing_statements = [stmt for stmt in required_statements if stmt not in financial_data]
                if missing_statements:
                    logger.warning(f"Missing required statements for {symbol}: {missing_statements}")
                    return None
            
            if financial_data:
                logger.info(f"Successfully loaded financial data for {symbol}")
                return financial_data
            else:
                logger.debug(f"No financial data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading financial data for {symbol}: {e}")
            if isinstance(e, (CacheError, ValidationError)):
                raise
            else:
                raise CacheError(f"Failed to load financial data for {symbol}: {e}")


def get_cache_info(symbol: str, cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about the current financial data cache without loading all data.
    
    Args:
        symbol: Stock ticker symbol
        cache_dir: Optional custom cache directory path
        
    Returns:
        Dict containing cache information
    """
    try:
        if cache_dir is None:
            cache_dir = get_default_cache_dir(symbol)
        
        info = {
            'symbol': symbol,
            'cache_dir': cache_dir,
            'exists': os.path.exists(cache_dir),
            'statements': {},
            'total_size_bytes': 0,
            'last_modified': None,
            'is_expired': True,
            'version': None
        }
        
        if info['exists']:
            # Check each financial statement
            for statement_type, cache_file in [
                ('income_statement', INCOME_STATEMENT_CACHE_FILE),
                ('balance_sheet', BALANCE_SHEET_CACHE_FILE),
                ('cash_flow', CASH_FLOW_CACHE_FILE),
                ('ratios', FINANCIAL_RATIOS_CACHE_FILE)
            ]:
                file_path = os.path.join(cache_dir, cache_file)
                statement_info = {
                    'exists': os.path.exists(file_path),
                    'size_bytes': 0,
                    'last_modified': None,
                    'is_expired': True
                }
                
                if statement_info['exists']:
                    stat = os.stat(file_path)
                    statement_info['size_bytes'] = stat.st_size
                    statement_info['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    info['total_size_bytes'] += statement_info['size_bytes']
                    
                    # Update overall last modified
                    if info['last_modified'] is None or statement_info['last_modified'] > info['last_modified']:
                        info['last_modified'] = statement_info['last_modified']
                    
                    # Load minimal metadata
                    try:
                        statement_data = safe_json_read(file_path)
                        if statement_data and 'metadata' in statement_data:
                            metadata = statement_data['metadata']
                            info['version'] = metadata.get('version')
                            statement_info['is_expired'] = _is_cache_expired(statement_data)
                    except Exception as e:
                        logger.warning(f"Could not load statement metadata: {e}")
                
                info['statements'][statement_type] = statement_info
            
            # Overall cache is not expired if any statement is not expired
            info['is_expired'] = all(stmt['is_expired'] for stmt in info['statements'].values() if stmt['exists'])
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting cache info for {symbol}: {e}")
        return {'error': str(e), 'symbol': symbol}


def validate_cache_integrity(symbol: str, cache_dir: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate the integrity of the financial data cache.
    
    Args:
        symbol: Stock ticker symbol
        cache_dir: Optional custom cache directory path
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    try:
        if cache_dir is None:
            cache_dir = get_default_cache_dir(symbol)
        
        issues = []
        
        # Check directory existence
        if not os.path.exists(cache_dir):
            issues.append(f"Cache directory does not exist: {cache_dir}")
            return False, issues
        
        # Check each financial statement file
        for statement_type, cache_file in [
            ('income_statement', INCOME_STATEMENT_CACHE_FILE),
            ('balance_sheet', BALANCE_SHEET_CACHE_FILE),
            ('cash_flow', CASH_FLOW_CACHE_FILE),
            ('ratios', FINANCIAL_RATIOS_CACHE_FILE)
        ]:
            file_path = os.path.join(cache_dir, cache_file)
            
            if not os.path.exists(file_path):
                issues.append(f"Missing {statement_type} cache file: {cache_file}")
                continue
            
            # Check file size
            if os.path.getsize(file_path) == 0:
                issues.append(f"Empty {statement_type} cache file: {cache_file}")
                continue
            
            # Load and validate structure
            statement_data = safe_json_read(file_path)
            if not statement_data:
                issues.append(f"Invalid JSON in {statement_type} cache file: {cache_file}")
                continue
            
            # Validate statement structure
            if not _validate_financial_statement_structure(statement_data, statement_type):
                issues.append(f"Invalid structure in {statement_type} cache file: {cache_file}")
            
            # Validate content consistency
            content_issues = _validate_statement_content(statement_data, statement_type)
            issues.extend(content_issues)
        
        is_valid = len(issues) == 0
        return is_valid, issues
        
    except Exception as e:
        logger.error(f"Error validating cache integrity for {symbol}: {e}")
        return False, [f"Validation error: {e}"]


def get_default_cache_dir(symbol: str) -> str:
    """Get the default cache directory path for a symbol."""
    config = get_config()
    base_cache_dir = config.get('cache_directory', 'altman_zscore/cache')
    return os.path.join(base_cache_dir, 'financial_data', symbol.upper())


def _add_storage_metadata(data: Dict[str, Any], symbol: str, statement_type: str) -> Dict[str, Any]:
    """Add metadata when storing financial statement cache."""
    enhanced = data.copy()
    
    # Add/update storage metadata
    if 'metadata' not in enhanced:
        enhanced['metadata'] = {}
        
    metadata = enhanced['metadata']
    metadata['symbol'] = symbol
    metadata['statement_type'] = statement_type
    metadata['last_updated'] = datetime.utcnow().isoformat()
    metadata['version'] = CURRENT_CACHE_VERSION
    metadata['cached_by'] = 'altman_zscore_fmp_cache'
    
    # Add data integrity hash
    content_hash = _calculate_content_hash(enhanced)
    metadata['content_hash'] = content_hash
    
    # Add data statistics
    if isinstance(data, list) and len(data) > 0:
        metadata['data_periods'] = len(data)
        metadata['latest_period'] = data[0].get('date', 'unknown') if data else None
        metadata['oldest_period'] = data[-1].get('date', 'unknown') if data else None
    
    return enhanced


def _store_financial_metadata(
    cache_dir: str, 
    symbol: str, 
    financial_data: Dict[str, Any], 
    success_count: int, 
    total_files: int
) -> None:
    """Store financial data metadata summary."""
    try:
        metadata_path = os.path.join(cache_dir, FINANCIAL_METADATA_FILE)
        
        metadata = {
            'symbol': symbol,
            'cache_dir': cache_dir,
            'stored_at': datetime.utcnow().isoformat(),
            'version': CURRENT_CACHE_VERSION,
            'statements_stored': success_count,
            'statements_total': total_files,
            'statements_available': list(financial_data.keys()),
            'cache_complete': success_count == total_files,
            'total_cache_size_bytes': sum(
                os.path.getsize(os.path.join(cache_dir, f))
                for f in [INCOME_STATEMENT_CACHE_FILE, BALANCE_SHEET_CACHE_FILE, 
                         CASH_FLOW_CACHE_FILE, FINANCIAL_RATIOS_CACHE_FILE]
                if os.path.exists(os.path.join(cache_dir, f))
            )
        }
        
        safe_json_write(metadata_path, metadata)
        
    except Exception as e:
        logger.warning(f"Failed to store financial metadata for {symbol}: {e}")


def _validate_financial_statement_structure(data: Dict[str, Any], statement_type: str) -> bool:
    """Validate the structure of financial statement data."""
    try:
        # Check if it's wrapped in metadata structure or direct FMP data
        if 'metadata' in data and isinstance(data.get('data'), list):
            # Wrapped structure - check the actual data
            financial_data = data['data']
        elif isinstance(data, list):
            # Direct FMP data structure
            financial_data = data
        else:
            logger.warning(f"Unexpected data structure for {statement_type}")
            return False
        
        if not isinstance(financial_data, list) or len(financial_data) == 0:
            logger.warning(f"Empty or invalid financial data for {statement_type}")
            return False
        
        # Check first item has expected fields
        first_item = financial_data[0]
        if not isinstance(first_item, dict):
            return False
        
        # Basic required fields for any financial statement
        required_fields = ['date', 'symbol']
        
        # Statement-specific required fields
        if statement_type == 'income_statement':
            required_fields.extend(['revenue', 'netIncome'])
        elif statement_type == 'balance_sheet':
            required_fields.extend(['totalAssets', 'totalLiabilities'])
        elif statement_type == 'cash_flow':
            required_fields.extend(['operatingCashFlow'])
        elif statement_type == 'ratios':
            required_fields.extend(['currentRatio', 'returnOnAssets'])
        
        # Check required fields exist
        missing_fields = [field for field in required_fields if field not in first_item]
        if missing_fields:
            logger.warning(f"Missing required fields in {statement_type}: {missing_fields}")
            return False
        
        return True
        
    except Exception as e:
        logger.warning(f"Error validating {statement_type} structure: {e}")
        return False


def _validate_statement_content(data: Dict[str, Any], statement_type: str) -> List[str]:
    """Validate the content consistency of financial statement data."""
    issues = []
    
    try:
        # Get actual financial data
        if 'metadata' in data and isinstance(data.get('data'), list):
            financial_data = data['data']
        elif isinstance(data, list):
            financial_data = data
        else:
            return [f"Invalid data structure for {statement_type}"]
        
        if not financial_data:
            return [f"No financial data found for {statement_type}"]
        
        # Check data consistency across periods
        symbols = set()
        dates = []
        
        for item in financial_data:
            if not isinstance(item, dict):
                issues.append(f"Invalid item structure in {statement_type}")
                continue
            
            symbol = item.get('symbol')
            date = item.get('date')
            
            if symbol:
                symbols.add(symbol)
            if date:
                dates.append(date)
        
        # Check symbol consistency
        if len(symbols) > 1:
            issues.append(f"Multiple symbols in {statement_type}: {symbols}")
        
        # Check date ordering (should be newest first)
        if len(dates) > 1:
            try:
                sorted_dates = sorted(dates, reverse=True)
                if dates != sorted_dates:
                    issues.append(f"Dates not in descending order in {statement_type}")
            except Exception:
                issues.append(f"Invalid date format in {statement_type}")
        
        # Statement-specific validations
        if statement_type == 'balance_sheet':
            for item in financial_data:
                total_assets = item.get('totalAssets', 0)
                total_liab = item.get('totalLiabilities', 0)
                total_equity = item.get('totalStockholdersEquity', 0)
                
                # Basic accounting equation check (with tolerance for rounding)
                if total_assets and total_liab and total_equity:
                    balance = abs(total_assets - (total_liab + total_equity))
                    if balance / total_assets > 0.01:  # 1% tolerance
                        issues.append(f"Balance sheet equation doesn't balance for {item.get('date')}")
        
    except Exception as e:
        issues.append(f"Content validation error for {statement_type}: {e}")
    
    return issues


def _is_cache_expired(data: Dict[str, Any]) -> bool:
    """Check if financial data cache has expired based on TTL."""
    try:
        # Check metadata in wrapped structure
        if 'metadata' in data:
            metadata = data['metadata']
        else:
            # For direct FMP data, check if we have a date field to determine freshness
            if isinstance(data, list) and len(data) > 0 and 'date' in data[0]:
                # Use the latest data date to determine if cache is stale
                latest_date_str = data[0]['date']
                try:
                    latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
                    # Consider cache expired if data is more than 30 days old
                    # (since financial statements are typically quarterly)
                    days_old = (datetime.now() - latest_date).days
                    return days_old > 30
                except Exception:
                    return True
            return True  # No date info, consider expired
        
        last_updated_str = metadata.get('last_updated') or metadata.get('cached_at')
        
        if not last_updated_str:
            return True  # No timestamp, consider expired
            
        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
        ttl_hours = get_config().get('cache_ttl_hours', DEFAULT_CACHE_TTL_HOURS)
        expiry_time = last_updated + timedelta(hours=ttl_hours)
        
        return datetime.utcnow() > expiry_time
        
    except Exception as e:
        logger.warning(f"Error checking cache expiry: {e}")
        return True  # If we can't determine, consider expired


def _calculate_content_hash(data: Dict[str, Any]) -> str:
    """Calculate hash of financial data content for integrity checking."""
    try:
        # Create a copy without metadata for hashing
        content = data.copy()
        content.pop('metadata', None)
        
        # Convert to JSON string for consistent hashing
        content_str = json.dumps(content, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        
    except Exception as e:
        logger.warning(f"Error calculating content hash: {e}")
        return "unknown"
