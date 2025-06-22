#!/usr/bin/env python
"""
Financial Modeling Prep Subscription Tier Analysis
Tests various endpoints to determine subscription requirements for each feature
"""

import os
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import certifi
from dotenv import load_dotenv

def get_jsonparsed_data(url, show_errors=False):
    """Fetch and parse JSON data from URL with error handling"""
    try:
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data), None
    except HTTPError as e:
        error_info = {
            "code": e.code,
            "reason": e.reason,
            "subscription_required": e.code == 402
        }
        
        # Try to read error response body for more details
        try:
            error_body = e.read().decode("utf-8")
            error_info["details"] = error_body
        except:
            pass
            
        if show_errors:
            print(f"  ❌ HTTP {e.code}: {e.reason}")
            if e.code == 402:
                print("     💰 Requires paid subscription")
        
        return None, error_info
    except Exception as e:
        if show_errors:
            print(f"  ❌ Error: {e}")
        return None, {"error": str(e)}

def analyze_subscription_requirements():
    """Analyze FMP API endpoints to determine subscription tier requirements"""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('FINANCIAL_MODELING_PREP_API_KEY')
    
    if not api_key:
        print("ERROR: FINANCIAL_MODELING_PREP_API_KEY not found")
        return
    
    api_key = api_key.strip('"')
    symbol = "SONO"  # Test with SONO
    
    print("=" * 80)
    print("FINANCIAL MODELING PREP - SUBSCRIPTION TIER ANALYSIS")
    print("=" * 80)
    print(f"Testing with symbol: {symbol}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Define endpoint categories with their features
    endpoint_categories = {
        "Basic Company Data (Usually Free)": [
            ("Company Profile", f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}"),
            ("Stock Quote", f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"),
            ("Company Search", f"https://financialmodelingprep.com/api/v3/search?query={symbol}&apikey={api_key}"),
        ],
        
        "Financial Statements (Basic/Standard Tier)": [
            ("Income Statement", f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={api_key}"),
            ("Balance Sheet", f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?apikey={api_key}"),
            ("Cash Flow Statement", f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?apikey={api_key}"),
            ("Income Statement (Quarterly)", f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?period=quarter&apikey={api_key}"),
            ("Balance Sheet (Quarterly)", f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?period=quarter&apikey={api_key}"),
        ],
        
        "Financial Ratios & Metrics (Standard Tier)": [
            ("Financial Ratios", f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?apikey={api_key}"),
            ("Key Metrics", f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?apikey={api_key}"),
            ("Financial Growth", f"https://financialmodelingprep.com/api/v3/financial-growth/{symbol}?apikey={api_key}"),
            ("Enterprise Values", f"https://financialmodelingprep.com/api/v3/enterprise-values/{symbol}?apikey={api_key}"),
        ],
        
        "Advanced Ratios & Analysis (Premium Tier)": [
            ("Financial Ratios TTM", f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={api_key}"),
            ("Key Metrics TTM", f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={api_key}"),
            ("Company Rating", f"https://financialmodelingprep.com/api/v3/rating/{symbol}?apikey={api_key}"),
            ("DCF Valuation", f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{symbol}?apikey={api_key}"),
        ],
        
        "Pre-computed Scores (Premium Tier)": [
            ("Financial Scores", f"https://financialmodelingprep.com/stable/financial-scores?symbol={symbol}&apikey={api_key}"),
            ("Altman Z-Score", f"https://financialmodelingprep.com/api/v4/score?symbol={symbol}&apikey={api_key}"),
            ("Company Grade", f"https://financialmodelingprep.com/api/v3/grade/{symbol}?apikey={api_key}"),
        ],
        
        "Market Data & Analysis (Various Tiers)": [
            ("Stock Price Target", f"https://financialmodelingprep.com/api/v4/price-target?symbol={symbol}&apikey={api_key}"),
            ("Analyst Estimates", f"https://financialmodelingprep.com/api/v3/analyst-estimates/{symbol}?apikey={api_key}"),
            ("Institutional Holders", f"https://financialmodelingprep.com/api/v3/institutional-holder/{symbol}?apikey={api_key}"),
            ("Insider Trading", f"https://financialmodelingprep.com/api/v4/insider-trading?symbol={symbol}&apikey={api_key}"),
        ],
    }
    
    tier_analysis = {
        "free": {"successful": [], "failed": []},
        "basic": {"successful": [], "failed": []},
        "standard": {"successful": [], "failed": []},
        "premium": {"successful": [], "failed": []}
    }
    
    # Test each category
    for category, endpoints in endpoint_categories.items():
        print(f"\n📊 {category}")
        print("-" * 60)
        
        category_results = {"successful": 0, "failed": 0, "premium_required": 0}
        
        for name, url in endpoints:
            print(f"Testing {name}...", end=" ")
            
            data, error = get_jsonparsed_data(url, show_errors=False)
            
            if data is not None:
                print("✅ SUCCESS")
                category_results["successful"] += 1
                
                # Categorize by likely tier
                if "Company" in category or "Stock Quote" in name:
                    tier_analysis["free"]["successful"].append(name)
                elif "Financial Statements" in category:
                    tier_analysis["basic"]["successful"].append(name)
                elif "Ratios & Metrics" in category and "TTM" not in name:
                    tier_analysis["standard"]["successful"].append(name)
                else:
                    tier_analysis["premium"]["successful"].append(name)
                    
            elif error and error.get("code") == 402:
                print("❌ PREMIUM REQUIRED")
                category_results["premium_required"] += 1
                tier_analysis["premium"]["failed"].append(name)
            else:
                print("❌ FAILED")
                category_results["failed"] += 1
        
        # Category summary
        total_tests = category_results["successful"] + category_results["failed"] + category_results["premium_required"]
        if total_tests > 0:
            success_rate = (category_results["successful"] / total_tests) * 100
            print(f"\nCategory Summary: {category_results['successful']}/{total_tests} accessible ({success_rate:.0f}%)")
            if category_results["premium_required"] > 0:
                print(f"                  {category_results['premium_required']} require premium subscription")
    
    # Overall subscription analysis
    print("\n" + "=" * 80)
    print("SUBSCRIPTION TIER ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Determine current subscription level
    total_successful = sum(len(tier["successful"]) for tier in tier_analysis.values())
    total_premium_failed = len(tier_analysis["premium"]["failed"])
    
    if total_successful >= 8 and total_premium_failed > 0:
        current_tier = "STANDARD/PROFESSIONAL"
        tier_color = "🟡"
    elif total_successful >= 5:
        current_tier = "BASIC/STARTER"
        tier_color = "🟢"
    elif total_successful >= 2:
        current_tier = "FREE"
        tier_color = "🔵"
    else:
        current_tier = "LIMITED/RESTRICTED"
        tier_color = "🔴"
    
    print(f"{tier_color} Current Subscription Level: {current_tier}")
    print(f"📊 Total Accessible Endpoints: {total_successful}")
    print(f"🔒 Premium-Only Endpoints: {total_premium_failed}")
    
    # Feature availability breakdown
    print(f"\n📋 FEATURE AVAILABILITY BY TIER:")
    print(f"✅ Available with your current subscription:")
    for tier_name, tier_data in tier_analysis.items():
        if tier_data["successful"]:
            print(f"   {tier_name.upper()}: {', '.join(tier_data['successful'])}")
    
    print(f"\n❌ Requires higher subscription tier:")
    for tier_name, tier_data in tier_analysis.items():
        if tier_data["failed"]:
            print(f"   {tier_name.upper()}: {', '.join(tier_data['failed'])}")
    
    # Specific recommendations for enhanced features
    print(f"\n🎯 ENHANCED FEATURES SUBSCRIPTION REQUIREMENTS:")
    print(f"📊 Pre-computed Financial Ratios: {'✅ Available' if tier_analysis['standard']['successful'] else '❌ Requires STANDARD+ tier'}")
    print(f"📈 Standardized Financial Statements: {'✅ Available' if tier_analysis['basic']['successful'] else '❌ Requires BASIC+ tier'}")
    print(f"💰 Enterprise Value & Advanced Valuation: {'✅ Available' if tier_analysis['standard']['successful'] else '❌ Requires STANDARD+ tier'}")
    print(f"🏭 Industry-Specific Metrics: {'✅ Available' if tier_analysis['premium']['successful'] else '❌ Requires PREMIUM tier'}")
    print(f"🎯 Pre-computed Z-Scores: {'✅ Available' if not tier_analysis['premium']['failed'] else '❌ Requires PREMIUM tier'}")
    
    # Cost-benefit analysis
    print(f"\n💡 RECOMMENDATIONS:")
    if total_premium_failed == 0:
        print("🎉 You have access to all tested features! Your current subscription is sufficient.")
    elif total_successful >= 8:
        print("📈 Consider upgrading to PREMIUM for pre-computed scores and advanced analytics.")
        print("   Current tier gives you excellent validation capabilities.")
    else:
        print("🚀 Consider upgrading to STANDARD for comprehensive financial statement access.")
        print("   This would unlock most validation features you need.")
    
    return tier_analysis

if __name__ == "__main__":
    analyze_subscription_requirements()
