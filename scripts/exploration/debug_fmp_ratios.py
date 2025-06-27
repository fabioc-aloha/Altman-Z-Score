#!/usr/bin/env python3
"""
Debug FMP Ratios API - Direct API testing

This script directly tests the FMP ratios API to understand
what data is being returned and fix the data merger integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from altman_zscore.layers.data_fetch.fmp_fetcher import FMPDataFetcher
from altman_zscore.common.logging_config import get_logger
import json

logger = get_logger(__name__)


def test_fmp_ratios_api():
    """Test FMP ratios API directly."""
    print("🔍 Testing FMP Ratios API Directly")
    print("=" * 50)
    
    try:
        # Initialize FMP fetcher
        fetcher = FMPDataFetcher()
        
        # Test getting financial ratios for MSFT
        ticker = "MSFT"
        print(f"\n📊 Fetching financial ratios for {ticker}...")
        
        ratios = fetcher.get_financial_ratios(ticker, period="annual", limit=1)
        
        if ratios:
            print(f"✅ Got {len(ratios)} ratio entries")
            
            # Show the first (latest) ratio entry
            if len(ratios) > 0:
                latest_ratio = ratios[0]
                print(f"\n📈 Latest Ratio Data for {ticker}:")
                print(f"Date: {latest_ratio.get('date', 'N/A')}")
                print(f"Symbol: {latest_ratio.get('symbol', 'N/A')}")
                
                # Check for the specific ratios we need
                needed_ratios = [
                    'workingCapitalToTotalAssets',
                    'retainedEarningsToTotalAssets', 
                    'ebitToTotalAssets',
                    'assetTurnover',
                    'currentRatio',
                    'debtToEquityRatio'
                ]
                
                print(f"\n🎯 Z-Score Ratios Check:")
                for ratio_name in needed_ratios:
                    value = latest_ratio.get(ratio_name)
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {ratio_name}: {value}")
                
                # Show all available ratio keys
                print(f"\n📋 All Available Ratio Keys ({len(latest_ratio)} total):")
                for i, key in enumerate(sorted(latest_ratio.keys())):
                    if i < 20:  # Show first 20 keys
                        print(f"   - {key}: {latest_ratio[key]}")
                    elif i == 20:
                        print(f"   ... and {len(latest_ratio) - 20} more keys")
                        break
                
                # Save raw data for inspection
                with open("debug_fmp_ratios_raw.json", "w") as f:
                    json.dump(latest_ratio, f, indent=2)
                print(f"\n💾 Raw data saved to: debug_fmp_ratios_raw.json")
                
        else:
            print(f"❌ No ratio data returned for {ticker}")
            
            # Try getting company profile to verify ticker works
            print(f"\n🔍 Testing if ticker {ticker} is valid...")
            try:
                profile = fetcher.get_company_profile(ticker)
                if profile:
                    print(f"✅ Company profile found: {profile.get('companyName', 'N/A')}")
                else:
                    print(f"❌ No company profile found for {ticker}")
            except Exception as e:
                print(f"❌ Error getting company profile: {e}")
    
    except Exception as e:
        print(f"❌ Error testing FMP ratios API: {e}")
        import traceback
        traceback.print_exc()


def test_alternative_fmp_endpoints():
    """Test alternative FMP endpoints to find ratio data."""
    print(f"\n🔍 Testing Alternative FMP Endpoints")
    print("=" * 50)
    
    try:
        fetcher = FMPDataFetcher()
        ticker = "MSFT"
        
        # Test income statement
        print(f"\n📊 Testing Income Statement for {ticker}...")
        income_stmt = fetcher.get_income_statement(ticker, period="annual", limit=1)
        if income_stmt:
            print(f"✅ Income statement: {len(income_stmt)} entries")
            latest = income_stmt[0]
            print(f"   Revenue: {latest.get('revenue', 'N/A')}")
            print(f"   EBITDA: {latest.get('ebitda', 'N/A')}")
        
        # Test balance sheet  
        print(f"\n📊 Testing Balance Sheet for {ticker}...")
        balance_sheet = fetcher.get_balance_sheet(ticker, period="annual", limit=1)
        if balance_sheet:
            print(f"✅ Balance sheet: {len(balance_sheet)} entries")
            latest = balance_sheet[0]
            print(f"   Total Assets: {latest.get('totalAssets', 'N/A')}")
            print(f"   Current Assets: {latest.get('totalCurrentAssets', 'N/A')}")
            print(f"   Current Liabilities: {latest.get('totalCurrentLiabilities', 'N/A')}")
        
        # Test key metrics
        print(f"\n📊 Testing Key Metrics for {ticker}...")
        try:
            key_metrics = fetcher.get_key_metrics(ticker, period="annual", limit=1)
            if key_metrics:
                print(f"✅ Key metrics: {len(key_metrics)} entries") 
                latest = key_metrics[0]
                print(f"   Working Capital: {latest.get('workingCapital', 'N/A')}")
                print(f"   Book Value per Share: {latest.get('bookValuePerShare', 'N/A')}")
        except AttributeError:
            print(f"❌ get_key_metrics method not available")
        
    except Exception as e:
        print(f"❌ Error testing alternative endpoints: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fmp_ratios_api()
    test_alternative_fmp_endpoints()
