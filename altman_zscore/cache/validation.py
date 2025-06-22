"""
Validation - FMP Financial Data Cache Layer

This module provides validation functions for FMP financial data integrity 
and completeness verification.

Key Features:
- Financial data validation
- Data structure integrity checks  
- Content consistency validation
- Error reporting with detailed diagnostics

Usage:
    from altman_zscore.cache.validation import validate_financial_data
    
    result = validate_financial_data(financial_data)
    if result.is_valid:
        print("Financial data is valid")
    else:
        print(f"Validation errors: {result.errors}")
"""

from typing import Dict, List, Set, Any, Optional, NamedTuple
from dataclasses import dataclass
from collections import Counter
from datetime import datetime

# Import shared infrastructure
from ..common.logging_config import get_logger
from ..common.validators import validate_ticker_symbol

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of field mapping validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    coverage_stats: Dict[str, Any]
    
    def __post_init__(self):
        """Ensure lists are not None."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.coverage_stats is None:
            self.coverage_stats = {}


class CoverageStats(NamedTuple):
    """Statistics about field mapping coverage."""
    total_canonical_fields: int
    mapped_canonical_fields: int
    coverage_percentage: float
    total_companies: int
    total_sec_fields: int
    avg_fields_per_company: float


def validate_field_mappings(cache_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate field mapping cache data for integrity and completeness.
    
    Args:
        cache_data: Field mapping cache data to validate
        
    Returns:
        ValidationResult with validation status and detailed feedback
    """
    logger.info("Validating field mappings")
    
    errors = []
    warnings = []
    coverage_stats = {}
    
    try:
        # Validate basic structure
        structure_errors = _validate_structure(cache_data)
        errors.extend(structure_errors)
        
        # Validate metadata
        metadata_errors = _validate_metadata(cache_data)
        errors.extend(metadata_errors)
        
        # Validate field mappings
        mapping_errors, mapping_warnings = _validate_mappings(cache_data)
        errors.extend(mapping_errors)
        warnings.extend(mapping_warnings)
        
        # Validate data consistency
        consistency_errors = _validate_consistency(cache_data)
        errors.extend(consistency_errors)
        
        # Calculate coverage statistics
        coverage_stats = _calculate_coverage_stats(cache_data)
        
        # Add coverage warnings
        coverage_warnings = _generate_coverage_warnings(coverage_stats)
        warnings.extend(coverage_warnings)
        
        is_valid = len(errors) == 0
        
        logger.info(f"Validation complete: {'PASSED' if is_valid else 'FAILED'} "
                   f"({len(errors)} errors, {len(warnings)} warnings)")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            coverage_stats=coverage_stats
        )
        
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        return ValidationResult(
            is_valid=False,
            errors=[f"Validation exception: {e}"],
            warnings=[],
            coverage_stats={}
        )


def _validate_structure(cache_data: Dict[str, Any]) -> List[str]:
    """Validate the basic structure of cache data."""
    errors = []
    
    required_keys = [
        'canonical_to_sec_mappings',
        'company_mappings',
        'field_frequency',
        'all_sec_fields',
        'metadata'
    ]
    
    for key in required_keys:
        if key not in cache_data:
            errors.append(f"Missing required key: {key}")
        elif not isinstance(cache_data[key], (dict, list)):
            errors.append(f"Invalid type for {key}: expected dict or list")
    
    return errors


def _validate_metadata(cache_data: Dict[str, Any]) -> List[str]:
    """Validate metadata section."""
    errors = []
    
    if 'metadata' not in cache_data:
        return ["Missing metadata section"]
    
    metadata = cache_data['metadata']
    
    required_metadata = [
        'version',
        'created_at',
        'companies_analyzed',
        'total_companies',
        'mapping_method'
    ]
    
    for key in required_metadata:
        if key not in metadata:
            errors.append(f"Missing metadata key: {key}")
    
    # Validate version format
    version = metadata.get('version')
    if version and not isinstance(version, str):
        errors.append("Version must be a string")
      # Validate companies_analyzed
    companies = metadata.get('companies_analyzed', [])
    if not isinstance(companies, list):
        errors.append("companies_analyzed must be a list")
    else:
        invalid_tickers = []
        for ticker in companies:
            ticker_result = validate_ticker_symbol(ticker)
            if not ticker_result.is_valid:
                invalid_tickers.append(ticker)
        if invalid_tickers:
            errors.append(f"Invalid ticker symbols: {invalid_tickers}")
    
    # Validate counts
    total_companies = metadata.get('total_companies', 0)
    if not isinstance(total_companies, int) or total_companies < 0:
        errors.append("total_companies must be a non-negative integer")
    
    return errors


def _validate_mappings(cache_data: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """Validate field mappings for correctness."""
    errors = []
    warnings = []
    
    canonical_mappings = cache_data.get('canonical_to_sec_mappings', {})
    company_mappings = cache_data.get('company_mappings', {})
    
    # Validate canonical mappings structure
    for canonical_field, sec_fields in canonical_mappings.items():
        if not isinstance(sec_fields, list):
            errors.append(f"SEC fields for {canonical_field} must be a list")
            continue
        
        if len(sec_fields) == 0:
            warnings.append(f"No SEC fields mapped for canonical field: {canonical_field}")
        
        # Check for duplicates
        if len(sec_fields) != len(set(sec_fields)):
            duplicates = [f for f in sec_fields if sec_fields.count(f) > 1]
            warnings.append(f"Duplicate SEC fields in {canonical_field}: {duplicates}")
    
    # Validate company mappings structure
    for company, mappings in company_mappings.items():
        if not isinstance(mappings, dict):
            errors.append(f"Mappings for {company} must be a dictionary")
            continue
        
        for canonical_field, sec_fields in mappings.items():
            if not isinstance(sec_fields, list):
                errors.append(f"SEC fields for {company}.{canonical_field} must be a list")
            elif len(sec_fields) == 0:
                warnings.append(f"No SEC fields mapped for {company}.{canonical_field}")
    
    return errors, warnings


def _validate_consistency(cache_data: Dict[str, Any]) -> List[str]:
    """Validate data consistency across different sections."""
    errors = []
    
    try:
        canonical_mappings = cache_data.get('canonical_to_sec_mappings', {})
        company_mappings = cache_data.get('company_mappings', {})
        field_frequency = cache_data.get('field_frequency', {})
        all_sec_fields = set(cache_data.get('all_sec_fields', []))
        metadata = cache_data.get('metadata', {})
        
        # Check company count consistency
        companies_analyzed = set(metadata.get('companies_analyzed', []))
        companies_in_mappings = set(company_mappings.keys())
        
        if companies_analyzed != companies_in_mappings:
            missing_from_metadata = companies_in_mappings - companies_analyzed
            missing_from_mappings = companies_analyzed - companies_in_mappings
            
            if missing_from_metadata:
                errors.append(f"Companies in mappings but not in metadata: {missing_from_metadata}")
            if missing_from_mappings:
                errors.append(f"Companies in metadata but not in mappings: {missing_from_mappings}")
        
        # Check field frequency consistency
        frequency_fields = set(field_frequency.keys())
        if not frequency_fields.issubset(all_sec_fields):
            missing = frequency_fields - all_sec_fields
            errors.append(f"Field frequency contains fields not in all_sec_fields: {missing}")
        
        # Check canonical mappings consistency
        all_mapped_fields = set()
        for sec_fields in canonical_mappings.values():
            all_mapped_fields.update(sec_fields)
        
        if not all_mapped_fields.issubset(all_sec_fields):
            missing = all_mapped_fields - all_sec_fields
            errors.append(f"Canonical mappings contain fields not in all_sec_fields: {missing}")
        
        # Check company mappings consistency
        company_mapped_fields = set()
        for company_data in company_mappings.values():
            for sec_fields in company_data.values():
                company_mapped_fields.update(sec_fields)
        
        if not company_mapped_fields.issubset(all_sec_fields):
            missing = company_mapped_fields - all_sec_fields
            errors.append(f"Company mappings contain fields not in all_sec_fields: {missing}")
        
    except Exception as e:
        errors.append(f"Consistency validation error: {e}")
    
    return errors


def _calculate_coverage_stats(cache_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate coverage statistics for the field mappings."""
    try:
        canonical_mappings = cache_data.get('canonical_to_sec_mappings', {})
        company_mappings = cache_data.get('company_mappings', {})
        all_sec_fields = cache_data.get('all_sec_fields', [])
        metadata = cache_data.get('metadata', {})
        
        # Basic counts
        total_canonical_fields = len(canonical_mappings)
        mapped_canonical_fields = len([f for f, sec_fields in canonical_mappings.items() if sec_fields])
        total_companies = len(company_mappings)
        total_sec_fields = len(all_sec_fields)
        
        # Calculate coverage percentage
        coverage_percentage = (mapped_canonical_fields / max(total_canonical_fields, 1)) * 100
        
        # Calculate average fields per company
        total_company_fields = sum(
            len(mappings) for mappings in company_mappings.values()
        )
        avg_fields_per_company = total_company_fields / max(total_companies, 1)
        
        # Field frequency stats
        field_frequency = cache_data.get('field_frequency', {})
        most_common_fields = Counter(field_frequency).most_common(10)
        
        # Canonical field coverage
        canonical_coverage = {}
        for canonical_field, sec_fields in canonical_mappings.items():
            companies_with_field = sum(
                1 for company_data in company_mappings.values()
                if canonical_field in company_data and company_data[canonical_field]
            )
            canonical_coverage[canonical_field] = {
                'sec_fields_count': len(sec_fields),
                'companies_with_field': companies_with_field,
                'company_coverage_percentage': (companies_with_field / max(total_companies, 1)) * 100
            }
        
        return {
            'total_canonical_fields': total_canonical_fields,
            'mapped_canonical_fields': mapped_canonical_fields,
            'coverage_percentage': round(coverage_percentage, 2),
            'total_companies': total_companies,
            'total_sec_fields': total_sec_fields,
            'avg_fields_per_company': round(avg_fields_per_company, 2),
            'most_common_fields': most_common_fields,
            'canonical_coverage': canonical_coverage,
            'metadata': {
                'cache_version': metadata.get('version'),
                'created_at': metadata.get('created_at'),
                'mapping_method': metadata.get('mapping_method')
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating coverage stats: {e}")
        return {'error': str(e)}


def _generate_coverage_warnings(coverage_stats: Dict[str, Any]) -> List[str]:
    """Generate warnings based on coverage statistics."""
    warnings = []
    
    try:
        coverage_percentage = coverage_stats.get('coverage_percentage', 0)
        if coverage_percentage < 50:
            warnings.append(f"Low canonical field coverage: {coverage_percentage}%")
        
        total_companies = coverage_stats.get('total_companies', 0)
        if total_companies < 10:
            warnings.append(f"Small sample size: only {total_companies} companies analyzed")
        
        canonical_coverage = coverage_stats.get('canonical_coverage', {})
        for canonical_field, stats in canonical_coverage.items():
            company_coverage = stats.get('company_coverage_percentage', 0)
            if company_coverage < 25:
                warnings.append(f"Low company coverage for {canonical_field}: {company_coverage}%")
        
    except Exception as e:
        logger.warning(f"Error generating coverage warnings: {e}")
    
    return warnings


def get_cache_validation_summary(cache_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of cache validation results.
    
    Args:
        cache_data: Field mapping cache data
        
    Returns:
        Dict containing validation summary
    """
    result = validate_field_mappings(cache_data)
    
    return {
        'is_valid': result.is_valid,
        'error_count': len(result.errors),
        'warning_count': len(result.warnings),
        'coverage_percentage': result.coverage_stats.get('coverage_percentage', 0),
        'total_companies': result.coverage_stats.get('total_companies', 0),
        'total_fields': result.coverage_stats.get('total_sec_fields', 0),
        'first_error': result.errors[0] if result.errors else None,
        'first_warning': result.warnings[0] if result.warnings else None
    }


def validate_financial_data(financial_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate FMP financial data structure and content.
    
    Args:
        financial_data: Dict containing financial statements data
                       Expected keys: income_statement, balance_sheet, cash_flow, ratios
    
    Returns:
        ValidationResult with validation status and detailed diagnostics
    """
    errors = []
    warnings = []
    coverage_stats = {}
    
    try:
        logger.debug("Starting financial data validation")
        
        # Check expected statement types
        expected_statements = ['income_statement', 'balance_sheet', 'cash_flow', 'ratios']
        available_statements = list(financial_data.keys())
        
        missing_statements = [stmt for stmt in expected_statements if stmt not in available_statements]
        if missing_statements:
            warnings.append(f"Missing financial statements: {missing_statements}")
        
        # Track validation stats
        total_statements = len(available_statements)
        valid_statements = 0
        total_periods = 0
        
        # Validate each available statement
        for statement_type, statement_data in financial_data.items():
            statement_errors = _validate_statement_data(statement_type, statement_data)
            errors.extend(statement_errors)
            
            if not statement_errors:
                valid_statements += 1
            
            # Count periods in this statement
            if isinstance(statement_data, list):
                total_periods += len(statement_data)
            elif isinstance(statement_data, dict) and 'data' in statement_data:
                if isinstance(statement_data['data'], list):
                    total_periods += len(statement_data['data'])
        
        # Cross-validate between statements
        cross_validation_errors = _cross_validate_statements(financial_data)
        errors.extend(cross_validation_errors)
        
        # Generate coverage statistics
        coverage_stats = {
            'total_statements': total_statements,
            'valid_statements': valid_statements,
            'statement_coverage_percentage': (valid_statements / max(total_statements, 1)) * 100,
            'total_periods': total_periods,
            'available_statements': available_statements,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Financial data validation passed")
        else:
            logger.warning(f"Financial data validation failed with {len(errors)} errors")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            coverage_stats=coverage_stats
        )
        
    except Exception as e:
        error_msg = f"Financial data validation error: {e}"
        logger.error(error_msg)
        return ValidationResult(
            is_valid=False,
            errors=[error_msg],
            warnings=warnings,
            coverage_stats=coverage_stats
        )


def _validate_statement_data(statement_type: str, statement_data: Any) -> List[str]:
    """Validate individual financial statement data."""
    errors = []
    
    try:
        # Handle both wrapped (with metadata) and direct data structures
        if isinstance(statement_data, dict) and 'data' in statement_data:
            # Wrapped structure
            data_array = statement_data['data']
        elif isinstance(statement_data, list):
            # Direct array structure
            data_array = statement_data
        else:
            return [f"{statement_type}: Invalid data structure, expected list or dict with 'data' key"]
        
        if not isinstance(data_array, list):
            return [f"{statement_type}: Data is not a list"]
        
        if len(data_array) == 0:
            return [f"{statement_type}: No data periods available"]
        
        # Validate each period
        for i, period_data in enumerate(data_array):
            if not isinstance(period_data, dict):
                errors.append(f"{statement_type}: Period {i} is not a dictionary")
                continue
            
            # Check required fields
            required_fields = _get_required_fields(statement_type)
            missing_fields = [field for field in required_fields if field not in period_data]
            
            if missing_fields:
                errors.append(f"{statement_type}: Period {i} missing required fields: {missing_fields}")
            
            # Validate data types and ranges
            validation_errors = _validate_field_values(statement_type, period_data, i)
            errors.extend(validation_errors)
    
    except Exception as e:
        errors.append(f"{statement_type}: Validation error: {e}")
    
    return errors


def _get_required_fields(statement_type: str) -> List[str]:
    """Get required fields for each statement type."""
    field_requirements = {
        'income_statement': ['date', 'symbol', 'revenue', 'netIncome', 'grossProfit'],
        'balance_sheet': ['date', 'symbol', 'totalAssets', 'totalLiabilities', 'totalStockholdersEquity'],
        'cash_flow': ['date', 'symbol', 'operatingCashFlow', 'netCashProvidedByOperatingActivities'],
        'ratios': ['date', 'symbol', 'currentRatio', 'returnOnAssets', 'debtRatio']
    }
    
    return field_requirements.get(statement_type, ['date', 'symbol'])


def _validate_field_values(statement_type: str, period_data: Dict[str, Any], period_index: int) -> List[str]:
    """Validate field values for business logic consistency."""
    errors = []
    
    try:
        # Date validation
        if 'date' in period_data:
            date_str = period_data['date']
            if not isinstance(date_str, str) or len(date_str) != 10:
                errors.append(f"{statement_type}: Period {period_index} has invalid date format: {date_str}")
        
        # Symbol validation  
        if 'symbol' in period_data:
            symbol = period_data['symbol']
            if not isinstance(symbol, str) or len(symbol) < 1:
                errors.append(f"{statement_type}: Period {period_index} has invalid symbol: {symbol}")
        
        # Statement-specific validations
        if statement_type == 'balance_sheet':
            # Check balance sheet equation: Assets = Liabilities + Equity
            total_assets = period_data.get('totalAssets', 0)
            total_liab = period_data.get('totalLiabilities', 0)
            total_equity = period_data.get('totalStockholdersEquity', 0)
            
            if all(isinstance(x, (int, float)) for x in [total_assets, total_liab, total_equity]):
                if total_assets > 0:  # Only check if we have meaningful data
                    balance_diff = abs(total_assets - (total_liab + total_equity))
                    balance_percentage = balance_diff / total_assets
                    
                    if balance_percentage > 0.02:  # 2% tolerance
                        errors.append(f"{statement_type}: Period {period_index} balance sheet doesn't balance (diff: {balance_percentage:.1%})")
        
        elif statement_type == 'income_statement':
            # Basic income statement checks
            revenue = period_data.get('revenue', 0)
            gross_profit = period_data.get('grossProfit', 0)
            net_income = period_data.get('netIncome', 0)
            
            if isinstance(revenue, (int, float)) and isinstance(gross_profit, (int, float)):
                if revenue != 0 and abs(gross_profit) > abs(revenue) * 2:  # Gross profit shouldn't be much larger than revenue
                    errors.append(f"{statement_type}: Period {period_index} gross profit seems inconsistent with revenue")
        
        elif statement_type == 'ratios':
            # Validate ratio ranges
            current_ratio = period_data.get('currentRatio', 0)
            if isinstance(current_ratio, (int, float)) and current_ratio < 0:
                errors.append(f"{statement_type}: Period {period_index} has negative current ratio: {current_ratio}")
            
            debt_ratio = period_data.get('debtRatio', 0) 
            if isinstance(debt_ratio, (int, float)) and (debt_ratio < 0 or debt_ratio > 10):
                errors.append(f"{statement_type}: Period {period_index} has unusual debt ratio: {debt_ratio}")
    
    except Exception as e:
        errors.append(f"{statement_type}: Field validation error for period {period_index}: {e}")
    
    return errors


def _cross_validate_statements(financial_data: Dict[str, Any]) -> List[str]:
    """Cross-validate consistency between different financial statements."""
    errors = []
    
    try:
        # Get data arrays from each statement
        statements = {}
        for stmt_type, stmt_data in financial_data.items():
            if isinstance(stmt_data, dict) and 'data' in stmt_data:
                statements[stmt_type] = stmt_data['data']
            elif isinstance(stmt_data, list):
                statements[stmt_type] = stmt_data
        
        # Check symbol consistency across statements
        symbols_by_statement = {}
        for stmt_type, data_array in statements.items():
            if data_array and len(data_array) > 0:
                symbols = set(item.get('symbol') for item in data_array if item.get('symbol'))
                symbols_by_statement[stmt_type] = symbols
        
        if len(symbols_by_statement) > 1:
            all_symbols = set.union(*symbols_by_statement.values())
            for stmt_type, symbols in symbols_by_statement.items():
                if symbols != all_symbols:
                    errors.append(f"Symbol inconsistency in {stmt_type}: {symbols} vs expected {all_symbols}")
        
        # Check date consistency (same periods across statements)
        dates_by_statement = {}
        for stmt_type, data_array in statements.items():
            if data_array and len(data_array) > 0:
                dates = [item.get('date') for item in data_array if item.get('date')]
                dates_by_statement[stmt_type] = set(dates)
        
        if len(dates_by_statement) > 1:
            all_dates = set.union(*dates_by_statement.values())
            for stmt_type, dates in dates_by_statement.items():
                missing_dates = all_dates - dates
                if missing_dates:
                    errors.append(f"Missing periods in {stmt_type}: {missing_dates}")
    
    except Exception as e:
        errors.append(f"Cross-validation error: {e}")
    
    return errors
