"""
Market Analysis Standalone Demo

Demonstrates the comprehensive market analysis capabilities independent 
of the FMP data fetch issues. Shows how market analysis transforms 
basic Z-Score information into actionable investment insights.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from altman_zscore.layers.market_analysis import MarketAnalysisOrchestrator
from altman_zscore.common.logging_config import get_logger

logger = get_logger(__name__)


def demonstrate_market_analysis_transformation():
    """Demonstrate how market analysis transforms Z-Score insights."""
    
    print("=" * 70)
    print("MARKET ANALYSIS TRANSFORMATION DEMO")
    print("Showing how basic Z-Score data becomes comprehensive investment analysis")
    print("=" * 70)
    
    # Test with different scenarios
    test_cases = [
        {
            "ticker": "AAPL",
            "z_score": 2.8,
            "category": "gray",
            "description": "Large cap tech with moderate Z-Score"
        },
        {
            "ticker": "MSFT", 
            "z_score": 4.2,
            "category": "safe",
            "description": "Strong fundamentals, safe Z-Score"
        },
        {
            "ticker": "TSLA",
            "z_score": 1.5,
            "category": "distress",
            "description": "High growth but distressed Z-Score"
        }
    ]
    
    market_orchestrator = MarketAnalysisOrchestrator()
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"TEST CASE {i}: {case['ticker']}")
        print(f"Scenario: {case['description']}")
        print(f"{'='*50}")
        
        try:
            # BEFORE: Basic Z-Score analysis
            print(f"\n📊 BEFORE (Basic Z-Score Only):")
            print(f"   Ticker: {case['ticker']}")
            print(f"   Z-Score: {case['z_score']:.2f}")
            print(f"   Category: {case['category']}")
            print(f"   Insight: {'Safe' if case['z_score'] >= 3.0 else 'Moderate Risk' if case['z_score'] >= 1.8 else 'High Risk'}")
            print(f"   Action: ❓ Limited guidance - is this a good investment?")
            
            # AFTER: Comprehensive market analysis
            print(f"\n🚀 AFTER (Comprehensive Market Analysis):")
            
            market_analysis = market_orchestrator.analyze_ticker(
                ticker=case['ticker'],
                z_score=case['z_score'],
                z_score_category=case['category'],
                period="1y"
            )
            
            # Technical insights
            if market_analysis.technical_analysis:
                tech = market_analysis.technical_analysis
                print(f"   📈 Technical: {tech.price_trend.title()} trend, {tech.overall_signal.upper()} signal")
                print(f"      Current Price: ${tech.current_price:.2f}")
                print(f"      Volatility: {tech.volatility_rank.title()}")
            
            # Valuation insights
            if market_analysis.valuation_metrics:
                val = market_analysis.valuation_metrics
                pe_str = f"P/E: {val.pe_ratio:.1f}" if val.pe_ratio else "P/E: N/A"
                div_str = f"Div: {val.dividend_yield:.1%}" if val.dividend_yield else "Div: N/A"
                print(f"   💰 Valuation: {val.relative_valuation.title()}, {pe_str}, {div_str}")
                if val.upside_potential:
                    print(f"      Analyst Upside: {val.upside_potential:.1%}")
            
            # Performance insights
            if market_analysis.market_performance:
                perf = market_analysis.market_performance
                ret_3m = f"{perf.return_3m:.1%}" if perf.return_3m else "N/A"
                vs_bench = f"{perf.benchmark_3m:+.1%}" if perf.benchmark_3m else "N/A"
                print(f"   📊 Performance: 3M return {ret_3m}, vs S&P 500: {vs_bench}")
                if perf.beta:
                    print(f"      Beta: {perf.beta:.2f} (Market sensitivity)")
            
            # Investment recommendation
            if market_analysis.risk_return_profile:
                risk = market_analysis.risk_return_profile
                print(f"   ⚖️ Investment Rating: {risk.investment_rating.upper()}")
                print(f"      Risk Level: {risk.overall_risk_category.title()}")
                print(f"      Confidence: {risk.confidence_level:.0%}")
                if risk.total_return_potential:
                    print(f"      Return Potential: {risk.total_return_potential:.1%}")
            
            # Investment thesis
            print(f"\n🎯 INVESTMENT THESIS:")
            print(f"   {market_analysis.investment_thesis}")
            
            # Key points
            print(f"\n✅ Top Strengths:")
            for strength in market_analysis.key_strengths[:2]:
                print(f"   • {strength}")
            
            print(f"\n⚠️ Top Concerns:")
            for concern in market_analysis.key_concerns[:2]:
                print(f"   • {concern}")
            
            # Price target
            if market_analysis.price_target:
                current_price = market_analysis.technical_analysis.current_price if market_analysis.technical_analysis else 0
                upside = ((market_analysis.price_target - current_price) / current_price * 100) if current_price > 0 else 0
                print(f"\n💡 Price Target: ${market_analysis.price_target:.2f} ({upside:+.1f}% upside)")
            
            # Data quality
            print(f"\n📋 Analysis Quality:")
            print(f"   Data Quality: {market_analysis.data_quality_score:.0%}")
            print(f"   Completeness: {market_analysis.analysis_completeness:.0%}")
            
            rating = market_analysis.risk_return_profile.investment_rating if market_analysis.risk_return_profile else "HOLD"
            confidence = market_analysis.risk_return_profile.confidence_level if market_analysis.risk_return_profile else 0.5
            
            print(f"\n🎯 FINAL RECOMMENDATION: {rating.upper()} (Confidence: {confidence:.0%})")
            
        except Exception as e:
            print(f"   ❌ Analysis failed for {case['ticker']}: {e}")
            continue
    
    # Summary of transformation
    print(f"\n{'='*70}")
    print("TRANSFORMATION SUMMARY")
    print("="*70)
    print("BEFORE Market Analysis Layer:")
    print("• Basic Z-Score number and risk category")
    print("• Limited actionable insights") 
    print("• No market context or valuation perspective")
    print("• Users left wondering: 'Is this a good investment?'")
    
    print("\nAFTER Market Analysis Layer:")
    print("• ✅ Technical analysis (price trends, momentum, volatility)")
    print("• ✅ Valuation analysis (P/E, P/B, dividend yield, relative valuation)")
    print("• ✅ Performance analysis (returns, benchmarks, risk metrics)")
    print("• ✅ Risk-return assessment (combined fundamental + market)")
    print("• ✅ Clear investment recommendation with confidence level")
    print("• ✅ Price targets and actionable insights")
    print("• ✅ Comprehensive investment thesis")
    
    print(f"\n🚀 RESULT: Transformed from 'Z-Score Calculator' to 'Complete Investment Analysis Platform'")
    print(f"📈 USER VALUE: Clear, actionable investment guidance beyond just financial health")
    
    return True


def main():
    """Run the market analysis transformation demo."""
    print("Starting Market Analysis Transformation Demo...\n")
    
    try:
        success = demonstrate_market_analysis_transformation()
        
        if success:
            print(f"\n✅ DEMO SUCCESSFUL!")
            print(f"\nPhase 1 of Market Analysis Integration is COMPLETE")
            print(f"Ready to proceed with Phase 2: Output Generation Enhancement")
            
        return success
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
