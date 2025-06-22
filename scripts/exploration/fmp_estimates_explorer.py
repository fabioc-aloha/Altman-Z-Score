#!/usr/bin/env python
"""
FMP Analyst Estimates Explorer
Tests Financial Modeling Prep's analyst estimates endpoints for forecasting Z-Score and F-Score
"""

import os
import json
import time
import sys
import argparse
from typing import Dict, List, Optional, Any
from urllib.request import urlopen
import certifi
from dotenv import load_dotenv

def get_jsonparsed_data(url: str, rate_limit_delay: float = 0.5) -> Optional[Dict]:
    """
    Fetch and parse JSON data from URL with enhanced error handling and rate limiting
    """
    try:
        time.sleep(rate_limit_delay)
        
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def test_estimates_endpoints(symbol: str, api_key: str):
    """Test all FMP analyst estimates endpoints for forecasting capabilities"""
    
    print(f"\n{'='*60}")
    print(f"FMP ANALYST ESTIMATES ENDPOINTS TEST - {symbol}")
    print(f"{'='*60}")
    
    # Define estimates endpoints
    estimates_endpoints = {
        "Analyst Estimates (Annual)": f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}",
        "Analyst Estimates (Quarterly)": f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}?period=quarter",
        "Earnings Estimates": f"https://financialmodelingprep.com/api/v3/earnings-estimate/{symbol}",
        "Revenue Estimates": f"https://financialmodelingprep.com/api/v3/revenue-estimate/{symbol}",
        "Analyst Recommendations": f"https://financialmodelingprep.com/api/v3/analyst-stock-recommendations/{symbol}",
        "Price Target": f"https://financialmodelingprep.com/api/v3/price-target/{symbol}",
        "Upgrades/Downgrades": f"https://financialmodelingprep.com/api/v3/upgrades-downgrades/{symbol}",
        "Consensus Estimates": f"https://financialmodelingprep.com/api/v3/analyst-estimates-consensus/{symbol}",
    }
    
    results = {}
    
    for name, endpoint in estimates_endpoints.items():
        print(f"\n{'-'*40}")
        print(f"Testing: {name}")
        print(f"Endpoint: {endpoint}")
        url = f"{endpoint}?apikey={api_key}"
        data = get_jsonparsed_data(url)
        
        if data is not None:
            if isinstance(data, list):
                if len(data) > 0:
                    print(f"✓ SUCCESS - Retrieved {len(data)} records")
                    print(f"  Sample keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                    if isinstance(data[0], dict):
                        print(f"  Sample data: {json.dumps(data[0], indent=2)[:200]}...")
                    results[name] = {
                        "status": "success",
                        "count": len(data),
                        "sample": data[0] if isinstance(data[0], dict) else data[0]
                    }
                else:
                    print("⚠ EMPTY - No records returned (may be valid for this stock)")
                    results[name] = {"status": "empty"}
            elif isinstance(data, dict):
                print(f"✓ SUCCESS - Retrieved dict data")
                print(f"  Keys: {list(data.keys())}")
                print(f"  Sample data: {json.dumps(data, indent=2)[:200]}...")
                results[name] = {
                    "status": "success",
                    "data": data
                }
            else:
                print(f"? PARTIAL - Unexpected data format: {type(data)}")
                results[name] = {
                    "status": "partial",
                    "data": data
                }
        else:
            print("✗ FAILED - No data returned")
            results[name] = {"status": "failed"}
    
    return results

def analyze_forecasting_potential(symbol: str, results: Dict):
    """Analyze the forecasting potential for Z-Score and F-Score calculations"""
    
    print(f"\n{'='*60}")
    print(f"FORECASTING ANALYSIS FOR {symbol}")
    print(f"{'='*60}")
    
    # Check for key data needed for Z-Score forecasting
    zscore_requirements = [
        "Working Capital estimates",
        "Retained Earnings estimates", 
        "EBIT estimates",
        "Market Value estimates",
        "Total Liabilities estimates",
        "Revenue estimates"
    ]
    
    # Check for key data needed for F-Score forecasting
    fscore_requirements = [
        "Net Income estimates",
        "Cash Flow estimates",
        "ROA estimates",
        "Debt-to-Assets estimates",
        "Current Ratio estimates",
        "Share count estimates"
    ]
    
    print("\nZ-SCORE FORECASTING POTENTIAL:")
    print("-" * 30)
    
    available_estimates = []
    if "Analyst Estimates (Annual)" in results and results["Analyst Estimates (Annual)"]["status"] == "success":
        sample = results["Analyst Estimates (Annual)"]["sample"]
        if isinstance(sample, dict):
            keys = sample.keys()
            print(f"Available estimate fields: {list(keys)}")
            available_estimates = list(keys)
    
    print(f"\nForecasting viability: {'HIGH' if len(available_estimates) > 5 else 'MEDIUM' if len(available_estimates) > 2 else 'LOW'}")
    
    print("\nF-SCORE FORECASTING POTENTIAL:")
    print("-" * 30)
    
    if "Earnings Estimates" in results and results["Earnings Estimates"]["status"] == "success":
        print("✓ Earnings estimates available for ROA forecasting")
    
    if "Revenue Estimates" in results and results["Revenue Estimates"]["status"] == "success":
        print("✓ Revenue estimates available for growth analysis")
    
    print("\nRECOMMENDATIONS:")
    print("-" * 15)
    print("1. Use analyst estimates to project future Z-Scores and F-Scores")
    print("2. Combine with historical trends for more robust forecasting")
    print("3. Consider analyst recommendation consensus for risk weighting")
    print("4. Monitor upgrades/downgrades for early warning signals")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Test FMP analyst estimates endpoints")
    parser.add_argument("symbol", nargs="?", default="AAPL", help="Stock symbol to test (default: AAPL)")
    
    args = parser.parse_args()
    symbol = args.symbol.upper()
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('FINANCIAL_MODELING_PREP_API_KEY')
    if not api_key:
        print("Error: FINANCIAL_MODELING_PREP_API_KEY not found in environment variables")
        print("Please add your FMP API key to .env file")
        sys.exit(1)
    
    print(f"Testing FMP Analyst Estimates Endpoints for {symbol}")
    print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:]}")
    
    # Test all estimates endpoints
    results = test_estimates_endpoints(symbol, api_key)
    
    # Analyze forecasting potential
    analyze_forecasting_potential(symbol, results)
    
    # Save results
    output_file = f"fmp_estimates_test_{symbol.lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for r in results.values() if r.get("status") == "success")
    total = len(results)
    
    print(f"Successful endpoints: {successful}/{total}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful >= 4:
        print("✓ EXCELLENT forecasting capability - most estimates available")
    elif successful >= 2:
        print("⚠ GOOD forecasting capability - some estimates available")
    else:
        print("✗ LIMITED forecasting capability - upgrade subscription may be needed")

if __name__ == "__main__":
    main()
