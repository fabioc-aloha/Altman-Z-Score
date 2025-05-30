"""
Test script for the company status detection functionality.
This script tests detection of bankrupt, delisted, or non-existent companies.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.altman_zscore.company_status import check_company_status, handle_special_status

def test_company_status(ticker):
    """Test the company status detection for a ticker."""
    print(f"\n=== Testing status detection for {ticker} ===")
    status = check_company_status(ticker)
    
    print(f"Exists: {status.exists}")
    print(f"Is Active: {status.is_active}")
    print(f"Is Bankrupt: {status.is_bankrupt}")
    print(f"Is Delisted: {status.is_delisted}")
    
    if status.last_trading_date:
        print(f"Last Trading Date: {status.last_trading_date}")
        
    if status.status_reason:
        print(f"Status Reason: {status.status_reason}")
        
    print(f"Status Message: {status.get_status_message()}")
    
    should_stop = handle_special_status(status)
    print(f"Should stop analysis: {should_stop}")
    
    return status

def main():
    """Test the company status detection on various tickers."""
    # Test known bankrupt company
    test_company_status("BIG")  # Big Lots (filed for bankruptcy)
    
    # Test active company 
    test_company_status("MSFT")  # Microsoft (active)
    
    # Test other potentially delisted/bankrupt companies
    test_company_status("SEARS")  # Sears (bankrupt)
    test_company_status("LEHMAN")  # Lehman Brothers (bankrupt)
    
    # Test non-existent ticker
    test_company_status("XYZABC")  # Made-up ticker

if __name__ == "__main__":
    main()
