"""Test script for monthly price statistics functionality."""
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(project_root, 'src'))

from altman_zscore.data_fetching.prices import get_monthly_price_stats
import pandas as pd

def test_monthly_stats():
    """Test the get_monthly_price_stats function with a known stable stock."""    # Test with MSFT data for a stable period
    start_date = "2024-01-01"
    end_date = "2025-05-29"  # Updated to current date
    ticker = "MSFT"
    
    try:
        stats = get_monthly_price_stats(ticker, start_date, end_date)
        
        # Basic validation
        print("\nValidating monthly statistics for", ticker)
        print("-" * 50)
        
        # Check DataFrame structure
        expected_columns = {'month', 'avg_price', 'min_price', 'max_price', 'days_with_data'}
        actual_columns = set(stats.columns)
        assert expected_columns == actual_columns, f"Unexpected columns: {actual_columns}"
        print("✓ Column structure is correct")
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(stats['month']), "month should be datetime"
        assert all(pd.api.types.is_float_dtype(stats[col]) for col in ['avg_price', 'min_price', 'max_price']), \
            "Price columns should be float"
        assert pd.api.types.is_integer_dtype(stats['days_with_data']), "days_with_data should be integer"
        print("✓ Data types are correct")
        
        # Logical validation
        assert (stats['max_price'] >= stats['avg_price']).all(), "Max price should be >= average"
        assert (stats['min_price'] <= stats['avg_price']).all(), "Min price should be <= average"
        assert (stats['days_with_data'] > 0).all(), "Should have at least one day of data per month"
        print("✓ Price relationships are valid")
        
        # Display results
        print("\nMonthly statistics:")
        print(stats.to_string(index=False))
        print("\nAll tests passed!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

def test_error_cases():
    """Test error handling in monthly stats calculation."""
    print("\nTesting error cases")
    print("-" * 50)
    
    # Test invalid date range
    try:
        get_monthly_price_stats("MSFT", "2024-05-28", "2024-01-01")
        assert False, "Should raise error for end_date before start_date"
    except ValueError as e:
        print("✓ Correctly handled invalid date range")
    
    # Test invalid ticker
    try:
        get_monthly_price_stats("INVALID123", "2024-01-01", "2024-05-28")
        assert False, "Should raise error for invalid ticker"
    except Exception as e:
        print("✓ Correctly handled invalid ticker")

if __name__ == "__main__":
    test_monthly_stats()
    test_error_cases()
