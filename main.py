#!/usr/bin/env python3
# Version: 3.6.0-dev (2025-06-22) - FMP-First API Strategy
"""
AI-Powered Altman Z-Score Analysis - Main Entry Point

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with
FMP pre-calculated ratios and LLM-powered qualitative insights. This script orchestrates 
the analysis pipeline for single or multiple stock tickers.

🎯 **Strategic Architecture: FMP-First Data Pipeline**
Financial Modeling Prep (FMP) provides **all Z-Score financial ratios pre-calculated**,
eliminating the need for complex SEC EDGAR field mapping and XBRL parsing.

Architecture Overview:
    1. Input Layer: Accepts ticker(s) and analysis parameters; validates input.
    2. FMP Data Fetching: Fetches pre-calculated financial ratios with 48-hour caching.
    3. Yahoo Market Data: Fetches market data (prices, market cap) with 48-hour caching.
    4. Data Integration: Merges FMP ratios with Yahoo market data through quality gates.
    5. Z-Score Calculation: Direct calculation using FMP pre-calculated ratios.
    6. AI Analysis: Azure OpenAI generates intelligent insights and commentary.
    7. Reporting Layer: Outputs results to CSV, JSON, charts, and comprehensive reports.

Key Principles:
    - **API-First**: FMP provides calculation-ready ratios, Yahoo provides market data
    - **Intelligent Caching**: 48-hour TTL for all API calls, ~95% performance improvement
    - **Deterministic Pipeline**: Focus on integration and quality rather than transformation
    - **AI Enhancement**: LLM for insights and commentary, not core data processing
    - **Production Ready**: Thread-safe operations with comprehensive error handling

Data Sources:
    - **Primary Financial**: FMP API with pre-calculated Z-Score ratios (eliminates field mapping)
    - **Market Data**: Yahoo Finance for real-time pricing and market capitalization
    - **AI Analysis**: Azure OpenAI for intelligent insights and commentary generation
    - **Optional Backup**: SEC EDGAR for validation (not required for calculations)

Strategic Advantages:
    - **Pre-calculated Ratios**: Working Capital/Total Assets, EBIT/Total Assets, etc. ready for use
    - **No Field Mapping**: Eliminates SEC XBRL parsing complexity
    - **Lightning Fast**: 48-hour caching + pre-calculated ratios = optimal performance
    - **Reliable**: Deterministic data pipeline with intelligent AI enhancement

Output Structure:
    All outputs are saved to output/<TICKER>/:
        - zscore_<TICKER>_zscore_full_report.md (comprehensive analysis with LLM insights)
        - zscore_<TICKER>_trend.png (trend visualization chart)
        - zscore_<TICKER>.csv and .json (raw analytical data)
        - llm_interactions/ (AI prompts/responses for debugging)
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
__version__ = "3.5.5"


import os
# Determine data period and CSV header field
DATA_PERIOD = os.getenv("FMP_DATA_PERIOD", "annual")  # 'annual' for free tier, 'quarter' for paid
END_FIELD = 'quarter_end' if DATA_PERIOD == 'quarter' else 'year_end'

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

# Add src directory to path for legacy imports (removed in future versions)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging with more verbosity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import new refactored pipeline
from altman_zscore.main_pipeline import AltmanZScorePipeline
import asyncio

# Legacy progress tracking for compatibility
PIPELINE_STEPS = [
    "Data Fetching",
    "Data Integration", 
    "Z-Score Calculation",
    "Market Analysis",
    "Report Generation"
]

def parse_args():
    """
    Parse command line arguments for the Altman Z-Score analysis CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments including tickers, model, date range, and options.    """
    parser = argparse.ArgumentParser(
        description="AI-Powered Altman Z-Score Analysis - Comprehensive financial analysis with LLM insights",        
        epilog="Examples:\n"
               "  python main.py AAPL                          # Single stock analysis\n"
               "  python main.py AAPL MSFT GOOGL               # Multi-stock portfolio analysis\n"
               "  python main.py TSLA --date 2023-01-01        # Custom date range\n"
               "  python main.py AAPL --model financial        # Force financial institution model\n"
               "  python main.py --test                        # Run all tests\n"
               "  python main.py --update-cache                # Update SEC company database\n"
               "  python main.py --log-level DEBUG             # Set log level",
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
        choices=['original', 'private', 'financial', 'retail', 'service', 'emerging'],        
        help="Optional: Force specific model type. Choices: original (manufacturing), private (non-manufacturing), "
             "financial (banks), retail (retail sector), service (service sector), emerging (emerging markets)"
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
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: ERROR or $LOG_LEVEL env var."    )
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
        df (pandas.DataFrame): DataFrame with 'period_end' and 'zscore' columns.

    Returns:
        list[str]: List of formatted strings summarizing Z-Score and risk zone by period.
    """
    result_df = df[['period_end', 'zscore']].copy()
    result_df.columns = ['Period', 'Z-Score']
    result_df = result_df.sort_values('Period', ascending=False)
    formatted_results = []
    for _, row in result_df.iterrows():
        period = row['Period']
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
        formatted_results.append(f"{period}: {score_str}")
    return formatted_results


# Pipeline steps are now defined above in the module

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

def main():
    """
    Main entry point for the AI-Powered Altman Z-Score Analysis CLI.

    Handles argument parsing, logging setup, input validation, and orchestrates the
    analysis pipeline for one or more tickers. Outputs results to disk and/or stdout.
    """
    try:
        args = parse_args()
        
        # Handle cache update command (disabled - cache functionality moved to new architecture)
        if getattr(args, "update_cache", False):
            print("Cache update functionality temporarily disabled during refactoring.")
            print("The new FMP-based architecture uses 48-hour API caching automatically.")
            sys.exit(0)

        # If no arguments except possibly --update-cache, show help and exit
        if len(sys.argv) == 1 or (not args.tickers and not getattr(args, "update_cache", False) and not getattr(args, "test", False)):
            parser = argparse.ArgumentParser(
                description="AI-Powered Altman Z-Score Analysis - Comprehensive financial analysis with LLM insights",                
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

        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        log_level = args.log_level.upper()
        if log_level not in valid_log_levels:
            logger.error(f"Invalid log level: {args.log_level}. Must be one of: {', '.join(valid_log_levels)}.")
            sys.exit(2)
        
        # Set logging level
        logging.getLogger().setLevel(getattr(logging, log_level, logging.WARNING))
        logger.info(f"Log level set to {log_level}")

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
                
                # Use the new pipeline to generate CSV, JSON, chart, and reports
                from altman_zscore.main_pipeline import AltmanZScorePipeline
                pipeline = AltmanZScorePipeline()
                output_files = asyncio.run(
                    pipeline.analyze_ticker(
                        ticker,
                        generate_charts=not no_plot,
                        generate_reports=True,
                        include_ai_insights=False,
                        start_date=args.date
                    )
                )
                # Log generated files
                logger.info(f"Generated CSV: {output_files.get('csv')}")
                logger.info(f"Generated JSON: {output_files.get('json')}")
                if output_files.get('chart'):
                    logger.info(f"Generated Chart: {output_files.get('chart')}")
                if output_files.get('report'):
                    logger.info(f"Generated Report: {output_files.get('report')}")
                if output_files.get('summary'):
                    logger.info(f"Generated Summary: {output_files.get('summary')}")

                end_time = time.time()
                elapsed = end_time - start_time

                # Mark ticker as successfully analyzed after pipeline run
                logger.info(f"Analysis completed in {elapsed:.2f} seconds for {ticker}")
                successful_tickers.append(ticker)
            except ValueError as ve:
                logger.error(f"ERROR {ticker}: {str(ve)}")
                failed_tickers.append((ticker, str(ve)))
            except Exception as e:
                logger.exception(f"ERROR {ticker}: Unexpected error - {str(e)}")
                failed_tickers.append((ticker, f"Unexpected error: {str(e)}"))

        # Provide comprehensive summary        
        logger.info("ANALYSIS SUMMARY")
        logger.info(f"{'='*60}")
        if successful_tickers:
            logger.info(f"✅ Successfully analyzed: {', '.join(successful_tickers)}")
            sys.exit(0)
        else:
            logger.error(f"❌ Failed to analyze any tickers: {len(failed_tickers)} failure(s)")
            sys.exit(1)

    except Exception as e:
        logger.exception(f"Critical error in main: {str(e)}")
        sys.exit(2)

if __name__ == '__main__':
    main()
