#!/usr/bin/env python3
"""
Altman Z-Score Analysis Pipeline Entry Point (MVP)

This script serves as the main entry point and pipeline coordinator for
single-stock or multi-stock Altman Z-Score trend analysis. It delegates analysis to the
core logic in src/altman_zscore/one_stock_analysis.py.

Note: This code follows PEP 8 style guidelines.

USAGE:
    python main.py AAPL MSFT TSLA
    python main.py TSLA --start 2023-01-01
    python main.py AAPL MSFT --moving-averages --no-plot

All outputs will be saved to output/<TICKER>/
"""
__version__ = "2.5"

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
        description="Single Stock Altman Z-Score Trend Analysis"
    )
    parser.add_argument(
        "tickers",
        type=str,
        nargs='+',
        help="Stock ticker symbol(s), space separated (e.g., AAPL MSFT TSLA)"
    )
    parser.add_argument(
        "--start",        type=str,
        default="2024-01-01",
        help="Start date (YYYY-MM-DD) for analysis (default: 2024-01-01)"
    )
    parser.add_argument(
        "--moving-averages",
        action="store_true",
        help="Show moving averages in Z-Score and price plots (default: False)"
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable plot generation (default: False)"
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


def main():
    """Main entry point for the Altman Z-Score analysis pipeline."""
    args = parse_args()
    ticker_list = [t.upper() for t in args.tickers]
    start_date = args.start
    show_moving_averages = args.moving_averages
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
