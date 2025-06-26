#!/usr/bin/env python3
"""
Enterprise Risk-Return Analysis Demo
v4.2.0 Feature Showcase

This script demonstrates the advanced risk-return analysis capabilities
of the Altman Z-Score Analysis System v4.2.0.

Features Demonstrated:
1. Multi-dimensional risk assessment
2. Investment recommendation engine  
3. Sector-specific benchmarking
4. Portfolio allocation suggestions
5. Comprehensive risk metrics
"""

import asyncio
import json
from datetime import datetime

from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.analysis import analyze_single_security, RiskLevel


async def demonstrate_enterprise_analysis():
    """Demonstrate enterprise risk-return analysis features."""
    
    print("=" * 80)
    print("🚀 ALTMAN Z-SCORE ANALYSIS SYSTEM v4.2.0")
    print("   Enterprise Risk-Return Analysis Engine")
    print("=" * 80)
    print()
    
    # Demo companies with different risk profiles
    demo_companies = [
        {
            "name": "TechCorp (High Quality Tech)",
            "data": MergedFinancialData(
                ticker="TECH",
                timestamp="2024-12-31",
                working_capital_ratio=1.8,
                retained_earnings_ratio=0.6,
                ebit_ratio=0.35,
                asset_turnover=0.7,
                current_ratio=2.5,
                debt_to_equity=0.2,
                market_cap=500_000_000_000,  # $500B
                data_quality_score=0.98
            ),
            "sector": "technology"
        },
        {
            "name": "ManufacturingCo (Stable Industrial)",
            "data": MergedFinancialData(
                ticker="MANUF",
                timestamp="2024-12-31",
                working_capital_ratio=1.1,
                retained_earnings_ratio=0.3,
                ebit_ratio=0.12,
                asset_turnover=1.2,
                current_ratio=1.5,
                debt_to_equity=0.6,
                market_cap=50_000_000_000,  # $50B
                data_quality_score=0.85
            ),
            "sector": "manufacturing"
        },
        {
            "name": "RetailChain (Competitive Retail)",
            "data": MergedFinancialData(
                ticker="RETAIL",
                timestamp="2024-12-31",
                working_capital_ratio=0.8,
                retained_earnings_ratio=0.2,
                ebit_ratio=0.08,
                asset_turnover=2.5,
                current_ratio=1.2,
                debt_to_equity=1.2,
                market_cap=25_000_000_000,  # $25B
                data_quality_score=0.80
            ),
            "sector": "retail"
        },
        {
            "name": "DistresSED Corp (Financial Troubles)",
            "data": MergedFinancialData(
                ticker="TROUBLE",
                timestamp="2024-12-31",
                working_capital_ratio=-0.2,
                retained_earnings_ratio=-0.1,
                ebit_ratio=-0.05,
                asset_turnover=0.4,
                current_ratio=0.7,
                debt_to_equity=4.0,
                market_cap=500_000_000,  # $500M
                data_quality_score=0.65
            ),
            "sector": "manufacturing"
        }
    ]
    
    print("📊 ANALYZING PORTFOLIO OF COMPANIES")
    print("   Demonstrating multi-dimensional risk assessment")
    print()
    
    results = []
    
    for i, company in enumerate(demo_companies, 1):
        print(f"[{i}/4] Analyzing: {company['name']}")
        print(f"      Ticker: {company['data'].ticker}")
        print(f"      Sector: {company['sector']}")
        print(f"      Market Cap: ${company['data'].market_cap:,.0f}")
        
        # Perform enterprise analysis
        try:
            recommendation = await analyze_single_security(
                company['data'], 
                sector=company['sector']
            )
            results.append((company, recommendation))
            
            print(f"      ✓ Analysis Complete")
            print()
            
        except Exception as e:
            print(f"      ❌ Analysis Failed: {e}")
            print()
            continue
    
    # Display comprehensive results
    print("=" * 80)
    print("📈 ENTERPRISE ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    for company, recommendation in results:
        print(f"🏢 {company['name']} ({recommendation.ticker})")
        print(f"   Sector: {company['sector'].title()}")
        print()
        
        # Investment Recommendation
        action_colors = {
            "strong_buy": "🟢",
            "buy": "🟢", 
            "hold": "🟡",
            "sell": "🟠",
            "strong_sell": "🔴"
        }
        action_color = action_colors.get(recommendation.action.value, "⚪")
        
        print(f"   {action_color} INVESTMENT RECOMMENDATION: {recommendation.action.value.upper()}")
        print(f"   📊 Confidence Level: {recommendation.confidence:.1%}")
        print(f"   ⚠️  Risk Level: {recommendation.risk_level.value.upper()}")
        print(f"   ⏰ Time Horizon: {recommendation.time_horizon}")
        print()
        
        # Risk Metrics
        print("   🎯 COMPREHENSIVE RISK METRICS:")
        print(f"      Z-Score: {recommendation.risk_metrics.z_score:.2f} ({recommendation.risk_metrics.risk_category})")
        print(f"      Bankruptcy Probability: {recommendation.risk_metrics.bankruptcy_probability:.1%}")
        print(f"      Financial Strength: {recommendation.risk_metrics.financial_strength_score:.1%}")
        print(f"      Liquidity Risk: {recommendation.risk_metrics.liquidity_risk_score:.1%}")
        print(f"      Operational Risk: {recommendation.risk_metrics.operational_risk_score:.1%}")
        print(f"      Market Risk: {recommendation.risk_metrics.market_risk_score:.1%}")
        print(f"      Overall Risk Score: {recommendation.risk_metrics.overall_risk_score:.1%}")
        print()
        
        # Portfolio Context
        print("   💼 PORTFOLIO ALLOCATION:")
        print(f"      Suggested Weight: {recommendation.portfolio_weight_suggestion:.1%}")
        if recommendation.correlation_risks:
            print(f"      Correlation Risks: {', '.join(recommendation.correlation_risks)}")
        print()
        
        # Investment Reasoning
        print("   💡 ANALYSIS REASONING:")
        for reason in recommendation.reasoning:
            print(f"      • {reason}")
        print()
        
        # Sector Benchmarking
        if recommendation.risk_metrics.peer_comparison_score is not None:
            if recommendation.risk_metrics.peer_comparison_score > 0.2:
                benchmark_status = "📈 Above sector average"
            elif recommendation.risk_metrics.peer_comparison_score < -0.2:
                benchmark_status = "📉 Below sector average"
            else:
                benchmark_status = "📊 Near sector average"
            
            print(f"   🏭 SECTOR BENCHMARK: {benchmark_status}")
            print(f"      Peer Comparison Score: {recommendation.risk_metrics.peer_comparison_score:+.2f}")
        print()
        
        print("-" * 80)
        print()
    
    # Portfolio Summary
    print("🎯 PORTFOLIO OPTIMIZATION SUMMARY")
    print("=" * 80)
    print()
    
    total_allocation = sum(r.portfolio_weight_suggestion for _, r in results)
    risk_distribution = {}
    
    for company, recommendation in results:
        risk_level = recommendation.risk_level.value
        if risk_level not in risk_distribution:
            risk_distribution[risk_level] = 0
        risk_distribution[risk_level] += recommendation.portfolio_weight_suggestion
    
    print(f"📊 Total Suggested Allocation: {total_allocation:.1%}")
    print(f"💰 Remaining Cash Position: {1-total_allocation:.1%}")
    print()
    
    print("📈 Risk Distribution:")
    for risk_level, allocation in risk_distribution.items():
        percentage = allocation / total_allocation * 100 if total_allocation > 0 else 0
        print(f"   {risk_level.title()}: {allocation:.1%} ({percentage:.1f}% of portfolio)")
    print()
    
    # Investment Actions Summary  
    actions_summary = {}
    for _, recommendation in results:
        action = recommendation.action.value
        if action not in actions_summary:
            actions_summary[action] = 0
        actions_summary[action] += 1
    
    print("🎯 Investment Actions Summary:")
    for action, count in actions_summary.items():
        print(f"   {action.replace('_', ' ').title()}: {count} companies")
    print()
    
    print("=" * 80)
    print("✅ ENTERPRISE ANALYSIS COMPLETE")
    print(f"   Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Total companies analyzed: {len(results)}")
    print(f"   Analysis engine: Altman Z-Score v4.2.0 Enterprise")
    print("=" * 80)


def main():
    """Main execution function."""
    print("Starting Enterprise Risk-Return Analysis Demo...")
    print()
    
    try:
        # Run the async demonstration
        asyncio.run(demonstrate_enterprise_analysis())
        
        print()
        print("🎉 Demo completed successfully!")
        print()
        print("Key Features Demonstrated:")
        print("• Multi-dimensional risk assessment beyond traditional Z-Score")
        print("• AI-powered investment recommendations with confidence scoring")
        print("• Sector-specific benchmarking and peer comparison")
        print("• Portfolio allocation optimization and correlation analysis")
        print("• Enterprise-grade analysis with comprehensive risk metrics")
        print()
        print("For more information about v4.2.0 enterprise features:")
        print("• See V4.2.0_PROGRESS_REPORT.md")
        print("• Review altman_zscore/layers/analysis/ module")
        print("• Run test suite: python -m pytest tests/unit/test_risk_return_analysis.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please ensure all dependencies are installed and the system is properly configured.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
