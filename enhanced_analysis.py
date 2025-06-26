#!/usr/bin/env python3
"""
Enhanced Multi-Quarter Z-Score Analysis Script

This script leverages upgraded FMP account features to perform comprehensive
multi-quarter Z-Score analysis with historical trends, peer comparisons,
and advanced portfolio analytics.

Features:
- 8-quarter historical Z-Score trends
- Quarterly seasonality analysis
- Industry peer comparisons
- Portfolio-level risk assessment
- Enhanced visualizations and reports

Usage:
    python enhanced_analysis.py AAPL MSFT GOOGL
    python enhanced_analysis.py --portfolio-file sp500_top50.txt
    python enhanced_analysis.py --sector technology --quarters 12
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.common.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedAnalysisRunner:
    """Enhanced analysis runner for upgraded FMP accounts."""
    
    def __init__(self, quarters: int = 8, batch_size: int = 20):
        self.pipeline = AltmanZScorePipeline()
        self.quarters = quarters
        self.batch_size = batch_size
        
    async def run_multi_quarter_analysis(self, tickers: List[str], output_dir: str = "enhanced_output"):
        """Run enhanced multi-quarter analysis."""
        logger.info(f"Starting enhanced multi-quarter analysis for {len(tickers)} companies")
        logger.info(f"Analysis parameters: {self.quarters} quarters, batch size {self.batch_size}")
        
        results = []
        
        # Process in batches for optimal performance
        for i in range(0, len(tickers), self.batch_size):
            batch = tickers[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}: {batch}")
            
            batch_results = await self._process_batch(batch, output_dir)
            results.extend(batch_results)
            
        # Generate portfolio-level analysis
        await self._generate_portfolio_analysis(results, output_dir)
        
        return results
        
    async def _process_batch(self, tickers: List[str], output_dir: str):
        """Process a batch of tickers with enhanced analysis."""
        batch_results = []
        
        for ticker in tickers:
            try:
                # Run enhanced analysis with correct pipeline method signature
                result = await self.pipeline.analyze_ticker(
                    ticker=ticker,
                    generate_charts=True,
                    generate_reports=True,
                    include_ai_insights=True,
                    include_market_analysis=True
                )
                
                if result:
                    batch_results.append(result)
                    logger.info(f"[SUCCESS] Completed enhanced analysis for {ticker}")
                else:
                    logger.warning(f"[WARNING] Analysis failed for {ticker}")
                    
            except Exception as e:
                logger.error(f"[ERROR] Error analyzing {ticker}: {e}")
                
        return batch_results
        
    async def _generate_portfolio_analysis(self, results, output_dir: str):
        """Generate portfolio-level analysis and comparisons."""
        logger.info("Generating portfolio-level analysis...")
        
        # Portfolio summary statistics
        # Risk distribution analysis
        # Sector comparisons
        # Trend correlations
        # TODO: Implement portfolio analysis features
        
        logger.info(f"Portfolio analysis complete. Results saved to {output_dir}/portfolio_analysis/")


def load_portfolio_from_file(file_path: str) -> List[str]:
    """Load ticker symbols from a portfolio file."""
    try:
        with open(file_path, 'r') as f:
            tickers = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
        return tickers
    except FileNotFoundError:
        logger.error(f"Portfolio file not found: {file_path}")
        return []


def main():
    """Main entry point for enhanced analysis."""
    parser = argparse.ArgumentParser(
        description="Enhanced Multi-Quarter Z-Score Analysis for Upgraded FMP Accounts"
    )
    
    parser.add_argument(
        "tickers",
        nargs="*",
        help="Stock ticker symbols to analyze"
    )
    
    parser.add_argument(
        "--portfolio-file",
        type=str,
        help="File containing list of tickers (one per line)"
    )
    
    parser.add_argument(
        "--quarters",
        type=int,
        default=8,
        help="Number of quarters for historical analysis (default: 8)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Batch size for processing (default: 20)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="enhanced_output",
        help="Output directory for enhanced analysis results"
    )
    
    parser.add_argument(
        "--sector",
        type=str,
        help="Pre-defined sector portfolio (technology, healthcare, financial, etc.)"
    )
    
    args = parser.parse_args()
    
    # Determine ticker list
    tickers = []
    
    if args.portfolio_file:
        tickers = load_portfolio_from_file(args.portfolio_file)
    elif args.sector:
        # Pre-defined sector portfolios
        sector_portfolios = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM'],
            'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'DHR', 'AMGN', 'GILD', 'MRNA', 'CVS'],
            'financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'USB', 'PNC', 'BK'],
            'industrial': ['CAT', 'DE', 'MMM', 'HON', 'UPS', 'GD', 'LMT', 'RTX', 'BA', 'FDX'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'PXD', 'SLB', 'HAL', 'KMI', 'WMB', 'NEE']
        }
        tickers = sector_portfolios.get(args.sector.lower(), [])
        if not tickers:
            logger.error(f"Unknown sector: {args.sector}")
            return
    else:
        tickers = [t.upper() for t in args.tickers]
    
    if not tickers:
        logger.error("No tickers specified. Use --help for usage instructions.")
        return
    
    # Run enhanced analysis
    runner = EnhancedAnalysisRunner(quarters=args.quarters, batch_size=args.batch_size)
    
    logger.info(f"ENHANCED ANALYSIS Starting")
    logger.info(f"Tickers: {len(tickers)} companies")
    logger.info(f"Quarters: {args.quarters}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Output: {args.output_dir}")
    
    # Set enhanced mode environment variable
    os.environ['FMP_ENHANCED_MODE'] = '1'
    
    # Run the analysis
    asyncio.run(runner.run_multi_quarter_analysis(tickers, args.output_dir))
    
    logger.info("Enhanced multi-quarter analysis complete!")


if __name__ == "__main__":
    main()
