#!/usr/bin/env python3
# Version: 3.5.2 (2025-06-18)
"""
Altman Z-Score Analysis Platform - Main Entry Point

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with
LLM-powered qualitative insights. This script orchestrates the analysis pipeline for
single or multiple stock tickers.

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
    - Primary: SEC EDGAR/XBRL (official regulatory filings for financial data)
    - Fallback: Yahoo Finance (when SEC data unavailable, plus market data)
    - Executive Data: Multi-source aggregation for comprehensive profiles

Output Structure:
    All outputs are saved to output/<TICKER>/:
        - zscore_<TICKER>_zscore_full_report.md (comprehensive analysis with LLM insights)
        - zscore_<TICKER>_trend.png (trend visualization chart)
        - zscore_<TICKER>.csv and .json (raw analytical data)
        - <TICKER>_NOT_AVAILABLE.txt (marker for unavailable tickers)

USAGE:
    python main.py AAPL MSFT TSLA
    python main.py TSLA --date 2023-01-01
    python main.py AAPL MSFT --no-plot
    python main.py --test

Examples:
    # Single stock analysis
    python main.py AAPL
    # Multi-stock portfolio analysis
    python main.py AAPL MSFT GOOGL TSLA
    # Custom date range analysis
    python main.py AAPL --date 2022-01-01
    # Analysis without chart generation
    python main.py AAPL MSFT --no-plot
    # Run tests
    python main.py --test
    # Set log level
    python main.py --log-level DEBUG

Note: This code follows PEP 8 style guidelines and uses 4-space indentation.
"""
__version__ = "3.5.1"


import os
# Load .env variables before any other imports that may use them
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import argparse
import sys
import time
import logging
import threading
import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging with more verbosity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from altman_zscore.core.one_stock_analysis import analyze_single_stock_zscore_trend
from altman_zscore.core.progress_tracking import PIPELINE_STEPS

def parse_args():
    """
    Parse command line arguments for the Altman Z-Score analysis CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments including tickers, model, date range, and options.
    """
    parser = argparse.ArgumentParser(
        description="Altman Z-Score Analysis Platform - Comprehensive financial analysis with LLM insights",
        epilog="Examples:\n"
               "  python main.py AAPL                    # Single stock analysis\n"
               "  python main.py AAPL MSFT GOOGL         # Multi-stock portfolio analysis\n"
               "  python main.py TSLA --date 2023-01-01  # Custom date range\n"
               "  python main.py AAPL --model financial  # Force financial institution model\n"
               "  python main.py --test                  # Run all tests\n"
               "  python main.py --update-cache          # Update SEC company database\n"
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
        "--model",
        type=str,
        choices=['original', 'private', 'financial', 'zeta', 'retail'],        
        help="Force a specific Z-Score model instead of using automatic selection. "
             "Options: original (manufacturing), private (private companies), "
             "financial (banks), zeta (mature), retail (retail sector)"
    )
    
    def default_start_date():
        """Calculate default analysis date.
        Default to 3 years of data, but users can request more historical data if available.
        """
        today = datetime.date.today()
        dt = today.replace(day=1) - relativedelta(months=36)  # Default to 3 years
        return dt.strftime("%Y-%m-%d")
    
    parser.add_argument(
        "--date",
        type=str,
        default=default_start_date(),
        help="Analysis date for historical data in YYYY-MM-DD format (default: 1st of the month 36 months before today). "
             "Historical data availability varies by company, with many U.S. companies having 15+ years of data available."
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
    parser.add_argument(
        "--update-cache",
        action="store_true",
        help="Download and update the SEC company tickers cache, then exit. "
             "This improves CIK lookup performance and reliability."
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


def format_zscore_results(df):
    """
    Format Z-Score results DataFrame for human-readable reporting.

    Args:
        df (pandas.DataFrame): DataFrame with 'quarter_end' and 'zscore' columns.

    Returns:
        list[str]: List of formatted strings summarizing Z-Score and risk zone by quarter.
    """
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

def show_progress_bar(ticker, step_idx, total_steps, model_name=None):
    """
    Display a progress bar for the analysis pipeline in the terminal.

    Args:
        ticker (str): Stock ticker symbol being analyzed.
        step_idx (int): Current pipeline step index (1-based).
        total_steps (int): Total number of steps in the pipeline.
        model_name (str, optional): Name of the Z-Score model in use.
    """
    try:
        # Validate total_steps
        if not isinstance(total_steps, int) or total_steps <= 0:
            total_steps = len(PIPELINE_STEPS)
        bar_length = 30
        # Safely compute filled length
        progress = (step_idx + 1) / total_steps if total_steps > 0 else 0
        filled_length = int(bar_length * progress)
        bar = '■' * filled_length + '□' * (bar_length - filled_length)
        step_name = PIPELINE_STEPS[step_idx] if step_idx < len(PIPELINE_STEPS) else "Unknown Step"
        # Header message
        if step_name == "Z-Score Computation" and model_name:
            header = f"[{ticker}] Applying {model_name} Model"
        else:
            header = f"[{ticker}] Analysis Pipeline"
        # Compose and print
        current_msg = f"{header}: |{bar}| {step_idx + 1}/{total_steps} {step_name}"
        max_length = max(
            len(f"[{ticker}] Analysis Pipeline: |{'■' * bar_length}| {i+1}/{total_steps} {step}")
            for i, step in enumerate(PIPELINE_STEPS)
        ) + 1
        print(f"\r{' ' * max_length}\r", end='', flush=True)
        print(f"{current_msg}", end='', flush=True)
        if step_idx + 1 == total_steps:
            print()  # New line at completion
    except Exception:
        # Safely ignore any progress display errors
        pass

def analyze_tickers(tickers: list, model: str = None, **kwargs) -> dict:
    """
    Analyze multiple stock tickers in sequence, with progress tracking and error handling.

    Args:
        tickers (list[str]): List of stock ticker symbols to analyze.
        model (str, optional): Model type to force for all analyses (overrides auto-selection).
        **kwargs: Additional keyword arguments passed to analyze_ticker.

    Returns:
        dict: Dictionary mapping each ticker to its analysis results or error info.
    """
    results = {}
    for ticker in tickers:
        try:
            # Create progress callback for this ticker
            def progress_callback(step_idx, total_steps, model_name):
                show_progress_bar(ticker, step_idx, total_steps, model_name)
            # Initialize analysis with progress tracking
            from altman_zscore.core.progress_tracking import create_progress_tracker
            progress_tracker = create_progress_tracker(progress_callback)
            # Run analysis with correct parameter names
            from altman_zscore.core.one_stock_analysis import analyze_ticker
            results[ticker] = analyze_ticker(
                ticker=ticker,
                force_model=model,
                progress_tracker=progress_tracker,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            if logger.level <= logging.DEBUG:
                logger.exception(e)
            results[ticker] = {"error": str(e)}
            continue
    return results


def main():
    """
    Main entry point for the Altman Z-Score Analysis Platform CLI.

    Handles argument parsing, logging setup, input validation, and orchestrates the
    analysis pipeline for one or more tickers. Outputs results to disk and/or stdout.
    """
    try:
        args = parse_args()
        logger.info("Starting Altman Z-Score Analysis")        # If no arguments except possibly --update-cache, show help and exit
        if len(sys.argv) == 1 or (not args.tickers and not getattr(args, "update_cache", False) and not getattr(args, "test", False)):
            parser = argparse.ArgumentParser(
                description="Altman Z-Score Analysis Platform - Comprehensive financial analysis with LLM insights",                
                epilog="Examples:\n"
                       "  python main.py AAPL                    # Single stock analysis\n"                       
                       "  python main.py AAPL MSFT GOOGL         # Multi-stock portfolio analysis\n"
                       "  python main.py TSLA --date 2023-01-01  # Custom date range\n"
                       "  python main.py AAPL --no-plot          # Skip chart generation\n"
                       "  python main.py --test                  # Run all tests\n"
                       "  python main.py --update-cache          # Update SEC company database\n"
                       "  python main.py --log-level DEBUG       # Set log level",
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            parser.print_help()
            sys.exit(0)

        logger.info(f"Processing tickers: {', '.join(args.tickers)}")
    
        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        log_level = args.log_level.upper()
        if log_level not in valid_log_levels:
            logger.error(f"Invalid log level: {args.log_level}. Must be one of: {', '.join(valid_log_levels)}.")
            sys.exit(2)        # Set logging level
        logging.getLogger().setLevel(getattr(logging, log_level, logging.WARNING))
        logger.info(f"Log level set to {log_level}")        # Handle cache update command
        if getattr(args, "update_cache", False):
            logger.info("Updating SEC company tickers cache...")
            from altman_zscore.company.cik_cache import get_cache, refresh_cache, get_cache_stats
            
            # Check existing cache first
            cache_info = get_cache_stats()
            if cache_info.get('cache_exists', False):
                logger.info(f"Existing cache found with {cache_info.get('entry_count', 'unknown')} entries")
            
            success = refresh_cache()
            if success:
                updated_info = get_cache_stats()
                logger.info(f"✅ Cache updated successfully! Downloaded {updated_info.get('entry_count', 'unknown')} company entries.")
                logger.info(f"Cache location: {updated_info.get('cache_path', 'unknown')}")
                logger.info(f"Cache last updated: {updated_info.get('last_updated', 'unknown')}")
            else:
                if cache_info.get('cache_exists', False):
                    logger.warning("⚠️  Failed to download fresh data due to SEC API rate limiting, but existing cache is available.")
                    logger.info(f"Existing cache has {cache_info.get('entry_count', 'unknown')} entries from {cache_info.get('last_updated', 'unknown')}")
                    logger.info("The system will use the existing cache for CIK lookups.")
                else:
                    logger.error("❌ Failed to update cache and no existing cache found. Check network connection and try again later.")
                    sys.exit(1)
            sys.exit(0)
          # Validate date format
        import re
        from datetime import datetime
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, args.date):
            logger.error(f"Invalid --date: {args.date}. Must be in YYYY-MM-DD format.")
            sys.exit(2)

        # Validate date is not in the future
        start_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        if start_date > datetime.now().date():
            logger.error(f"Analysis date ({args.date}) cannot be in the future.")
            sys.exit(2)

        logger.info(f"Analysis date: {args.date}")

        if getattr(args, "test", False):
            import subprocess
            logger.info("Running test suite with pytest...")
            result = subprocess.run([sys.executable, "-m", "pytest"], check=False)
            sys.exit(result.returncode)
        
        ticker_list = [t.upper() for t in args.tickers]
        start_date = args.date
        no_plot = args.no_plot
        failed_tickers = []
        successful_tickers = []

        for ticker in ticker_list:
            try:
                logger.info(f"\nProcessing {ticker}...")
                start_time = time.time()

                def progress_callback(step_idx, total_steps, model_name=None):
                    show_progress_bar(ticker, step_idx, total_steps, model_name)
                    time.sleep(0.1)

                # Run analysis
                df = analyze_single_stock_zscore_trend(
                    ticker,
                    start_date=start_date,
                    progress_callback=progress_callback,
                    force_model=args.model
                )

                end_time = time.time()
                elapsed = end_time - start_time

                if df is not None and not df.empty and 'zscore' in df.columns:
                    valid_scores = df[df['zscore'].notnull()]
                    if not valid_scores.empty:
                        formatted_results = format_zscore_results(df)
                        for result in formatted_results:
                            logger.info(result)
                        logger.info(f"Analysis completed in {elapsed:.2f} seconds")
                        plot_path = os.path.join("output", ticker, f"zscore_{ticker}_trend.png")
                        if not no_plot:
                            logger.info(f"Z-Score plot saved to {plot_path}")
                        successful_tickers.append(ticker)
                    else:
                        logger.warning(f"No valid Z-Scores calculated for {ticker}")
                        failed_tickers.append((ticker, "No valid Z-Scores calculated"))
                else:
                    logger.warning(f"No analysis results available for {ticker}")
                    failed_tickers.append((ticker, "No analysis results available"))
            except ValueError as ve:
                logger.error(f"❌ {ticker}: {str(ve)}")
                failed_tickers.append((ticker, str(ve)))
            except Exception as e:
                logger.exception(f"❌ {ticker}: Unexpected error - {str(e)}")
                failed_tickers.append((ticker, f"Unexpected error: {str(e)}"))

        # Provide comprehensive summary
        logger.info(f"\n{'='*60}")
        logger.info("ANALYSIS SUMMARY")
        logger.info(f"{'='*60}")
        
        if successful_tickers:
            logger.info(f"✅ Successfully analyzed: {', '.join(successful_tickers)}")
        
        if failed_tickers:
            logger.warning(f"❌ Failed to analyze {len(failed_tickers)} ticker(s):")
            for ticker, reason in failed_tickers:
                logger.warning(f"   {ticker}: {reason}")
        
        if failed_tickers and not successful_tickers:
            logger.error("All tickers failed analysis")
            sys.exit(1)
        elif failed_tickers:
            logger.warning("Some tickers failed analysis")
            sys.exit(1)
        else:
            logger.info("All analyses completed successfully")
            sys.exit(0)

    except Exception as e:
        logger.exception(f"Critical error in main: {str(e)}")
        sys.exit(2)

if __name__ == '__main__':
    main()
