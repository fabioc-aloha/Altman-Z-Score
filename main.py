#!/usr/bin/env python3
# Version: 2.7.3 (2025-06-03)
"""
Altman Z-Score Analysis Platform - Main Entry Point

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with
enhanced LLM-powered qualitative insights. This script orchestrates the analysis
pipeline for single or multiple stock tickers.

Version 2.7.3 Features:
- Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- Updated documentation and version numbers for v2.7.3
- No breaking changes; all outputs and APIs remain stable

Data Sources:
- Primary: Yahoo Finance (real-time financials and market data)
- Fallback: SEC EDGAR/XBRL (official regulatory filings)
- Executive Data: Multi-source aggregation for comprehensive profiles

Output Structure:
All outputs are saved to output/<TICKER>/:
- zscore_<TICKER>_zscore_full_report.md (comprehensive analysis with LLM insights)
- zscore_<TICKER>_trend.png (trend visualization chart)
- zscore_<TICKER>.csv and .json (raw analytical data)
- <TICKER>_NOT_AVAILABLE.txt (marker for unavailable tickers)

USAGE:
    python main.py AAPL MSFT TSLA
    python main.py TSLA --start 2023-01-01
    python main.py AAPL MSFT --no-plot

Examples:
    # Single stock analysis
    python main.py AAPL
    
    # Multi-stock portfolio analysis
    python main.py AAPL MSFT GOOGL TSLA
    
    # Custom date range analysis
    python main.py AAPL --start 2022-01-01
    
    # Analysis without chart generation
    python main.py AAPL MSFT --no-plot

Note: This code follows PEP 8 style guidelines and uses 4-space indentation.
"""
__version__ = "2.7.3"

# v2.7.1 release: Enhanced executive/officer information injection into LLM qualitative analysis, 
# improved company profiles with multi-source data integration, fixed missing officer data 
# handling in LLM prompts for more robust analysis

import argparse
import os
import sys
import time

import pandas as pd

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.one_stock_analysis import (  # noqa: E402
    analyze_single_stock_zscore_trend,
    print_header,
    print_info,
    print_success,
    print_warning,
    print_error
)


def parse_args():
    """Parse command line arguments for the Altman Z-Score analysis."""
    parser = argparse.ArgumentParser(
        description="Altman Z-Score Analysis Platform v2.7.1 - Comprehensive financial analysis with LLM insights",
        epilog="Examples:\n"
               "  python main.py AAPL                    # Single stock analysis\n"
               "  python main.py AAPL MSFT GOOGL         # Multi-stock portfolio analysis\n"
               "  python main.py TSLA --start 2023-01-01 # Custom date range\n"
               "  python main.py AAPL --no-plot          # Skip chart generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "tickers",
        type=str,
        nargs='+',
        help="Stock ticker symbol(s) for analysis (e.g., AAPL MSFT TSLA). "
             "Each ticker generates comprehensive reports with Z-Score trends, "
             "LLM qualitative analysis, and executive/officer profiles."
    )
    parser.add_argument(
        "--start",
        type=str,
        default="2024-01-01",
        help="Start date for analysis in YYYY-MM-DD format (default: 2024-01-01). "
             "Analysis will include all available quarterly data from this date forward."
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable trend chart generation (default: False). "
             "When enabled, saves processing time but skips visual trend analysis."
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


def main():
    """
    Main entry point for the Altman Z-Score Analysis Platform.
    
    Orchestrates comprehensive financial analysis including:
    - Multi-source data fetching (Yahoo Finance + SEC EDGAR fallback)
    - Industry-specific Z-Score model selection and calculation
    - Enhanced LLM qualitative analysis with executive/officer profiles
    - Trend visualization and comprehensive report generation
    - Robust error handling with transparent reporting
    
    For each ticker, generates:
    - Full analytical report with LLM insights (.md)
    - Trend visualization chart (.png)
    - Raw data outputs (.csv, .json)
    - Error markers for unavailable tickers
    """
    args = parse_args()
    ticker_list = [t.upper() for t in args.tickers]
    start_date = args.start
    no_plot = args.no_plot
    for ticker in ticker_list:
        try:
            start_time = time.time()
            df = analyze_single_stock_zscore_trend(
                ticker,
                start_date=start_date
            )
            end_time = time.time()
            if df is not None and not df.empty and 'zscore' in df.columns:
                valid_scores = df[df['zscore'].notnull()]
                if not valid_scores.empty:
                    result_df = df[['quarter_end', 'zscore']].copy()
                    result_df.columns = ['Quarter', 'Z-Score']
                    result_df = result_df.sort_values('Quarter', ascending=False)
                    formatted_results = []
                    for _, row in result_df.iterrows():
                        quarter = row['Quarter']
                        z_score = row['Z-Score']
                        if pd.isna(z_score):
                            score_str = "N/A"
                        else:
                            if z_score < 1.8:
                                score_str = f"{z_score:.2f} (Distress)"
                            elif z_score < 3.0:
                                score_str = f"{z_score:.2f} (Grey)"
                            else:
                                score_str = f"{z_score:.2f} (Safe)"
                        formatted_results.append(f"{quarter}: {score_str}")                    
                        for result in formatted_results:
                            print(result)
                    elapsed = end_time - start_time
                    print_success(f"Analysis completed in {elapsed:.2f} seconds")
                    plot_path = f"output/{ticker}/zscore_{ticker}_trend.png"
                    if not no_plot:
                        print_info(f"Z-Score plot saved to {plot_path}")
                    # Note: Plotting is already handled by analyze_single_stock_zscore_trend
                    # The chart uses the correct model selected by the analysis logic
                else:
                    print_warning(f"No valid Z-Scores calculated for {ticker}")
            else:
                print_warning(f"No analysis results available for {ticker}")
        except Exception as e:
            print_error(f"Analysis failed for {ticker}: {e}")
            continue


if __name__ == "__main__":
    main()
