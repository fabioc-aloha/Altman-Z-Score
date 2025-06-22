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
        
        response = urlopen(url)
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
                        print(f"  Sample data preview:")
                        # Show key fields for Z-Score/F-Score relevance
                        sample = data[0]
                        relevant_fields = [k for k in sample.keys() if any(term in k.lower() for term in 
                                         ['revenue', 'earnings', 'ebit', 'debt', 'asset', 'equity', 'cash', 'current'])]
                        if relevant_fields:
                            print(f"    Relevant fields: {relevant_fields}")
                            for field in relevant_fields[:3]:  # Show first 3 relevant fields
                                print(f"    {field}: {sample.get(field)}")
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
    
    # Analyze successful endpoints
    successful_endpoints = [name for name, result in results.items() if result.get("status") == "success"]
    
    print(f"\nSUCCESSFUL ENDPOINTS ({len(successful_endpoints)}):")
    print("-" * 30)
    for endpoint in successful_endpoints:
        print(f"✓ {endpoint}")
    
    print("\nZ-SCORE FORECASTING ANALYSIS:")
    print("-" * 30)
    
    zscore_mapping = {
        "Working Capital": ["current_assets", "current_liabilities", "working_capital"],
        "Retained Earnings": ["retained_earnings", "accumulated_earnings"],
        "EBIT": ["ebit", "operating_income", "earnings_before_interest_and_taxes"],
        "Market Value": ["market_cap", "market_capitalization"],
        "Revenue": ["revenue", "total_revenue", "net_revenue"],
        "Total Assets": ["total_assets", "assets"],
        "Total Liabilities": ["total_liabilities", "liabilities"]
    }
    
    print("Z-Score component availability from estimates:")
    for component, field_names in zscore_mapping.items():
        found = False
        for name, result in results.items():
            if result.get("status") == "success" and "sample" in result:
                sample = result["sample"]
                if isinstance(sample, dict):
                    sample_keys = [k.lower() for k in sample.keys()]
                    if any(field in sample_keys for field in field_names):
                        print(f"  ✓ {component}: Available in {name}")
                        found = True
                        break
        if not found:
            print(f"  ✗ {component}: Not found in estimates")
    
    print("\nF-SCORE FORECASTING ANALYSIS:")
    print("-" * 30)
    
    fscore_components = {
        "Net Income": ["net_income", "earnings"],
        "Cash Flow": ["operating_cash_flow", "cash_flow_from_operations"],
        "ROA": ["return_on_assets", "roa"],
        "Long-term Debt": ["long_term_debt", "total_debt"],
        "Current Ratio": ["current_ratio"],
        "Shares Outstanding": ["shares_outstanding", "weighted_average_shares"]
    }
    
    print("F-Score component availability from estimates:")
    for component, field_names in fscore_components.items():
        found = False
        for name, result in results.items():
            if result.get("status") == "success" and "sample" in result:
                sample = result["sample"]
                if isinstance(sample, dict):
                    sample_keys = [k.lower() for k in sample.keys()]
                    if any(field in sample_keys for field in field_names):
                        print(f"  ✓ {component}: Available in {name}")
                        found = True
                        break
        if not found:
            print(f"  ✗ {component}: Not found in estimates")
    
    print("\nFORECASTING RECOMMENDATIONS:")
    print("-" * 25)
    
    if len(successful_endpoints) >= 4:
        print("🎯 EXCELLENT: Strong forecasting capability")
        print("   → Implement automated Z-Score/F-Score projections")
        print("   → Build trend analysis and early warning systems")
    elif len(successful_endpoints) >= 2:
        print("📈 GOOD: Moderate forecasting capability")
        print("   → Focus on available estimates for key ratios")
        print("   → Supplement with historical trend extrapolation")
    else:
        print("⚠️  LIMITED: Minimal forecasting capability")
        print("   → Consider upgrading FMP subscription tier")
        print("   → Use historical data for trend-based forecasting")
    
    print("\nIMPLEMENTATION STRATEGY:")
    print("1. Combine analyst estimates with historical financial data")
    print("2. Weight forecasts by analyst consensus strength")
    print("3. Create confidence intervals based on estimate variance")
    print("4. Monitor estimate revisions as leading indicators")

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
    empty = sum(1 for r in results.values() if r.get("status") == "empty")
    total = len(results)
    
    print(f"Successful endpoints: {successful}/{total}")
    print(f"Empty results: {empty}/{total}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful >= 4:
        print("✅ EXCELLENT forecasting capability - most estimates available")
    elif successful >= 2:
        print("⚠️ GOOD forecasting capability - some estimates available")
    else:
        print("❌ LIMITED forecasting capability - upgrade subscription may be needed")

if __name__ == "__main__":
    main()
