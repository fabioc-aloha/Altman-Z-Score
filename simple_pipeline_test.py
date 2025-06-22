#!/usr/bin/env python3
"""
Simple Pipeline Test - Test data integration and Z-Score calculation
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from altman_zscore.main_pipeline import AltmanZScorePipeline


async def main():
    print("Testing Pipeline Integration...")
    
    # Initialize pipeline
    pipeline = AltmanZScorePipeline()
    print("✅ Pipeline initialized")
    
    # Test data merger
    print("Testing data merger with MSFT...")
    try:
        merged_data = await pipeline.data_merger.merge_financial_data("MSFT")
        print(f"✅ Data merger successful - {merged_data.ticker}")
        print(f"   Market Cap: ${merged_data.market_cap:,.0f}" if merged_data.market_cap else "   Market Cap: N/A")
        
        # Test Z-Score calculation
        print("Testing Z-Score calculation...")
        zscore_result = pipeline.zscore_calculator.calculate_zscore(merged_data)
        print(f"✅ Z-Score calculation successful")
        print(f"   Z-Score: {zscore_result.z_score:.3f}")
        print(f"   Risk Category: {zscore_result.risk_category}")
        print(f"   Model Used: {zscore_result.model_used}")
        
        print("\n🎉 Pipeline integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"Exit code: {0 if success else 1}")
