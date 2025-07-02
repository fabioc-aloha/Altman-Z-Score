#!/usr/bin/env python3
"""
SEC EDGAR Retrieval Example
========================

This script demonstrates how to use the SEC EDGAR connector to retrieve
financial data for delisted companies.

Usage:
    python retail_validation/scripts/get_sec_edgar_data.py [ticker]
"""

import sys
import asyncio
import json
from pathlib import Path
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from retail_validation.data.sec_edgar.edgar_connector import EdgarConnector
from retail_validation.config.validation_config import BANKRUPTCY_DATES

async def get_financial_data_for_ticker(ticker: str):
    """Retrieve financial data for a delisted company from SEC EDGAR"""
    
    print(f"Retrieving SEC EDGAR data for {ticker}")
    
    if ticker not in BANKRUPTCY_DATES:
        print(f"Error: No bankruptcy date found for {ticker}")
        print(f"Known bankruptcy tickers: {list(BANKRUPTCY_DATES.keys())}")
        return
    
    bankruptcy_date = BANKRUPTCY_DATES[ticker]
    print(f"Bankruptcy date: {bankruptcy_date}")
    
    connector = EdgarConnector()
    
    # Get CIK number
    cik = await connector.get_cik_for_ticker(ticker)
    if not cik:
        print(f"Error: Could not find CIK for {ticker}")
        return
    
    print(f"CIK: {cik}")
    
    # Get filings
    print("Getting recent filings...")
    annual_filings = await connector.get_recent_filings(ticker, "10-K", 3)
    quarterly_filings = await connector.get_recent_filings(ticker, "10-Q", 4)
    
    print(f"Found {len(annual_filings)} annual filings")
    print(f"Found {len(quarterly_filings)} quarterly filings")
    
    # Get financial data
    print("Extracting financial data...")
    financial_data = await connector.get_financial_data(ticker)
    
    if not financial_data:
        print("Error: Could not retrieve financial data")
        return
    
    # Display results
    print("\nFinancial Data Summary:")
    print("-----------------------")
    
    if 'filing_date' in financial_data:
        print(f"Filing Date: {financial_data['filing_date']}")
    if 'filing_type' in financial_data:
        print(f"Filing Type: {financial_data['filing_type']}")
    if 'quarters_before_bankruptcy' in financial_data:
        print(f"Quarters Before Bankruptcy: {financial_data['quarters_before_bankruptcy']}")
    
    print("\nFinancial Metrics:")
    for metric, value in {k: v for k, v in financial_data.items() 
                        if k not in ['ticker', 'filing_date', 'filing_type', 'quarters_before_bankruptcy']}.items():
        if value is not None:
            print(f"  {metric}: ${value:,.2f}")
    
    # Transform to Z-Score input format
    transformed_data = await connector.transform_to_zscore_input(financial_data)
    
    if transformed_data:
        print("\nData ready for Z-Score calculation")
        print("--------------------------------")
        
        # Display some key metrics
        metrics = transformed_data.metrics
        
        working_capital = metrics.total_current_assets - metrics.total_current_liabilities
        total_assets = metrics.total_assets
        
        print(f"Working Capital / Total Assets: {working_capital / total_assets:.4f}")
        print(f"Retained Earnings / Total Assets: {metrics.retained_earnings / total_assets:.4f}")
        print(f"EBIT / Total Assets: {metrics.ebit / total_assets:.4f}")
        print(f"Revenue / Total Assets: {metrics.revenue / total_assets:.4f}")
    else:
        print("Could not transform data for Z-Score calculation")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Retrieve SEC EDGAR data for a delisted company')
    parser.add_argument('ticker', help='Ticker symbol of delisted company')
    
    args = parser.parse_args()
    
    asyncio.run(get_financial_data_for_ticker(args.ticker.upper()))

if __name__ == "__main__":
    main()
