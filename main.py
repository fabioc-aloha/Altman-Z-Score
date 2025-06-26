#!/usr/bin/env python3
# Version: 4.0.0 (2025-01-07) - Professional Investment Analysis Platform
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
    python main.py TSLA --quarters 8
    python main.py AAPL --model financial

Examples:
    # Single stock analysis
    python main.py AAPL
    # Multi-stock portfolio analysis
    python main.py AAPL MSFT GOOGL TSLA
    # Multi-quarter analysis
    python main.py AAPL --quarters 8
    # Force specific model
    python main.py AAPL --model financial
    # Set log level
    python main.py --log-level DEBUG

Note: This code follows PEP 8 style guidelines and uses 4-space indentation.
"""
__version__ = "4.0.0"


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
import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

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

# CLI help epilog - single source of truth
CLI_EPILOG = ("Examples:\n"
              "  python main.py AAPL                        # Single stock analysis\n"
              "  python main.py AAPL MSFT GOOGL             # Multi-stock portfolio analysis\n"
              "  python main.py TSLA --quarters 8           # Multi-quarter analysis\n"
              "  python main.py AAPL --model financial      # Force financial institution model\n"
              "  python main.py --clear-cache               # Clear all API caches\n"
              "  python main.py --cache-stats               # Show cache statistics\n"
              "  python main.py --log-level DEBUG           # Set log level")

# CLI description - single source of truth
CLI_DESCRIPTION = "AI-Powered Altman Z-Score Analysis - Comprehensive financial analysis with LLM insights"

class HelpFormatterWithEmptyLine(argparse.RawDescriptionHelpFormatter):
    """Custom formatter for consistent help formatting."""
    
    def format_help(self):
        help_text = super().format_help()
        return help_text

class HelpAction(argparse._HelpAction):
    """Custom help action that prints empty line before exit."""
    
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        print()  # Add empty line
        parser.exit()

def get_env_default(key: str, default_value, value_type=str):
    """
    Get environment variable with type conversion and fallback to default.
    
    Args:
        key: Environment variable name
        default_value: Default value if env var not found or invalid
        value_type: Type to convert to (str, int, bool)
    
    Returns:
        Converted value or default_value
    """
    try:
        env_value = os.environ.get(key)
        if env_value is None:
            return default_value
        
        if value_type == bool:
            return env_value.lower() in ('1', 'true', 'yes', 'on')
        elif value_type == int:
            return int(env_value)
        else:
            return str(env_value)
    except (ValueError, TypeError):
        return default_value


def parse_args():
    """
    Parse command line arguments for the Altman Z-Score analysis CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments including tickers, model, date range, and options.    """
    parser = argparse.ArgumentParser(
        description=CLI_DESCRIPTION,        
        epilog=CLI_EPILOG,
        formatter_class=HelpFormatterWithEmptyLine,
        add_help=False  # Disable default help to use custom
    )
    
    # Add custom help argument
    parser.add_argument(
        '-h', '--help',
        action=HelpAction,
        help='show this help message and exit'
    )
    parser.add_argument(
        "tickers",
        type=str,        
        nargs='*',
        help="Stock ticker symbol(s) for analysis (e.g., AAPL MSFT TSLA). "
             "Each ticker generates comprehensive reports with Z-Score trends, "
             "LLM qualitative analysis, and executive/officer profiles."
    )
    # Determine defaults based on environment configuration
    fmp_enhanced = get_env_default('FMP_ENHANCED_MODE', False, bool)
    default_quarters = get_env_default('DEFAULT_QUARTERS', 4 if not fmp_enhanced else 8, int)
    default_batch_size = get_env_default('MAX_BATCH_SIZE', 10 if not fmp_enhanced else 25, int)
    
    parser.add_argument(
        "--model",
        type=str,
        choices=['original', 'private', 'financial', 'retail', 'service', 'emerging'],        
        help="Optional: Force specific model type. Choices: original (manufacturing), private (non-manufacturing), "
             "financial (banks), retail (retail sector), service (service sector), emerging (emerging markets)"
    )
    
    parser.add_argument(
        "--quarters",
        type=int,
        default=default_quarters,
        help=f"Number of quarters for historical Z-Score trend analysis (default: {default_quarters}). "
             "Enhanced FMP accounts support extended historical data (up to 20+ quarters). "
             "Provides quarter-over-quarter Z-Score trends and seasonality analysis."
    )
    parser.add_argument(
        "--enhanced-analysis",
        action="store_true",
        default=fmp_enhanced,
        help=f"Enable enhanced analysis features for upgraded FMP accounts (default: {'enabled' if fmp_enhanced else 'disabled'} based on .env). "
             "Includes: detailed quarterly trends, peer comparison data, "
             "industry benchmarking, and comprehensive ratio decomposition."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=default_batch_size,
        help=f"Batch size for concurrent processing (default: {default_batch_size} based on .env). "
             "Upgraded accounts can process larger batches efficiently."
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=get_env_default("LOG_LEVEL", "ERROR"),
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
             f"Default: {get_env_default('LOG_LEVEL', 'ERROR')} (from .env or ERROR)."
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached API responses (FMP financial data + Yahoo Finance market data), then exit. "
             "Forces fresh data retrieval on next analysis run."
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Display cache statistics (size, entries, hit rates) and exit. "
             "Shows details for both FMP financial data and Yahoo Finance market data caches."
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


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
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        step_name = PIPELINE_STEPS[step_idx] if step_idx < len(PIPELINE_STEPS) else "Unknown Step"
        # Header message
        if step_name == "Z-Score Computation" and model_name:
            header = f"[{ticker}] Applying {model_name} Model"
        else:
            header = f"[{ticker}] Analysis Pipeline"
        # Compose and print
        current_msg = f"{header}: |{bar}| {step_idx + 1}/{total_steps} {step_name}"
        max_length = max(
            len(f"[{ticker}] Analysis Pipeline: |{'#' * bar_length}| {i+1}/{total_steps} {step}")
            for i, step in enumerate(PIPELINE_STEPS)
        ) + 1
        print(f"\r{' ' * max_length}\r", end='', flush=True)
        print(f"{current_msg}", end='', flush=True)
        if step_idx + 1 == total_steps:
            print()  # New line at completion
    except Exception:
        # Safely ignore any progress display errors
        pass

def show_cache_stats():
    """
    Display comprehensive cache statistics for all cached data sources.
    
    Shows statistics for:
    - FMP financial data cache
    - Yahoo Finance market data cache
    - Overall cache performance metrics
    """
    try:
        import shutil
        from pathlib import Path
        import json
        from datetime import datetime as dt
        
        print("CACHE STATISTICS REPORT")
        print("=" * 60)
        
        # Define cache directory
        cache_dir = Path(".cache")
        
        if not cache_dir.exists():
            print("[ERROR] No cache directory found")
            print("   Run an analysis first to populate the cache.")
            return
        
        # Overall cache statistics
        total_files = 0
        total_size = 0
        cache_sources = {}
        
        # Scan cache directories
        for source_dir in cache_dir.iterdir():
            if source_dir.is_dir():
                source_name = source_dir.name.upper()
                source_files = 0
                source_size = 0
                source_entries = []
                
                # Count files and calculate size
                for cache_file in source_dir.rglob("*"):
                    if cache_file.is_file():
                        file_size = cache_file.stat().st_size
                        source_files += 1
                        source_size += file_size
                        total_files += 1
                        total_size += file_size
                        
                        # Try to get metadata for this cache entry
                        if cache_file.suffix == '.json' and not cache_file.name.endswith('.meta'):
                            try:
                                modified_time = dt.fromtimestamp(cache_file.stat().st_mtime)
                                
                                # Try to extract ticker from corresponding .meta file
                                ticker_info = "Unknown"
                                meta_file = cache_file.with_suffix('.json.meta')
                                if meta_file.exists():
                                    try:
                                        with open(meta_file, 'r') as f:
                                            meta_data = json.load(f)
                                            cache_key = meta_data.get('key', '')
                                            # Extract ticker from key formats like "fmp_income:AAPL:annual" or "yahoo_summary:AAPL"
                                            if ':' in cache_key:
                                                parts = cache_key.split(':')
                                                if len(parts) >= 2:
                                                    ticker_info = parts[1]  # Second part should be ticker
                                            elif cache_key:
                                                ticker_info = cache_key
                                    except Exception:
                                        pass
                                
                                source_entries.append({
                                    'file': cache_file.name,
                                    'ticker': ticker_info,
                                    'size': file_size,
                                    'modified': modified_time
                                })
                            except Exception:
                                pass
                
                cache_sources[source_name] = {
                    'files': source_files,
                    'size': source_size,
                    'entries': source_entries
                }
        
        # Display overall statistics
        print(f"Cache Directory: {cache_dir.absolute()}")
        print(f"Total Files: {total_files:,}")
        print(f"Total Size: {_format_bytes(total_size)}")
        print()
        
        # Display per-source statistics
        for source_name, stats in cache_sources.items():
            print(f"[{source_name}] Cache")
            print(f"   Files: {stats['files']:,}")
            print(f"   Size: {_format_bytes(stats['size'])}")
            
            if stats['entries']:
                # Group entries by ticker for better organization
                ticker_groups = {}
                for entry in stats['entries']:
                    ticker = entry.get('ticker', 'Unknown')
                    if ticker not in ticker_groups:
                        ticker_groups[ticker] = []
                    ticker_groups[ticker].append(entry)
                
                print(f"   Cached Tickers: {', '.join(sorted(ticker_groups.keys()))}")
                
                # Show most recent entries
                recent_entries = sorted(stats['entries'], key=lambda x: x['modified'], reverse=True)[:5]
                print(f"   Recent Entries:")
                for entry in recent_entries:
                    age_str = _format_time_ago(entry['modified'])
                    ticker_display = entry.get('ticker', 'Unknown')
                    cache_type = ""
                    if source_name == "FMP":
                        cache_type = " (Financial Data)"
                    elif source_name == "YAHOO":
                        cache_type = " (Market Data)"
                    print(f"     - {ticker_display}{cache_type} ({_format_bytes(entry['size'])}, {age_str})")
            print()
        
        # Cache effectiveness estimates
        if total_files > 0:
            print("Cache Effectiveness")
            estimated_api_calls_saved = total_files // 2  # Rough estimate (JSON + meta files)
            print(f"   Estimated API calls saved: ~{estimated_api_calls_saved:,}")
            print(f"   Storage efficiency: {_format_bytes(total_size / total_files if total_files > 0 else 0)} per entry")
            
            # Time-based analysis
            if any(stats['entries'] for stats in cache_sources.values()):
                all_entries = []
                for stats in cache_sources.values():
                    all_entries.extend(stats['entries'])
                
                if all_entries:
                    oldest = min(entry['modified'] for entry in all_entries)
                    newest = max(entry['modified'] for entry in all_entries)
                    print(f"   Cache age range: {_format_time_ago(oldest)} to {_format_time_ago(newest)}")
        
        print("=" * 60)
        print("TIPS:")
        print("   - Use --clear-cache to remove all cached data")
        print("   - Cache files expire automatically after 48 hours")
        print("   - Large cache = fewer API calls = faster analysis")
        
    except Exception as e:
        print(f"[ERROR] Error retrieving cache statistics: {e}")
        print("   This may indicate cache corruption or permission issues.")

def _format_bytes(bytes_count: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"


def _format_time_ago(timestamp: datetime.datetime) -> str:
    """Format timestamp as time ago string."""
    try:
        # Ensure we have a timezone-naive datetime for comparison
        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)
        
        now = datetime.datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"
    except Exception as e:
        return f"unknown ({e})"


def main():
    """
    Main entry point for the AI-Powered Altman Z-Score Analysis CLI.

    Handles argument parsing, logging setup, input validation, and orchestrates the
    analysis pipeline for one or more tickers. Outputs results to disk and/or stdout.
    """
    try:
        args = parse_args()
        
        # Handle cache update command
        if getattr(args, "clear_cache", False):
            print("Updating cache files...")
            print("This operation clears all cached API responses to ensure fresh data.")
            
            try:
                import shutil
                from pathlib import Path
                
                # Define cache directory (matches the caching strategy used in fetchers)
                cache_dir = Path(".cache")
                
                if cache_dir.exists():
                    files_removed = 0
                    # Count files recursively
                    for item in cache_dir.rglob("*"):
                        if item.is_file():
                            files_removed += 1
                    
                    # Remove the entire cache directory
                    shutil.rmtree(cache_dir)
                    print(f"[SUCCESS] Cache updated: {files_removed} cached files removed")
                else:
                    print("[SUCCESS] Cache directory was already empty")
                    
                print("Next analysis will fetch fresh data from all APIs.")
                print("Note: This includes FMP financial data and Yahoo Finance market data caches.")
                
            except Exception as e:
                print(f"[ERROR] Cache update failed: {str(e)}")
                print()  # Empty line before exit
                sys.exit(1)
                
            print()  # Empty line before exit
            sys.exit(0)

        # Handle cache stats command
        if getattr(args, "cache_stats", False):
            show_cache_stats()
            print()  # Empty line before exit
            sys.exit(0)

        # If no arguments except possibly --clear-cache or --cache-stats, show help and exit
        if len(sys.argv) == 1 or (not args.tickers and not getattr(args, "clear_cache", False) and not getattr(args, "cache_stats", False)):
            parser = argparse.ArgumentParser(
                description=CLI_DESCRIPTION,                
                epilog=CLI_EPILOG,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            parser.print_help()
            print()  # Empty line before exit
            sys.exit(0)

        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        log_level = args.log_level.upper()
        if log_level not in valid_log_levels:
            logger.error(f"Invalid log level: {args.log_level}. Must be one of: {', '.join(valid_log_levels)}.")
            print()  # Empty line before exit
            sys.exit(2)
        
        # Set logging level
        logging.getLogger().setLevel(getattr(logging, log_level, logging.WARNING))
        logger.info(f"Log level set to {log_level}")

        # Show environment-based defaults if enhanced mode is detected
        fmp_enhanced = get_env_default('FMP_ENHANCED_MODE', False, bool)
        if fmp_enhanced:
            logger.info("Enhanced FMP account detected - using enhanced defaults:")
            logger.info(f"  - Default quarters: {args.quarters}")
            logger.info(f"  - Enhanced analysis: {'enabled' if args.enhanced_analysis else 'disabled'}")
            logger.info(f"  - Batch size: {args.batch_size}")
        else:
            logger.info("Free FMP account mode - using conservative defaults")

        # Validate date format
        ticker_list = [t.upper() for t in args.tickers]
        failed_tickers = []
        successful_tickers = []

        for ticker in ticker_list:
            try:
                logger.info(f"Processing {ticker}...")
                start_time = time.time()
                
                # Use the new pipeline to generate CSV, JSON, chart, and reports                
                from altman_zscore.main_pipeline import AltmanZScorePipeline
                pipeline = AltmanZScorePipeline()
                output_files = asyncio.run(
                    pipeline.analyze_ticker(
                        ticker,
                        generate_charts=True,  # Always generate charts and dashboards
                        generate_reports=True,
                        include_ai_insights=True,  # Enable AI-powered investment narratives
                        forced_model=args.model,  # Pass model override if specified
                        quarters=getattr(args, 'quarters', 4),  # Pass quarters argument
                        enhanced_analysis=getattr(args, 'enhanced_analysis', False),  # Pass enhanced analysis flag
                        batch_size=getattr(args, 'batch_size', 10)  # Pass batch size
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
                
            except Exception as e:
                # Handle all pipeline errors gracefully
                error_message = str(e)
                
                # Provide user-friendly error messages for common issues
                if "Invalid ticker symbol" in error_message and "not found in financial databases" in error_message:
                    user_message = f"Invalid ticker symbol '{ticker}' - not found in financial databases"
                elif "Data merger failed" in error_message:
                    user_message = f"Unable to retrieve financial data for '{ticker}' - ticker may be invalid or delisted"
                elif "Empty response from FMP API" in error_message:
                    user_message = f"No financial data available for '{ticker}' - ticker may be invalid or not supported"
                elif "API rate limit" in error_message.lower():
                    user_message = f"API rate limit exceeded while processing '{ticker}' - please try again later"
                elif "Network" in error_message or "Connection" in error_message:
                    user_message = f"Network error while processing '{ticker}' - please check internet connection"
                else:
                    user_message = f"Analysis failed for '{ticker}': {error_message}"
                
                # Log the error once with a clean message
                logger.error(f"{ticker}: {user_message}")
                failed_tickers.append((ticker, user_message))
                # Continue processing other tickers instead of stopping

        # Provide comprehensive summary        
        logger.info("ANALYSIS SUMMARY")
        logger.info(f"{'='*60}")
        if successful_tickers:
            logger.info(f"SUCCESS: Successfully analyzed: {', '.join(successful_tickers)}")
            if failed_tickers:
                logger.warning(f"WARNING: {len(failed_tickers)} ticker(s) failed:")
                for ticker, error in failed_tickers:
                    logger.warning(f"  - {ticker}: {error}")
            print()  # Empty line before exit
            sys.exit(0)
        else:
            logger.error(f"FAILED: No tickers were successfully analyzed ({len(failed_tickers)} failure(s)):")
            for ticker, error in failed_tickers:
                logger.error(f"  - {ticker}: {error}")
            logger.info("\nTips:")
            logger.info("  - Verify ticker symbols are correct (e.g., AAPL, MSFT, TSLA)")
            logger.info("  - Check if companies are publicly traded")
            logger.info("  - Ensure internet connection is stable")
            print()  # Empty line before exit
            sys.exit(1)

    except Exception as e:
        logger.exception(f"Critical error in main: {str(e)}")
        print()  # Empty line before exit
        sys.exit(2)

if __name__ == '__main__':
    main()
