"""
Test script for AI Data Quality Checker

This script demonstrates the new AI-enhanced data quality analysis
capability integrated into the Altman Z-Score pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from altman_zscore.layers.ai_analysis.ai_data_quality_checker import AIDataQualityChecker
from altman_zscore.layers.ai_analysis.ai_orchestrator import AIAnalysisOrchestrator  
from altman_zscore.layers.data_fetch.data_merger import DataMerger
from altman_zscore.common.logging_config import get_logger

logger = get_logger(__name__)


async def test_ai_data_quality():
    """Test the AI data quality checker with real financial data."""
    try:
        print("🤖 Testing AI Data Quality Analysis")
        print("=" * 50)
        
        # Initialize components
        data_merger = DataMerger()
        ai_orchestrator = AIAnalysisOrchestrator()
        
        # Test with a well-known company
        test_ticker = "AAPL"
        print(f"📊 Analyzing data quality for {test_ticker}...")
        
        # Fetch financial data
        financial_data = await data_merger.merge_financial_data(test_ticker)
        if isinstance(financial_data, list):
            financial_data = financial_data[0]  # Use most recent data
        
        print(f"✅ Financial data fetched for {test_ticker}")
        print(f"   Report Date: {financial_data.report_date}")
        print(f"   Market Cap: ${financial_data.market_cap:,.0f}" if financial_data.market_cap else "   Market Cap: Not available")
        
        # Run comprehensive AI analysis (currently just data quality)
        ai_analysis = await ai_orchestrator.perform_comprehensive_analysis(
            financial_data=financial_data,
            include_data_quality=True,
            include_peer_analysis=True,  # Will show "not implemented" message
            include_sentiment=True,      # Will show "not implemented" message
            include_risk_analysis=True   # Will show "not implemented" message
        )
        
        # Display results
        print("\n🔍 AI Data Quality Analysis Results:")
        print("-" * 40)
        
        if ai_analysis.data_quality:
            dq = ai_analysis.data_quality
            print(f"Overall Quality Score: {dq.overall_quality_score:.1f}/100")
            print(f"Reliability Rating: {dq.reliability_rating.upper()}")
            print(f"Completeness: {dq.completeness_score:.1f}/100")
            print(f"Consistency: {dq.consistency_score:.1f}/100") 
            print(f"Accuracy: {dq.accuracy_score:.1f}/100")
            print(f"Anomalies Detected: {len(dq.anomalies_detected)}")
            
            if dq.anomalies_detected:
                print("\n⚠️  Detected Anomalies:")
                for i, anomaly in enumerate(dq.anomalies_detected[:3], 1):  # Show first 3
                    print(f"   {i}. {anomaly.field_name}: {anomaly.description}")
                    print(f"      Severity: {anomaly.severity.upper()}, Confidence: {anomaly.confidence:.1%}")
            
            print(f"\n💡 AI Recommendation:")
            print(f"   {dq.recommendation}")
        
        print(f"\n🎯 Overall AI Confidence: {ai_analysis.overall_ai_confidence:.1%}")
        
        if ai_analysis.ai_recommendations:
            print(f"\n📋 AI Recommendations:")
            for i, rec in enumerate(ai_analysis.ai_recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Show implementation status
        print(f"\n🚀 AI Implementation Status:")
        status = ai_orchestrator.get_implementation_status()
        for component, info in status.items():
            status_emoji = "✅" if info['status'] == 'implemented' else "🔄"
            print(f"   {status_emoji} {component.replace('_', ' ').title()}: {info['status']}")
        
        print(f"\n✅ AI Data Quality Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"AI data quality test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True


async def test_multiple_companies():
    """Test AI data quality analysis with multiple companies."""
    print(f"\n🧪 Testing Multiple Companies")
    print("=" * 50)
    
    test_tickers = ["MSFT", "GOOGL", "TSLA"]
    data_merger = DataMerger()
    ai_quality_checker = AIDataQualityChecker()
    
    results = {}
    
    for ticker in test_tickers:
        try:
            print(f"\n📈 Analyzing {ticker}...")
            
            # Fetch data
            financial_data = await data_merger.merge_financial_data(ticker)
            if isinstance(financial_data, list):
                financial_data = financial_data[0]
            
            # Run AI quality analysis
            quality_metrics = await ai_quality_checker.analyze_data_quality(financial_data)
            
            results[ticker] = {
                'quality_score': quality_metrics.overall_quality_score,
                'reliability': quality_metrics.reliability_rating,
                'anomalies': len(quality_metrics.anomalies_detected)
            }
            
            print(f"   Quality: {quality_metrics.overall_quality_score:.1f}/100 ({quality_metrics.reliability_rating})")
            print(f"   Anomalies: {len(quality_metrics.anomalies_detected)}")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results[ticker] = {'error': str(e)}
    
    # Summary
    print(f"\n📊 Summary Results:")
    print("-" * 30)
    for ticker, result in results.items():
        if 'error' in result:
            print(f"   {ticker}: Error - {result['error'][:50]}...")
        else:
            print(f"   {ticker}: {result['quality_score']:.1f}/100 ({result['reliability']}) - {result['anomalies']} anomalies")


if __name__ == "__main__":
    print("🚀 AI-Enhanced Altman Z-Score Pipeline Test")
    print("Testing Phase 1: Data Quality & Anomaly Detection")
    print("=" * 60)
    
    # Run single company test
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_ai_data_quality())
    
    if success:
        # Run multiple company test
        loop.run_until_complete(test_multiple_companies())
        
        print(f"\n🎉 All tests completed!")
        print(f"📖 See docs/AI_INTEGRATION_PLAN.md for full implementation roadmap")
    else:
        print(f"❌ Primary test failed, skipping additional tests")
