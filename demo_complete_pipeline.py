#!/usr/bin/env python3
"""
Complete Pipeline Demonstration
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from altman_zscore.main_pipeline import AltmanZScorePipeline


async def main():
    print("🚀 ALTMAN Z-SCORE COMPLETE PIPELINE DEMONSTRATION")
    print("=" * 60)
    
    pipeline = AltmanZScorePipeline()
    
    test_tickers = ["MSFT", "AAPL", "TSLA"]
    
    for ticker in test_tickers:
        print(f"\n📊 Analyzing {ticker}...")
        print("-" * 40)
        
        try:
            # Run complete analysis
            output_files = await pipeline.analyze_ticker(ticker)
            
            # Read the JSON file to get Z-Score details
            json_file = output_files.get('json')
            if json_file and os.path.exists(json_file):
                import json
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                summary = data['analysis_summary']
                print(f"✅ {ticker} Analysis Complete")
                print(f"   📈 Z-Score: {summary['z_score']}")
                print(f"   🛡️  Risk Category: {summary['risk_category']}")
                print(f"   🧠 Model Used: {summary['model_used']}")
                print(f"   📊 Data Quality: {summary['data_quality_score']}")
                
                print(f"\n📁 Generated Files:")
                for file_type, file_path in output_files.items():
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    print(f"   {file_type.upper()}: {file_path} ({file_size:,} bytes)")
                
            else:
                print(f"⚠️  Could not read analysis results for {ticker}")
                
        except Exception as e:
            print(f"❌ Analysis failed for {ticker}: {e}")
    
    print(f"\n🎉 PIPELINE DEMONSTRATION COMPLETE!")
    print(f"📂 Check the output/ directory for all generated files")
    
    # List all output directories
    output_dir = Path("output")
    if output_dir.exists():
        subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
        print(f"\n📁 Output directories: {', '.join([d.name for d in subdirs])}")


if __name__ == "__main__":
    asyncio.run(main())
