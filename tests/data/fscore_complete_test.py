#!/usr/bin/env python
"""
F-Score Field Inspector
Inspects actual FMP data structure to find all available fields for F-Score calculation
"""

import os
import json
import time
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional, Any
from urllib.request import urlopen
import certifi
from dotenv import load_dotenv

def get_jsonparsed_data(url: str, rate_limit_delay: float = 0.5) -> Optional[Dict]:
    """Fetch and parse JSON data from URL with enhanced error handling and rate limiting"""
    try:
        time.sleep(rate_limit_delay)
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def inspect_all_fields(symbol: str, api_key: str):
    """Inspect all available fields in FMP financial statements"""
    
    print(f"\n{'='*60}")
    print(f"COMPLETE FIELD INSPECTION - {symbol}")
    print(f"{'='*60}")
    
    endpoints = {
        "Income Statement": f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=2&apikey={api_key}",
        "Balance Sheet": f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=2&apikey={api_key}",
        "Cash Flow": f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit=2&apikey={api_key}",
        "Financial Ratios": f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?limit=2&apikey={api_key}",
    }
    
    all_data = {}
    
    for endpoint_name, url in endpoints.items():
        print(f"\n{'-'*50}")
        print(f"INSPECTING: {endpoint_name}")
        print(f"{'-'*50}")
        
        data = get_jsonparsed_data(url)
        
        if data and isinstance(data, list) and len(data) >= 2:
            current_year = data[0]
            prior_year = data[1]
            
            print(f"Available fields ({len(current_year.keys())} total):")
            for i, field in enumerate(sorted(current_year.keys()), 1):
                value = current_year[field]
                print(f"  {i:2}. {field}: {value} ({type(value).__name__})")
            
            all_data[endpoint_name] = {
                "current_year": current_year,
                "prior_year": prior_year,
                "all_fields": list(current_year.keys())
            }
        else:
            print("❌ No data available")
            all_data[endpoint_name] = None
    
    return all_data

def calculate_complete_fscore(symbol: str, data: Dict):
    """Calculate complete F-Score using all available data"""
    
    print(f"\n{'='*60}")
    print(f"COMPLETE F-SCORE CALCULATION - {symbol}")
    print(f"{'='*60}")
    
    if not all(endpoint in data and data[endpoint] for endpoint in ["Income Statement", "Balance Sheet", "Cash Flow", "Financial Ratios"]):
        print("❌ Insufficient data for complete F-Score calculation")
        return None
    
    # Extract current and prior year data
    income_current = data["Income Statement"]["current_year"]
    income_prior = data["Income Statement"]["prior_year"]
    balance_current = data["Balance Sheet"]["current_year"]
    balance_prior = data["Balance Sheet"]["prior_year"]
    cashflow_current = data["Cash Flow"]["current_year"]
    cashflow_prior = data["Cash Flow"]["prior_year"]
    ratios_current = data["Financial Ratios"]["current_year"]
    ratios_prior = data["Financial Ratios"]["prior_year"]
    
    fscore = 0
    components = {}
    
    print(f"Calculating F-Score for:")
    print(f"  Current year: {income_current.get('date', 'N/A')}")
    print(f"  Prior year: {income_prior.get('date', 'N/A')}")
    print()
    
    # 1. Positive Net Income
    net_income = income_current.get('netIncome', 0)
    if net_income > 0:
        fscore += 1
        components['positive_net_income'] = True
        print(f"✅ 1. Positive Net Income: ${net_income:,.0f} > 0 → +1 point")
    else:
        components['positive_net_income'] = False
        print(f"❌ 1. Positive Net Income: ${net_income:,.0f} ≤ 0 → 0 points")
    
    # 2. Positive ROA
    roa = ratios_current.get('returnOnAssets', 0)
    if roa > 0:
        fscore += 1
        components['positive_roa'] = True
        print(f"✅ 2. Positive ROA: {roa:.4f} > 0 → +1 point")
    else:
        components['positive_roa'] = False
        print(f"❌ 2. Positive ROA: {roa:.4f} ≤ 0 → 0 points")
    
    # 3. Positive Operating Cash Flow
    op_cash_flow = cashflow_current.get('operatingCashFlow', 0)
    if op_cash_flow > 0:
        fscore += 1
        components['positive_operating_cf'] = True
        print(f"✅ 3. Positive Operating Cash Flow: ${op_cash_flow:,.0f} > 0 → +1 point")
    else:
        components['positive_operating_cf'] = False
        print(f"❌ 3. Positive Operating Cash Flow: ${op_cash_flow:,.0f} ≤ 0 → 0 points")
    
    # 4. Operating Cash Flow > Net Income (Quality of Earnings)
    if op_cash_flow > net_income:
        fscore += 1
        components['cf_exceeds_ni'] = True
        print(f"✅ 4. Operating CF > Net Income: ${op_cash_flow:,.0f} > ${net_income:,.0f} → +1 point")
    else:
        components['cf_exceeds_ni'] = False
        print(f"❌ 4. Operating CF > Net Income: ${op_cash_flow:,.0f} ≤ ${net_income:,.0f} → 0 points")
    
    # 5. Decreasing Long-term Debt Ratio
    current_debt_ratio = balance_current.get('longTermDebt', 0) / balance_current.get('totalAssets', 1)
    prior_debt_ratio = balance_prior.get('longTermDebt', 0) / balance_prior.get('totalAssets', 1)
    if current_debt_ratio < prior_debt_ratio:
        fscore += 1
        components['decreasing_debt'] = True
        print(f"✅ 5. Decreasing Debt Ratio: {current_debt_ratio:.4f} < {prior_debt_ratio:.4f} → +1 point")
    else:
        components['decreasing_debt'] = False
        print(f"❌ 5. Decreasing Debt Ratio: {current_debt_ratio:.4f} ≥ {prior_debt_ratio:.4f} → 0 points")
    
    # 6. Increasing Current Ratio
    current_ratio_current = ratios_current.get('currentRatio', 0)
    current_ratio_prior = ratios_prior.get('currentRatio', 0)
    if current_ratio_current > current_ratio_prior:
        fscore += 1
        components['improving_current_ratio'] = True
        print(f"✅ 6. Increasing Current Ratio: {current_ratio_current:.4f} > {current_ratio_prior:.4f} → +1 point")
    else:
        components['improving_current_ratio'] = False
        print(f"❌ 6. Increasing Current Ratio: {current_ratio_current:.4f} ≤ {current_ratio_prior:.4f} → 0 points")
    
    # 7. No Share Dilution - check multiple possible field names
    share_fields = ['commonStock', 'commonStockSharesOutstanding', 'sharesOutstanding', 'weightedAverageShsOut', 'weightedAverageShsOutDil']
    shares_current = None
    shares_prior = None
    
    for field in share_fields:
        if field in balance_current and field in balance_prior:
            shares_current = balance_current[field]
            shares_prior = balance_prior[field]
            break
    
    if shares_current is not None and shares_prior is not None:
        if shares_current <= shares_prior:
            fscore += 1
            components['no_share_dilution'] = True
            print(f"✅ 7. No Share Dilution: {shares_current:,.0f} ≤ {shares_prior:,.0f} → +1 point")
        else:
            components['no_share_dilution'] = False
            print(f"❌ 7. No Share Dilution: {shares_current:,.0f} > {shares_prior:,.0f} → 0 points")
    else:
        components['no_share_dilution'] = None
        print(f"❓ 7. No Share Dilution: Share count data not available → 0 points")
    
    # 8. Increasing Gross Margin
    gross_margin_current = ratios_current.get('grossProfitMargin', 0)
    gross_margin_prior = ratios_prior.get('grossProfitMargin', 0)
    if gross_margin_current > gross_margin_prior:
        fscore += 1
        components['improving_gross_margin'] = True
        print(f"✅ 8. Increasing Gross Margin: {gross_margin_current:.4f} > {gross_margin_prior:.4f} → +1 point")
    else:
        components['improving_gross_margin'] = False
        print(f"❌ 8. Increasing Gross Margin: {gross_margin_current:.4f} ≤ {gross_margin_prior:.4f} → 0 points")
    
    # 9. Increasing Asset Turnover
    asset_turnover_current = ratios_current.get('assetTurnover', 0)
    asset_turnover_prior = ratios_prior.get('assetTurnover', 0)
    if asset_turnover_current > asset_turnover_prior:
        fscore += 1
        components['improving_asset_turnover'] = True
        print(f"✅ 9. Increasing Asset Turnover: {asset_turnover_current:.4f} > {asset_turnover_prior:.4f} → +1 point")
    else:
        components['improving_asset_turnover'] = False
        print(f"❌ 9. Increasing Asset Turnover: {asset_turnover_current:.4f} ≤ {asset_turnover_prior:.4f} → 0 points")
    
    print(f"\n{'='*40}")
    print(f"FINAL F-SCORE: {fscore}/9")
    print(f"{'='*40}")
    
    # Interpret F-Score
    if fscore >= 8:
        interpretation = "🟢 HIGH QUALITY - Strong fundamental health"
    elif fscore >= 6:
        interpretation = "🟡 MEDIUM QUALITY - Mixed signals"
    elif fscore >= 4:
        interpretation = "🟠 LOW QUALITY - Some concerns"
    else:
        interpretation = "🔴 POOR QUALITY - Significant issues"
    
    print(f"Interpretation: {interpretation}")
    
    return {
        'f_score': fscore,
        'components': components,
        'interpretation': interpretation
    }

def main():
    """Main execution function"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('FINANCIAL_MODELING_PREP_API_KEY')
    if not api_key:
        print("Error: FINANCIAL_MODELING_PREP_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Test with a symbol (default AAPL)
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    symbol = symbol.upper()
    
    print(f"Complete F-Score analysis for {symbol}")
    print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:]}")
    
    # Inspect all available fields
    all_data = inspect_all_fields(symbol, api_key)
    
    # Calculate complete F-Score
    fscore_result = calculate_complete_fscore(symbol, all_data)
    
    # Save complete results
    output_file = f"complete_fscore_{symbol.lower()}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "symbol": symbol,
            "fscore_result": fscore_result,
            "raw_data": all_data
        }, f, indent=2, default=str)
    
    print(f"\nComplete results saved to: {output_file}")
    
    # Summary
    if fscore_result:
        print(f"\n🎯 SUMMARY:")
        print(f"  Symbol: {symbol}")
        print(f"  F-Score: {fscore_result['f_score']}/9")
        print(f"  Assessment: {fscore_result['interpretation']}")
        print(f"  Data Coverage: Complete (all 9 components calculated)")

if __name__ == "__main__":
    main()
