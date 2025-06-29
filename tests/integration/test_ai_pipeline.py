"""
Test Script for Comprehensive AI Analysis Pipeline

This script tests the complete AI-enhanced analysis pipeline including:
1. Data Quality Analysis
2. Peer Comparison Analysis
3. Market Sentiment Analysis  
4. Risk Factor Analysis
5. Dashboard Integration
6. LLM Final Commentary

Usage: python test_ai_pipeline.py [TICKER]
"""

import asyncio
import sys
from pathlib import Path
import logging

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.common.logging_config import get_logger

logger = get_logger(__name__)


async def test_comprehensive_ai_analysis(ticker: str = "AAPL"):
    """
    Test the comprehensive AI analysis pipeline end-to-end.
    
    Args:
        ticker: Stock ticker to analyze
    """
    print(f"\n{'='*60}")
    print(f"Testing Comprehensive AI Analysis Pipeline")
    print(f"Ticker: {ticker}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize pipeline
        pipeline = AltmanZScorePipeline(output_base_path="test_output")
        
        # Run complete analysis with all AI features enabled
        print("🚀 Starting comprehensive analysis...")
        results = await pipeline.analyze_ticker(
            ticker=ticker,
            generate_charts=True,
            generate_reports=True,
            include_ai_insights=True,
            include_comprehensive_ai_analysis=True,
            include_market_analysis=True,
            enhanced_analysis=False,  # Use basic mode for testing
            quarters=4
        )
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"Generated {len(results)} output files:")
        
        for file_type, file_path in results.items():
            if 'error' not in file_type:
                print(f"  📄 {file_type.upper()}: {file_path}")
        
        # Test AI orchestrator directly
        print(f"\n🧠 Testing AI Orchestrator directly...")
        
        # Get financial data for direct AI testing
        merged_data = await pipeline.data_merger.merge_financial_data(ticker, quarters=4)
        if isinstance(merged_data, list):
            financial_data = merged_data[0]
        else:
            financial_data = merged_data
        
        # Run comprehensive AI analysis
        ai_results = await pipeline.ai_orchestrator.perform_comprehensive_analysis(
            financial_data,
            include_data_quality=True,
            include_peer_analysis=True,
            include_sentiment=True,
            include_risk_analysis=True,
            generate_final_commentary=True
        )
        
        print(f"\n📊 AI Analysis Results Summary:")
        print(f"  Overall Confidence: {ai_results.overall_ai_confidence:.1%}")
        print(f"  Recommendations: {len(ai_results.ai_recommendations)}")
        
        # Display key insights from each AI component
        if ai_results.data_quality:
            print(f"\n📈 Data Quality:")
            print(f"  Score: {ai_results.data_quality.overall_quality_score}/100")
            print(f"  Rating: {ai_results.data_quality.reliability_rating}")
            print(f"  Issues: {len(ai_results.data_quality.quality_issues)}")
        
        if ai_results.peer_analysis:
            print(f"\n🏢 Peer Analysis:")
            print(f"  Position: {ai_results.peer_analysis.relative_position}")
            print(f"  Industry Avg Z-Score: {ai_results.peer_analysis.industry_average_z_score:.2f}")
            print(f"  Peers Identified: {len(ai_results.peer_analysis.identified_peers)}")
        
        if ai_results.sentiment_analysis:
            print(f"\n💭 Sentiment Analysis:")
            sentiment_desc = _describe_sentiment(ai_results.sentiment_analysis.overall_sentiment_score)
            print(f"  Overall Sentiment: {sentiment_desc}")
            print(f"  Trend: {ai_results.sentiment_analysis.sentiment_trend}")
            if ai_results.sentiment_analysis.fundamental_sentiment_divergence:
                print(f"  Divergence: {ai_results.sentiment_analysis.fundamental_sentiment_divergence}")
        
        if ai_results.risk_analysis:
            print(f"\n⚠️ Risk Analysis:")
            risk_desc = _describe_risk(ai_results.risk_analysis.overall_risk_score)
            print(f"  Risk Level: {risk_desc}")
            print(f"  Trajectory: {ai_results.risk_analysis.risk_trajectory}")
            print(f"  Risk Factors: {len(ai_results.risk_analysis.identified_risks)}")
        
        # Display LLM final commentary
        if ai_results.llm_final_commentary:
            print(f"\n🎯 LLM Final Commentary:")
            print(f"  {ai_results.llm_final_commentary[:300]}...")
        
        # Display dashboard summary
        if ai_results.dashboard_summary:
            print(f"\n📊 Dashboard Integration:")
            print(f"  Key Insights: {len(ai_results.dashboard_summary.get('key_insights', []))}")
            print(f"  Metrics Available: {list(ai_results.dashboard_summary.get('metrics', {}).keys())}")
        
        print(f"\n✅ End-to-end AI pipeline test completed successfully!")
        print(f"📁 Output files available in: test_output/{ticker}/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.error(f"AI pipeline test failed: {str(e)}", exc_info=True)
        return False


def _describe_sentiment(sentiment_score: float) -> str:
    """Convert sentiment score to descriptive text."""
    if sentiment_score > 0.6:
        return "Very Positive"
    elif sentiment_score > 0.2:
        return "Positive"
    elif sentiment_score > -0.2:
        return "Neutral"
    elif sentiment_score > -0.6:
        return "Negative"
    else:
        return "Very Negative"


def _describe_risk(risk_score: float) -> str:
    """Convert risk score to descriptive text."""
    if risk_score > 0.8:
        return "Very High Risk"
    elif risk_score > 0.6:
        return "High Risk"
    elif risk_score > 0.4:
        return "Moderate Risk"
    elif risk_score > 0.2:
        return "Low-Moderate Risk"
    else:
        return "Low Risk"


async def main():
    """Main test function."""
    # Get ticker from command line or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Run the comprehensive test
    success = await test_comprehensive_ai_analysis(ticker)
    
    if success:
        print(f"\n🎉 All tests passed! The comprehensive AI analysis pipeline is working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 Tests failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    # Set up logging for test
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    asyncio.run(main())
