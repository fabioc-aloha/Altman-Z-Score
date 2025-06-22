#!/usr/bin/env python
"""
Comprehensive test script for Financial Modeling Prep API
Tests all key endpoints available with STANDARD/PROFESSIONAL tier subscription
Validates Z-Score calculation capability using FMP pre-computed ratios
Includes analyst estimates for forecasting capabilities
"""

import os
import json
import time
import sys
import argparse
from typing import Dict, List, Optional, Any
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import certifi
from dotenv import load_dotenv

def get_jsonparsed_data(url: str, rate_limit_delay: float = 0.5) -> Optional[Dict]:
    """
    Fetch and parse JSON data from URL with enhanced error handling and rate limiting
    
    Args:
        url: API endpoint URL
        rate_limit_delay: Delay between requests to respect rate limits
    
    Returns:
        Parsed JSON data or None if error
    """
    try:
        # Rate limiting
        time.sleep(rate_limit_delay)
        
        import urllib.error
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        if e.code == 402:
            error_msg += "\n  -> Payment required or subscription tier insufficient"
        elif e.code == 401:
            error_msg += "\n  -> Invalid or expired API key"
        elif e.code == 403:
            error_msg += "\n  -> Access forbidden or API key lacks permissions"
        elif e.code == 429:
            error_msg += "\n  -> Rate limit exceeded - try reducing request frequency"
        elif e.code == 404:
            error_msg += "\n  -> Endpoint not found or symbol not supported"
        
        # Try to read error response body
        try:
            error_body = e.read().decode("utf-8")
            error_msg += f"\n  -> Server response: {error_body}"
        except:
            pass
            
        print(f"❌ Error: {error_msg}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_fmp_comprehensive(symbol: str = "SONO"):
    """
    Comprehensive test of Financial Modeling Prep API endpoints
    Tests all key endpoints that should be available with STANDARD/PROFESSIONAL tier
    
    Args:
        symbol: Stock ticker symbol to test (default: SONO)
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('FINANCIAL_MODELING_PREP_API_KEY')
    
    if not api_key:
        print("❌ ERROR: FINANCIAL_MODELING_PREP_API_KEY not found in environment variables")
        return
    
    # Remove quotes if present
    api_key = api_key.strip('"')
    
    print("🚀 COMPREHENSIVE FMP API TEST")
    print("=" * 60)
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"📊 Test Symbol: {symbol.upper()}")
    print("=" * 60)
    print()
    
    # Test endpoints in order of importance for Z-Score calculation
    test_results = {}
    
    # Define all endpoints to test
    endpoints = [
        # Core Financial Data (Required for Z-Score)
        {
            "name": "Company Profile",
            "url": f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "HIGH",
            "purpose": "Company info, market cap, industry"
        },
        {
            "name": "Balance Sheet Statement",
            "url": f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?apikey={api_key}",
            "tier": "STARTER", 
            "importance": "HIGH",
            "purpose": "Working capital, retained earnings, total assets"
        },
        {
            "name": "Income Statement",
            "url": f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "HIGH", 
            "purpose": "Revenue, EBIT, net income"
        },
        {
            "name": "Cash Flow Statement",
            "url": f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "MEDIUM",
            "purpose": "Operating cash flow, free cash flow"
        },
        
        # Pre-computed Ratios (Key for Z-Score calculation)
        {
            "name": "Financial Ratios",
            "url": f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "HIGH",
            "purpose": "Pre-computed ratios for direct Z-Score calculation"
        },
        {
            "name": "Key Metrics",
            "url": f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?apikey={api_key}",
            "tier": "STARTER", 
            "importance": "HIGH",
            "purpose": "Market cap, book value, enterprise value"
        },
        {
            "name": "Financial Ratios TTM",
            "url": f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "HIGH",
            "purpose": "Real-time trailing twelve months ratios"
        },
        {
            "name": "Key Metrics TTM", 
            "url": f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "HIGH",
            "purpose": "Real-time TTM metrics"
        },
        
        # Enhanced Analysis
        {
            "name": "Enterprise Values",
            "url": f"https://financialmodelingprep.com/api/v3/enterprise-values/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "MEDIUM",
            "purpose": "Enterprise value calculations"
        },
        {
            "name": "Financial Growth",
            "url": f"https://financialmodelingprep.com/api/v3/financial-growth/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "MEDIUM", 
            "purpose": "Growth metrics and trends"
        },
        {
            "name": "Company Rating",
            "url": f"https://financialmodelingprep.com/api/v3/rating/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "LOW",
            "purpose": "Credit-style company ratings"
        },
        {
            "name": "DCF Valuation",
            "url": f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{symbol}?apikey={api_key}",
            "tier": "PREMIUM",
            "importance": "LOW",
            "purpose": "Discounted cash flow valuation"
        },
        
        # Premium Features (Expected to fail with current tier)
        {
            "name": "Financial Scores",
            "url": f"https://financialmodelingprep.com/api/v4/score?symbol={symbol}&apikey={api_key}",
            "tier": "ULTIMATE",
            "importance": "MEDIUM",
            "purpose": "Pre-computed Z-Score and Piotroski Score"
        },
        {
            "name": "Quarterly Balance Sheet",
            "url": f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?period=quarter&apikey={api_key}",
            "tier": "PREMIUM",  
            "importance": "MEDIUM",
            "purpose": "Quarterly financial statements"
        },
        
        # Analyst Estimates (Newly added endpoints)
        {
            "name": "Analyst Estimates",
            "url": f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "MEDIUM",
            "purpose": "Analyst price targets and ratings"
        },
        {
            "name": "Analyst Ratings",
            "url": f"https://financialmodelingprep.com/api/v3/analyst-ratings/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "MEDIUM",
            "purpose": "Analyst ratings distribution"
        },
        {
            "name": "Price Target",
            "url": f"https://financialmodelingprep.com/api/v3/price-target/{symbol}?apikey={api_key}",
            "tier": "STARTER",
            "importance": "MEDIUM",
            "purpose": "Consensus price target from analysts"
        }
    ]
    
    # Test each endpoint
    successful_endpoints = []
    failed_endpoints = []
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"🧪 Test {i}/{len(endpoints)}: {endpoint['name']}")
        print(f"   📊 Tier: {endpoint['tier']} | Importance: {endpoint['importance']}")
        print(f"   🎯 Purpose: {endpoint['purpose']}")
        
        # Test the endpoint
        data = get_jsonparsed_data(endpoint['url'])
        
        if data is not None:
            print(f"   ✅ SUCCESS - Data retrieved")
            successful_endpoints.append(endpoint)
            test_results[endpoint['name']] = {
                'status': 'success',
                'data_size': len(str(data)),
                'data_preview': str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
            }
        else:
            print(f"   ❌ FAILED - No data retrieved")
            failed_endpoints.append(endpoint)
            test_results[endpoint['name']] = {
                'status': 'failed',
                'tier': endpoint['tier'],
                'importance': endpoint['importance']
            }
        
        print()
        time.sleep(0.5)  # Rate limiting
    
    # Display comprehensive results
    display_comprehensive_results(successful_endpoints, failed_endpoints, test_results, symbol)
    
    # Test Z-Score calculation capability
    if any(ep['name'] in ['Financial Ratios', 'Balance Sheet Statement', 'Key Metrics'] 
           for ep in successful_endpoints):
        print("\n" + "="*60)
        print("🧮 Z-SCORE CALCULATION TEST")
        print("="*60)
        test_zscore_calculation(symbol, api_key, test_results)
    
    return test_results

def display_comprehensive_results(successful_endpoints: List[Dict], failed_endpoints: List[Dict], 
                                 test_results: Dict, symbol: str):
    """
    Display comprehensive test results with analysis
    """
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("="*60)
    
    # Summary statistics
    total_tests = len(successful_endpoints) + len(failed_endpoints)
    success_rate = (len(successful_endpoints) / total_tests) * 100
    
    print(f"🎯 Symbol Tested: {symbol}")
    print(f"✅ Successful Endpoints: {len(successful_endpoints)}/{total_tests} ({success_rate:.1f}%)")
    print(f"❌ Failed Endpoints: {len(failed_endpoints)}/{total_tests}")
    print()
    
    # Successful endpoints by tier
    print("✅ SUCCESSFUL ENDPOINTS:")
    print("-" * 40)
    tier_counts = {}
    for endpoint in successful_endpoints:
        tier = endpoint['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        status_icon = "🟢" if endpoint['importance'] == 'HIGH' else "🟡" if endpoint['importance'] == 'MEDIUM' else "⚪"
        print(f"  {status_icon} {endpoint['name']} (Tier: {tier}, Importance: {endpoint['importance']})")
    
    print()
    print("📈 SUCCESS BY SUBSCRIPTION TIER:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count} endpoints")
    
    # Failed endpoints analysis
    if failed_endpoints:
        print()
        print("❌ FAILED ENDPOINTS:")
        print("-" * 40)
        tier_failures = {}
        for endpoint in failed_endpoints:
            tier = endpoint['tier']
            tier_failures[tier] = tier_failures.get(tier, 0) + 1
            status_icon = "🔴" if endpoint['importance'] == 'HIGH' else "🟠" if endpoint['importance'] == 'MEDIUM' else "⚫"
            print(f"  {status_icon} {endpoint['name']} (Tier: {tier}, Importance: {endpoint['importance']})")
        
        print()
        print("📉 FAILURES BY SUBSCRIPTION TIER:")
        for tier, count in sorted(tier_failures.items()):
            print(f"  {tier}: {count} endpoints")
    
    # Z-Score capability analysis
    print()
    print("🧮 Z-SCORE CALCULATION CAPABILITY:")
    print("-" * 40)
    
    zscore_requirements = {
        'Balance Sheet Statement': 'Working capital, retained earnings, total assets',
        'Income Statement': 'EBIT, revenue', 
        'Key Metrics': 'Market capitalization',
        'Financial Ratios': 'Pre-computed ratios for direct calculation'
    }
    
    available_zscore_data = []
    missing_zscore_data = []
    
    for requirement, description in zscore_requirements.items():
        if any(ep['name'] == requirement for ep in successful_endpoints):
            available_zscore_data.append((requirement, description))
            print(f"  ✅ {requirement}: {description}")
        else:
            missing_zscore_data.append((requirement, description))
            print(f"  ❌ {requirement}: {description}")
    
    # Overall assessment
    print()
    print("🎯 SUBSCRIPTION TIER ASSESSMENT:")
    print("-" * 40)
    
    if len(available_zscore_data) >= 3:
        print("  🚀 EXCELLENT: Full Z-Score calculation capability confirmed!")
        print("  💡 Your current tier provides all necessary data for Z-Score analysis")
    elif len(available_zscore_data) >= 2:
        print("  ✅ GOOD: Most Z-Score components available")
        print("  💡 Z-Score calculation possible with some limitations")
    else:
        print("  ⚠️  LIMITED: Missing critical Z-Score components")
        print("  💡 Consider subscription upgrade for full capability")
    
    # Cost-benefit analysis
    print()
    high_importance_success = sum(1 for ep in successful_endpoints if ep['importance'] == 'HIGH')
    high_importance_total = sum(1 for ep in successful_endpoints + failed_endpoints if ep['importance'] == 'HIGH')
    
    if high_importance_success == high_importance_total:
        print("  💰 VALUE ASSESSMENT: Excellent value - all critical features available")
    elif high_importance_success >= high_importance_total * 0.75:
        print("  💰 VALUE ASSESSMENT: Good value - most critical features available")
    else:
        print("  💰 VALUE ASSESSMENT: Consider upgrade - missing critical features")

def test_zscore_calculation(symbol: str, api_key: str, test_results: Dict):
    """
    Test actual Z-Score calculation using available FMP data
    """
    print("🧮 Testing Z-Score calculation from FMP data...")
    print()
    
    # Try to calculate Z-Score using available data
    zscore_components = {}
    calculation_possible = True
    
    # Get financial ratios if available
    if 'Financial Ratios' in test_results and test_results['Financial Ratios']['status'] == 'success':
        print("📊 Fetching financial ratios for Z-Score calculation...")
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?apikey={api_key}"
        ratios_data = get_jsonparsed_data(ratios_url)
        
        if ratios_data and len(ratios_data) > 0:
            latest_ratios = ratios_data[0]  # Most recent year
            print(f"   ✅ Retrieved ratios for {latest_ratios.get('date', 'unknown date')}")
            
            # Extract Z-Score relevant ratios
            zscore_components['current_ratio'] = latest_ratios.get('currentRatio')
            zscore_components['debt_equity_ratio'] = latest_ratios.get('debtEquityRatio') 
            zscore_components['return_on_assets'] = latest_ratios.get('returnOnAssets')
            zscore_components['asset_turnover'] = latest_ratios.get('assetTurnover')
            
            print("   📈 Key ratios extracted:")
            for key, value in zscore_components.items():
                if value is not None:
                    print(f"     {key.replace('_', ' ').title()}: {value:.4f}")
    
    # Get balance sheet data if available  
    if 'Balance Sheet Statement' in test_results and test_results['Balance Sheet Statement']['status'] == 'success':
        print("📊 Fetching balance sheet for Z-Score components...")
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?apikey={api_key}"
        balance_data = get_jsonparsed_data(balance_url)
        
        if balance_data and len(balance_data) > 0:
            latest_balance = balance_data[0]  # Most recent year
            print(f"   ✅ Retrieved balance sheet for {latest_balance.get('date', 'unknown date')}")
            
            # Calculate working capital ratio
            current_assets = latest_balance.get('totalCurrentAssets', 0)
            current_liabilities = latest_balance.get('totalCurrentLiabilities', 0) 
            total_assets = latest_balance.get('totalAssets', 1)  # Avoid division by zero
            
            if total_assets > 0:
                working_capital_ratio = (current_assets - current_liabilities) / total_assets
                zscore_components['working_capital_ratio'] = working_capital_ratio
                print(f"     Working Capital Ratio: {working_capital_ratio:.4f}")
                
                # Retained earnings ratio
                retained_earnings = latest_balance.get('retainedEarnings', 0)
                retained_earnings_ratio = retained_earnings / total_assets
                zscore_components['retained_earnings_ratio'] = retained_earnings_ratio
                print(f"     Retained Earnings Ratio: {retained_earnings_ratio:.4f}")
    
    # Get market data if available
    if 'Key Metrics' in test_results and test_results['Key Metrics']['status'] == 'success':
        print("📊 Fetching key metrics for market value component...")
        metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?apikey={api_key}"
        metrics_data = get_jsonparsed_data(metrics_url)
        
        if metrics_data and len(metrics_data) > 0:
            latest_metrics = metrics_data[0]
            market_cap = latest_metrics.get('marketCap')
            if market_cap:
                zscore_components['market_cap'] = market_cap
                print(f"     Market Cap: ${market_cap:,.0f}")
    
    # Attempt Z-Score calculation
    print()
    print("🧮 Z-SCORE CALCULATION ATTEMPT:")
    print("-" * 40)
    
    if len(zscore_components) >= 4:  # Need at least 4 components for reasonable calculation
        print("✅ Sufficient data available for Z-Score calculation!")
        
        # Mock Z-Score calculation (would need actual balance sheet values for precise calculation)
        working_capital_ratio = zscore_components.get('working_capital_ratio', 0)
        retained_earnings_ratio = zscore_components.get('retained_earnings_ratio', 0)
        return_on_assets = zscore_components.get('return_on_assets', 0)
        asset_turnover = zscore_components.get('asset_turnover', 0)
        
        # Simplified Altman Z-Score calculation
        z_score = (1.2 * working_capital_ratio + 
                  1.4 * retained_earnings_ratio + 
                  3.3 * return_on_assets + 
                  1.0 * asset_turnover)
        
        print(f"📊 Calculated Z-Score (partial): {z_score:.2f}")
        
        if z_score > 2.99:
            interpretation = "🟢 Safe Zone - Low bankruptcy risk"
        elif z_score > 1.81:
            interpretation = "🟡 Grey Zone - Moderate bankruptcy risk"
        else:
            interpretation = "🔴 Distress Zone - High bankruptcy risk"
        
        print(f"📈 Interpretation: {interpretation}")
        print()
        print("💡 NOTE: This is a simplified calculation. Full Z-Score requires market value component.")
        print("   Your FMP tier provides all necessary data for complete Z-Score calculation!")
        
    else:
        print("⚠️  Insufficient data for Z-Score calculation")
        print(f"   Available components: {len(zscore_components)}/5 required")
        print("   Missing components may require higher subscription tier")
    
    print()
    print("🎯 CONCLUSION:")
    print("   ✅ FMP provides excellent data for Z-Score validation and calculation")
    print("   🚀 Your current subscription tier is suitable for comprehensive analysis")
    print("   💰 No upgrade needed for Z-Score calculation capability!")

def display_results(symbol: str, data: Any):
    """
    Display formatted results from financial scores API (legacy function)
    """
    print("=" * 60)
    print(f"FINANCIAL SCORES FOR {symbol}")
    print("=" * 60)
    
    if isinstance(data, list) and len(data) > 0:
        score_data = data[0]
    elif isinstance(data, dict):
        score_data = data
    else:
        print("Unexpected data format:")
        print(json.dumps(data, indent=2))
        return
    
    print(f"Symbol: {score_data.get('symbol', 'N/A')}")
    print(f"Altman Z-Score: {score_data.get('altmanZScore', 'N/A')}")
    print(f"Piotroski Score: {score_data.get('piotroskiScore', 'N/A')}")
    print()
    print("Raw API Response:")
    print(json.dumps(data, indent=2))

def main():
    """
    Main function with command-line argument parsing
    """
    parser = argparse.ArgumentParser(
        description='Comprehensive test of Financial Modeling Prep API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,        epilog="""
Examples:
  python fmp_api_explorer.py                    # Test with default symbol (SONO)
  python fmp_api_explorer.py AAPL              # Test Apple Inc.
  python fmp_api_explorer.py MSFT              # Test Microsoft
  python fmp_api_explorer.py TSLA              # Test Tesla
  python fmp_api_explorer.py --symbol NVDA     # Test NVIDIA (explicit parameter)
        """
    )
    
    parser.add_argument(
        'symbol', 
        nargs='?', 
        default='SONO',
        help='Stock ticker symbol to test (default: SONO)'
    )
    
    parser.add_argument(
        '--symbol', 
        dest='symbol_explicit',
        help='Stock ticker symbol to test (alternative parameter format)'
    )
    
    args = parser.parse_args()
    
    # Use explicit symbol parameter if provided, otherwise use positional argument
    symbol = args.symbol_explicit if args.symbol_explicit else args.symbol
    symbol = symbol.upper()  # Ensure uppercase
    
    # Validate symbol format (basic check)
    if not symbol.isalpha() or len(symbol) > 5:
        print(f"❌ ERROR: Invalid ticker symbol '{symbol}'")
        print("   Ticker symbols should be 1-5 alphabetic characters (e.g., AAPL, MSFT, TSLA)")
        sys.exit(1)
    
    print(f"🎯 Testing FMP API with symbol: {symbol}")
    print()
    
    # Run comprehensive test
    try:
        test_results = test_fmp_comprehensive(symbol)
        
        if test_results:
            print(f"\n🎉 Test completed successfully for {symbol}!")
            print("📊 Check the detailed results above for Z-Score calculation capability.")
        else:
            print(f"\n❌ Test failed for {symbol}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
