"""
Validation framework for the Altman Z-Score package.

This module provides:
- Reusable validation functions for common data types
- Financial data validation (ranges, types, consistency)
- Date validation and parsing utilities
- Company identifier validation (ticker, CIK)
"""

import re
import math
from datetime import datetime, date
from typing import Any, List, Optional, Union, Dict, Tuple
from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError
from .logging_config import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
    
    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid
    
    def __str__(self) -> str:
        """String representation of validation result."""
        if self.is_valid:
            result = "Valid"
            if self.warnings:
                result += f" (with {len(self.warnings)} warnings)"
        else:
            result = f"Invalid ({len(self.errors)} errors"
            if self.warnings:
                result += f", {len(self.warnings)} warnings"
            result += ")"
        return result


class FinancialDataValidator:
    """Validator for financial data and Z-Score components."""
    
    # Reasonable ranges for financial values (in millions)
    REASONABLE_RANGES = {
        "total_assets": (0.1, 10_000_000),      # $100K to $10T
        "current_assets": (0, 10_000_000),      # $0 to $10T
        "current_liabilities": (0, 10_000_000), # $0 to $10T
        "total_liabilities": (0, 10_000_000),   # $0 to $10T
        "retained_earnings": (-1_000_000, 10_000_000),  # Can be negative
        "ebit": (-1_000_000, 1_000_000),        # Can be negative
        "sales": (0, 10_000_000),               # $0 to $10T
        "market_value_equity": (0.1, 50_000_000),  # $100K to $50T
        "book_value_equity": (-1_000_000, 10_000_000),  # Can be negative
    }
    
    @staticmethod
    def validate_financial_value(value: Any, 
                                field_name: str,
                                allow_negative: bool = False,
                                allow_zero: bool = True) -> ValidationResult:
        """
        Validate a single financial value.
        
        Args:
            value: Value to validate
            field_name: Name of the field being validated
            allow_negative: Whether negative values are allowed
            allow_zero: Whether zero values are allowed
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        # Check if value is None
        if value is None:
            result.add_error(f"{field_name} cannot be None")
            return result
        
        # Try to convert to float
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            result.add_error(f"{field_name} must be a valid number, got {type(value).__name__}")
            return result
        
        # Check for NaN or infinity
        if math.isnan(float_value):
            result.add_error(f"{field_name} cannot be NaN")
            return result
        
        if math.isinf(float_value):
            result.add_error(f"{field_name} cannot be infinite")
            return result
        
        # Check sign constraints
        if not allow_negative and float_value < 0:
            result.add_error(f"{field_name} cannot be negative, got {float_value}")
        
        if not allow_zero and float_value == 0:
            result.add_error(f"{field_name} cannot be zero")
        
        # Check reasonable ranges
        if field_name in FinancialDataValidator.REASONABLE_RANGES:
            min_val, max_val = FinancialDataValidator.REASONABLE_RANGES[field_name]
            if float_value < min_val or float_value > max_val:
                result.add_warning(
                    f"{field_name} value {float_value:,.0f} is outside reasonable range "
                    f"[{min_val:,.0f}, {max_val:,.0f}]"
                )
        
        return result
    
    @staticmethod
    def validate_quarter_data(quarter_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a complete quarter's financial data.
        
        Args:
            quarter_data: Dictionary containing quarter financial data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        # Required fields for Z-Score calculation
        required_fields = [
            "total_assets", "current_assets", "current_liabilities",
            "total_liabilities", "retained_earnings", "ebit", "sales"
        ]
        
        # Check for required fields
        for field in required_fields:
            if field not in quarter_data:
                result.add_error(f"Required field '{field}' is missing")
                continue
            
            # Validate individual field
            allow_negative = field in ["retained_earnings", "ebit", "book_value_equity"]
            allow_zero = field not in ["total_assets", "sales"]  # These should not be zero
            
            field_result = FinancialDataValidator.validate_financial_value(
                quarter_data[field], field, allow_negative, allow_zero
            )
            result.merge(field_result)
        
        # Logical consistency checks
        if result.is_valid:
            result.merge(FinancialDataValidator._validate_balance_sheet_consistency(quarter_data))
            result.merge(FinancialDataValidator._validate_ratio_consistency(quarter_data))
        
        return result
    
    @staticmethod
    def _validate_balance_sheet_consistency(data: Dict[str, Any]) -> ValidationResult:
        """Validate balance sheet logical consistency."""
        result = ValidationResult()
        
        try:
            # Current assets should not exceed total assets
            if data.get("current_assets", 0) > data.get("total_assets", 0):
                result.add_warning("Current assets exceed total assets")
            
            # Current liabilities should not exceed total liabilities
            if data.get("current_liabilities", 0) > data.get("total_liabilities", 0):
                result.add_warning("Current liabilities exceed total liabilities")
            
            # Book value of equity should roughly equal assets - liabilities
            if "book_value_equity" in data:
                calculated_equity = data.get("total_assets", 0) - data.get("total_liabilities", 0)
                reported_equity = data.get("book_value_equity", 0)
                
                if abs(calculated_equity - reported_equity) > (abs(calculated_equity) * 0.1):
                    result.add_warning(
                        f"Book value of equity ({reported_equity:,.0f}) differs significantly "
                        f"from calculated value ({calculated_equity:,.0f})"
                    )
        
        except (TypeError, ValueError) as e:
            result.add_error(f"Error in balance sheet validation: {e}")
        
        return result
    
    @staticmethod
    def _validate_ratio_consistency(data: Dict[str, Any]) -> ValidationResult:
        """Validate financial ratio consistency."""
        result = ValidationResult()
        
        try:
            # Working capital should be reasonable
            working_capital = data.get("current_assets", 0) - data.get("current_liabilities", 0)
            total_assets = data.get("total_assets", 1)
            
            working_capital_ratio = working_capital / total_assets
            if working_capital_ratio < -1 or working_capital_ratio > 1:
                result.add_warning(
                    f"Working capital ratio ({working_capital_ratio:.3f}) seems extreme"
                )
            
            # Asset turnover should be reasonable (sales / total assets)
            sales = data.get("sales", 0)
            asset_turnover = sales / total_assets
            if asset_turnover > 10:  # Very high turnover
                result.add_warning(
                    f"Asset turnover ratio ({asset_turnover:.2f}) is very high"
                )
        
        except (TypeError, ValueError, ZeroDivisionError) as e:
            result.add_error(f"Error in ratio validation: {e}")
        
        return result


class CompanyValidator:
    """Validator for company identifiers and metadata."""
    
    # US ticker symbol pattern
    TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}(\.[A-Z])?$')
    
    # CIK pattern (10 digits with leading zeros)
    CIK_PATTERN = re.compile(r'^\d{10}$')
    
    @staticmethod
    def validate_ticker(ticker: str) -> ValidationResult:
        """
        Validate a stock ticker symbol.
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        if not ticker:
            result.add_error("Ticker cannot be empty")
            return result
        
        if not isinstance(ticker, str):
            result.add_error(f"Ticker must be a string, got {type(ticker).__name__}")
            return result
        
        # Convert to uppercase for validation
        ticker_upper = ticker.upper()
        
        if not CompanyValidator.TICKER_PATTERN.match(ticker_upper):
            result.add_error(
                f"Ticker '{ticker}' does not match expected pattern (1-5 letters, optional class)"
            )
        
        # Check for common invalid patterns
        if ticker_upper in ["TEST", "NULL", "NONE", "N/A"]:
            result.add_error(f"Ticker '{ticker}' appears to be a placeholder")
        
        return result
    
    @staticmethod
    def validate_cik(cik: Union[str, int]) -> ValidationResult:
        """
        Validate a CIK (Central Index Key).
        
        Args:
            cik: CIK to validate
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        if cik is None:
            result.add_error("CIK cannot be None")
            return result
        
        # Convert to string and pad with zeros
        try:
            if isinstance(cik, int):
                cik_str = f"{cik:010d}"
            else:
                cik_str = str(cik).zfill(10)
        except (ValueError, TypeError):
            result.add_error(f"CIK must be a number or numeric string, got {type(cik).__name__}")
            return result
        
        if not CompanyValidator.CIK_PATTERN.match(cik_str):
            result.add_error(f"CIK '{cik}' is not a valid 10-digit number")
        
        return result


class DateValidator:
    """Validator for dates and date ranges."""
    
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    @staticmethod
    def validate_date(date_value: Any, field_name: str = "date") -> ValidationResult:
        """
        Validate a date value.
        
        Args:
            date_value: Date to validate
            field_name: Name of the field being validated
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        if date_value is None:
            result.add_error(f"{field_name} cannot be None")
            return result
        
        # If already a date object, validate range
        if isinstance(date_value, (date, datetime)):
            return DateValidator._validate_date_range(date_value, field_name)
        
        # Try to parse string date
        if isinstance(date_value, str):
            parsed_date = None
            for fmt in DateValidator.DATE_FORMATS:
                try:
                    parsed_date = datetime.strptime(date_value, fmt).date()
                    break
                except ValueError:
                    continue
            
            if parsed_date is None:
                result.add_error(f"{field_name} '{date_value}' is not a valid date format")
                return result
            
            return DateValidator._validate_date_range(parsed_date, field_name)
        
        result.add_error(f"{field_name} must be a date, datetime, or date string")
        return result
    
    @staticmethod
    def _validate_date_range(date_obj: Union[date, datetime], field_name: str) -> ValidationResult:
        """Validate that a date is within reasonable range."""
        result = ValidationResult()
        
        # Convert datetime to date if needed
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        # Check reasonable range (1900 to 10 years in the future)
        min_date = date(1900, 1, 1)
        max_date = date.today().replace(year=date.today().year + 10)
        
        if date_obj < min_date:
            result.add_error(f"{field_name} {date_obj} is too far in the past")
        elif date_obj > max_date:
            result.add_error(f"{field_name} {date_obj} is too far in the future")
        
        return result
    
    @staticmethod
    def validate_date_range(start_date: Any, end_date: Any) -> ValidationResult:
        """
        Validate a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        
        # Validate individual dates
        start_result = DateValidator.validate_date(start_date, "start_date")
        end_result = DateValidator.validate_date(end_date, "end_date")
        
        result.merge(start_result)
        result.merge(end_result)
        
        # If both dates are valid, check order
        if start_result.is_valid and end_result.is_valid:
            # Parse dates for comparison
            start_parsed = DateValidator._parse_date_safe(start_date)
            end_parsed = DateValidator._parse_date_safe(end_date)
            
            if start_parsed and end_parsed and start_parsed > end_parsed:
                result.add_error("Start date must be before or equal to end date")
        
        return result
    
    @staticmethod
    def _parse_date_safe(date_value: Any) -> Optional[date]:
        """Safely parse a date value."""
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            for fmt in DateValidator.DATE_FORMATS:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        return None


# Convenience functions for common validations
def validate_financial_quarter(quarter_data: Dict[str, Any]) -> ValidationResult:
    """Validate a complete financial quarter."""
    return FinancialDataValidator.validate_quarter_data(quarter_data)


def validate_ticker_symbol(ticker: str) -> ValidationResult:
    """Validate a ticker symbol."""
    return CompanyValidator.validate_ticker(ticker)


def validate_cik_number(cik: Union[str, int]) -> ValidationResult:
    """Validate a CIK number."""
    return CompanyValidator.validate_cik(cik)


def validate_analysis_date_range(start_date: Any, end_date: Any = None) -> ValidationResult:
    """Validate date range for analysis."""
    if end_date is None:
        end_date = date.today()
    return DateValidator.validate_date_range(start_date, end_date)


# Example usage and testing
if __name__ == "__main__":
    # Test financial data validation
    test_quarter = {
        "total_assets": 100000,
        "current_assets": 30000,
        "current_liabilities": 20000,
        "total_liabilities": 60000,
        "retained_earnings": 15000,
        "ebit": 8000,
        "sales": 50000,
        "book_value_equity": 40000
    }
    
    result = validate_financial_quarter(test_quarter)
    print(f"Financial data validation: {result}")
    if result.errors:
        print("Errors:", result.errors)
    if result.warnings:
        print("Warnings:", result.warnings)
    
    # Test ticker validation
    tickers = ["AAPL", "GOOGL", "BRK.A", "invalid", "TEST"]
    for ticker in tickers:
        result = validate_ticker_symbol(ticker)
        print(f"Ticker '{ticker}': {result}")
    
    # Test date validation
    dates = ["2023-01-01", "01/01/2023", "invalid", "2050-01-01"]
    for date_str in dates:
        result = DateValidator.validate_date(date_str)
        print(f"Date '{date_str}': {result}")
