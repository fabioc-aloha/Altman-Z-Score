#!/usr/bin/env python3
# Version: 3.0.0 (2025-06-07)
"""
Altman Z-Score Analysis Platform - Main Entry Point

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with
LLM-powered qualitative insights. This script orchestrates the analysis pipeline for single or multiple stock tickers.

Architecture Overview:
    1. Input Layer: Accepts ticker(s) and analysis date; validates input.
    2. Data Fetching Layer: Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance).
    3. Validation Layer: Validates raw data using Pydantic schemas; reports missing/invalid fields.
    4. Computation Layer: Computes Altman Z-Score using validated data; returns result object.
    5. Reporting Layer: Outputs results to CSV, JSON, or stdout; logs all steps and errors.

Key Principles:
    - Modularity: Each phase is implemented as a separate, testable module.
    - Robustness: Strong error handling, logging, and data validation at every step.
    - Extensibility: Easy to add new data sources, models, or output formats.
    - Testability: Each module is independently testable with clear interfaces.

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
    python main.py --test

Examples:
    # Single stock analysis
    python main.py AAPL
    # Multi-stock portfolio analysis
    python main.py AAPL MSFT GOOGL TSLA
    # Custom date range analysis
    python main.py AAPL --start 2022-01-01
    # Analysis without chart generation
    python main.py AAPL MSFT --no-plot
    # Run tests
    python main.py --test
    # Set log level
    python main.py --log-level DEBUG

Note: This code follows PEP 8 style guidelines and uses 4-space indentation.
"""
__version__ = "3.0.0"


import argparse
import os
import sys
import time
import logging
import threading

import pandas as pd

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.core.one_stock_analysis import analyze_single_stock_zscore_trend
from altman_zscore.core.progress_tracking import PIPELINE_STEPS

def parse_args():
    """Parse command line arguments for the Altman Z-Score analysis."""
    parser = argparse.ArgumentParser(
        description="Altman Z-Score Analysis Platform - Comprehensive financial analysis with LLM insights",
        epilog="Examples:\n"
               "  python main.py AAPL                    # Single stock analysis\n"
               "  python main.py AAPL MSFT GOOGL         # Multi-stock portfolio analysis\n"
               "  python main.py TSLA --start 2023-01-01 # Custom date range\n"
               "  python main.py AAPL --no-plot          # Skip chart generation\n"
               "  python main.py --test                  # Run all tests\n"
               "  python main.py --log-level DEBUG       # Set log level",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "tickers",
        type=str,
        nargs='*',
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
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the test suite and exit. Ignores all other arguments."
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOG_LEVEL", "ERROR"),
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: ERROR or $LOG_LEVEL env var."
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


def format_zscore_results(df):
    """Format Z-Score results for reporting."""
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
    return formatted_results


# Import pipeline steps from progress tracking module
from altman_zscore.core.progress_tracking import PIPELINE_STEPS

def show_progress_bar(ticker, step_idx, total_steps):
    bar_length = 30
    progress = (step_idx + 1) / total_steps
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    step_name = PIPELINE_STEPS[step_idx] if step_idx < len(PIPELINE_STEPS) else "Unknown Step"
    print(f"\r[{ticker}] Pipeline Progress: |{bar}| {step_idx + 1}/{total_steps} {step_name}", end='', flush=True)
    if step_idx + 1 == total_steps:
        print()  # Move to new line when complete


def main():
    """
    Main entry point for the Altman Z-Score Analysis Platform.

    Orchestrates a modular, robust pipeline for:
        - Input validation (tickers, dates, CLI args)
        - Data fetching (Yahoo Finance, SEC EDGAR)
        - Data validation (schema checks, missing/invalid field reporting)
        - Computation (Altman Z-Score calculation, model selection)
        - Reporting (CSV, JSON, Markdown, logging)

    Key Features:
        - Strong error handling and logging at every step
        - Extensible: easy to add new models, data sources, or output formats
        - Testable: each module is independently testable
        - CI/CD friendly: returns non-zero exit code on failure, supports --test flag

    Returns:
        None. Exits with code 0 on success, 1 on any ticker failure, 2 on CLI/input error.
    """
    args = parse_args()
    # If no arguments (other than script name), show help and exit
    if len(sys.argv) == 1:
        parser = argparse.ArgumentParser(
            description="Altman Z-Score Analysis Platform - Comprehensive financial analysis with LLM insights",
            epilog="Examples:\n"
                   "  python main.py AAPL                    # Single stock analysis\n"
                   "  python main.py AAPL MSFT GOOGL         # Multi-stock portfolio analysis\n"
                   "  python main.py TSLA --start 2023-01-01 # Custom date range\n"
                   "  python main.py AAPL --no-plot          # Skip chart generation\n"
                   "  python main.py --test                  # Run all tests\n"
                   "  python main.py --log-level DEBUG       # Set log level",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.print_help()
        sys.exit(0)
    # Validate log level
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    log_level = args.log_level.upper()
    if log_level not in valid_log_levels:
        print(f"[ERROR] Invalid log level: {args.log_level}. Must be one of: {', '.join(valid_log_levels)}.", file=sys.stderr)
        sys.exit(2)
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),  # Default to WARNING if not specified
        format='[%(levelname)s] %(message)s'
    )
    # Validate start date format
    import re
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, args.start):
        logging.error(f"Invalid --start date: {args.start}. Must be in YYYY-MM-DD format.")
        sys.exit(2)
    if getattr(args, "test", False):
        import subprocess
        logging.info("Running test suite with pytest...")
        result = subprocess.run([sys.executable, "-m", "pytest"], check=False)
        sys.exit(result.returncode)
    
    ticker_list = [t.upper() for t in args.tickers]
    start_date = args.start
    no_plot = args.no_plot
    any_failed = False

    for ticker in ticker_list:
        try:
            start_time = time.time()
            print(f"\n=== Starting analysis for {ticker} ===")

            def progress_callback(step_name, step_idx, total_steps):
                show_progress_bar(ticker, step_idx, total_steps)
                # Add small delay to make progress visible
                time.sleep(0.1)

            # --- ACTUAL WORKFLOW WITH REAL-TIME PROGRESS ---
            df = analyze_single_stock_zscore_trend(
                ticker,
                start_date=start_date,
                progress_callback=progress_callback
            )

            end_time = time.time()
            print(f"=== Completed analysis for {ticker} ===\n")

            if df is not None and not df.empty and 'zscore' in df.columns:
                valid_scores = df[df['zscore'].notnull()]
                if not valid_scores.empty:
                    formatted_results = format_zscore_results(df)
                    for result in formatted_results:
                        logging.info(result)
                    elapsed = end_time - start_time
                    logging.info(f"Analysis completed in {elapsed:.2f} seconds")
                    plot_path = os.path.join("output", ticker, f"zscore_{ticker}_trend.png")
                    if not no_plot:
                        logging.info(f"Z-Score plot saved to {plot_path}")
                else:
                    logging.warning(f"No valid Z-Scores calculated for {ticker}")
                    any_failed = True
            else:
                logging.warning(f"No analysis results available for {ticker}")
                any_failed = True
        except Exception as e:
            logging.error(f"Analysis failed for {ticker}: {e}")
            any_failed = True
            continue
    if any_failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
