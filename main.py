#!/usr/bin/env python3
# Version: Dynamic from _version.py - AI-Powered Altman Z-Score Analysis
"""
AI-Powered Altman Z-Score Analysis - Main Entry Point

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with
FMP pre-calculated ratios and LLM-powered qualitative insights. This script orchestrates 
the analysis pipeline for single or multiple stock tickers.

🎯 **Strategic Architecture: Modern Multi-Model Z-Score Analysis**
Features breakthrough retail-specific Z-Score model with inventory turnover integration,
alongside traditional models optimized for different industry sectors and company types.

💎 **DIAMOND v4.5.0: Academic Excellence & Novel Retail Model**
- Novel retail Z-Score model with revolutionary X₆ inventory component
- Academic-grade documentation with peer-review ready research
- Comprehensive empirical validation framework with 75-company backtest
- Production-ready automation with PowerShell/batch validation scripts

Architecture Overview:
    1. Input Layer: Accepts ticker(s) and analysis parameters; validates input.
    2. FMP Data Fetching: Fetches pre-calculated financial ratios with 48-hour caching.
    3. Yahoo Market Data: Fetches market data (prices, market cap) with 48-hour caching.
    4. Data Integration: Merges FMP ratios with Yahoo market data through quality gates.
    5. Z-Score Calculation: Industry-specific model selection with novel retail enhancement.
    6. AI Analysis: Azure OpenAI generates intelligent insights and commentary.
    7. Reporting Layer: Outputs results to CSV, JSON, charts, and comprehensive reports.

Key Principles:
    - **Academic Innovation**: Novel retail Z-Score model with inventory turnover integration
    - **API-First**: FMP provides calculation-ready ratios, Yahoo provides market data
    - **Intelligent Caching**: 48-hour TTL for all API calls, ~95% performance improvement
    - **Industry-Specific**: Automated model selection for optimal sector analysis
    - **AI Enhancement**: LLM for insights and commentary, not core data processing
    - **Production Ready**: Thread-safe operations with comprehensive error handling

Data Sources:
    - **Primary Financial**: FMP API with pre-calculated Z-Score ratios (no field mapping needed)
    - **Market Data**: Yahoo Finance for real-time pricing and market capitalization
    - **AI Analysis**: Azure OpenAI for intelligent insights and commentary generation

Strategic Advantages:
    - **Novel Retail Model**: First academic retail-specific Z-Score enhancement with X₆ component
    - **Pre-calculated Ratios**: Working Capital/Total Assets, EBIT/Total Assets, etc. ready for use
    - **Lightning Fast**: 48-hour caching + pre-calculated ratios = optimal performance
    - **Academic Rigor**: Literature-compliant implementations with peer-review documentation
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

# Import version from centralized location
from altman_zscore._version import __version__


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
import os
from typing import List
from dateutil.relativedelta import relativedelta

import pandas as pd

# Prevent automatic logging initialization from altman_zscore modules
os.environ["ALTMAN_ZSCORE_SKIP_LOGGING_INIT"] = "1"

# Import and initialize proper logging configuration first
from altman_zscore.common.logging_config import LoggingConfig, get_logger

# Initialize logger (logging config will be set up later based on CLI args)
logger = get_logger(__name__)

# Import new refactored pipeline
from altman_zscore.main_pipeline import AltmanZScorePipeline
import asyncio

# CLI help epilog - single source of truth
CLI_EPILOG = ("Examples:\n"
              "  python main.py AAPL                        # Single stock analysis\n"
              "  python main.py AAPL MSFT GOOGL             # Multi-stock portfolio analysis\n"
              "  python main.py --portfolio-file portfolios/tech_portfolio.txt  # Analyze portfolio from file\n"
              "  python main.py --sector technology         # Analyze technology sector portfolio\n"
              "  python main.py TSLA --quarters 8           # Multi-quarter analysis\n"
              "  python main.py AAPL --model financial      # Force financial institution model\n"
              "  python main.py --clear-cache               # Clear all API caches\n"
              "  python main.py --cache-stats               # Show cache statistics\n"
              "  python main.py --log-level DEBUG           # Enable debug logging\n"
              "  python main.py --log-structured            # Enable JSON structured logging\n"
              "  python main.py --log-dir ./my-logs         # Custom log directory\n"
              "  python main.py --progress always           # Always show progress bars\n"
              "  python main.py --progress never            # Never show progress bars\n"
              "  python main.py AAPL --forecast-off         # Disable Z-Score forecasting\n"
              "  python main.py TSLA --forecast-years 3     # 3-year forecast (default: 1 year)\n"
              "  python main.py --portfolio-file portfolio.txt --skip-existing  # Process only new tickers")

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

def load_portfolio_from_file(file_path: str) -> list:
    """Load ticker symbols from a portfolio file with inline comment support."""
    from altman_zscore.common.utils import load_portfolio_from_file as centralized_loader
    
    try:
        return centralized_loader(file_path, validate_tickers=True)
    except Exception as e:
        print(f"Error loading portfolio file {file_path}: {e}")
        return []


def get_sector_portfolio(sector: str) -> list:
    """Get pre-defined sector portfolio tickers."""
    sector_portfolios = {
        'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM'],
        'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'DHR', 'AMGN', 'GILD', 'MRNA', 'CVS'],
        'financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'USB', 'PNC', 'BK'],
        'industrial': ['CAT', 'DE', 'MMM', 'HON', 'UPS', 'GD', 'LMT', 'RTX', 'BA', 'FDX'],
        'energy': ['XOM', 'CVX', 'COP', 'EOG', 'PXD', 'SLB', 'HAL', 'KMI', 'WMB', 'NEE']
    }
    return sector_portfolios.get(sector.lower(), [])


def check_existing_analysis(ticker: str, output_base_dir: str = "output") -> bool:
    """
    Check if analysis outputs already exist for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        output_base_dir: Base output directory (default: "output")
    
    Returns:
        bool: True if existing analysis files are found, False otherwise
    """
    from pathlib import Path
    
    ticker_dir = Path(output_base_dir) / ticker.upper()
    
    if not ticker_dir.exists():
        return False
    
    # Check for key output files that indicate completed analysis
    expected_files = [
        f"zscore_{ticker.upper()}.csv",  # CSV output
        f"zscore_{ticker.upper()}.json",  # JSON output
        f"zscore_{ticker.upper()}_zscore_full_report.md"  # Full report
    ]
    
    existing_files = []
    for expected_file in expected_files:
        file_path = ticker_dir / expected_file
        if file_path.exists() and file_path.stat().st_size > 0:  # File exists and is not empty
            existing_files.append(expected_file)
    
    # Consider analysis complete if we have at least CSV and JSON outputs
    has_core_outputs = any(f.endswith('.csv') for f in existing_files) and any(f.endswith('.json') for f in existing_files)
    
    return has_core_outputs


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
        
        # Strip inline comments (everything after #)
        if '#' in env_value:
            env_value = env_value.split('#')[0].strip()
        
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
        "--log-structured",
        action="store_true",
        default=get_env_default("LOG_STRUCTURED", False, bool),
        help="Enable structured JSON logging output. "
             f"Default: {get_env_default('LOG_STRUCTURED', False, bool)} (from .env or False)."
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=get_env_default("LOG_DIR", "logs"),
        help="Directory for log files. "
             f"Default: {get_env_default('LOG_DIR', 'logs')} (from .env or 'logs')."
    )
    parser.add_argument(
        "--log-file-level",
        type=str,
        default=get_env_default("LOG_FILE_LEVEL", "DEBUG"),
        help="Set file logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
             f"Default: {get_env_default('LOG_FILE_LEVEL', 'DEBUG')} (from .env or DEBUG)."
    )
    parser.add_argument(
        "--progress",
        type=str,
        choices=["auto", "always", "never"],
        default=get_env_default("SHOW_PROGRESS_BARS", "auto"),
        help="Control progress bar display. 'auto' shows progress bars when logging is quiet (WARNING/ERROR/CRITICAL), "
             "'always' shows them regardless of log level, 'never' disables them. "
             f"Default: {get_env_default('SHOW_PROGRESS_BARS', 'auto')} (from .env or auto)."
    )
    parser.add_argument(
        "--portfolio-file",
        type=str,
        help="File containing list of tickers (one per line, comments with # ignored). "
             "Useful for analyzing predefined portfolios or large lists of stocks."
    )
    parser.add_argument(
        "--sector",
        type=str,
        choices=["technology", "healthcare", "financial", "industrial", "energy"],
        help="Pre-defined sector portfolio for quick analysis. "
             "Available sectors: technology, healthcare, financial, industrial, energy."
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
    parser.add_argument(
        "--forecast-off",
        action="store_true",
        help="Disable Z-Score forecasting. By default, forecasting is enabled and generates "
             "forward-looking Z-Score projections using analyst consensus estimates."
    )
    parser.add_argument(
        "--forecast-years",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="Number of years to forecast Z-Scores (1-3 years). "
             "Default: 1 year. Requires analyst consensus data availability."
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip tickers that already have analysis outputs in the output directory. "
             "Useful for processing only new entries when portfolio is updated. "
             "Checks for existence of CSV, JSON, and report files before processing."
    )
    # Add more feature toggles here as needed
    return parser.parse_args()


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
        has_ticker_source = args.tickers or args.portfolio_file or args.sector
        if len(sys.argv) == 1 or (not has_ticker_source and not getattr(args, "clear_cache", False) and not getattr(args, "cache_stats", False)):
            parser = argparse.ArgumentParser(
                description=CLI_DESCRIPTION,                
                epilog=CLI_EPILOG,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            parser.print_help()
            print()  # Empty line before exit
            sys.exit(0)

        # Validate log levels
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        log_level = args.log_level.upper()
        file_log_level = args.log_file_level.upper()
        
        if log_level not in valid_log_levels:
            print(f"Error: Invalid console log level: {args.log_level}. Must be one of: {', '.join(valid_log_levels)}.")
            print()  # Empty line before exit
            sys.exit(2)
            
        if file_log_level not in valid_log_levels:
            print(f"Error: Invalid file log level: {args.log_file_level}. Must be one of: {', '.join(valid_log_levels)}.")
            print()  # Empty line before exit
            sys.exit(2)
        
        # Initialize proper logging configuration with CLI preferences
        logging_config = LoggingConfig(
            log_dir=args.log_dir,
            console_level=log_level,
            file_level=file_log_level,
            structured_output=args.log_structured
        )
        logging_config.setup_logging()
        
        # Set progress bar preference from CLI argument
        os.environ["SHOW_PROGRESS_BARS"] = args.progress
        
        # Get fresh logger instance after config setup
        logger = get_logger(__name__)
        logger.info(f"Console log level set to {log_level}")
        logger.info(f"File log level set to {file_log_level}")
        logger.info(f"Progress bars set to '{args.progress}' mode")
        logger.info(f"Log directory: {args.log_dir}")
        if args.log_structured:
            logger.info("Structured JSON logging enabled")
            
        # Test logging levels to verify configuration
        logger.debug("Debug logging test - this should only appear if debug level is enabled")
        logger.info("Info logging test - logging configuration successful")

        # Show environment-based defaults
        logger.info("Using defaults based on configuration:")
        logger.info(f"  - Default quarters: {args.quarters}")
        logger.info(f"  - Batch size: {args.batch_size}")

        # Determine ticker list from various sources
        ticker_list = []
        
        if args.portfolio_file:
            ticker_list = load_portfolio_from_file(args.portfolio_file)
            if not ticker_list:
                logger.error(f"No valid tickers found in portfolio file: {args.portfolio_file}")
                sys.exit(1)
            logger.info(f"Loaded {len(ticker_list)} tickers from portfolio file: {args.portfolio_file}")
        elif args.sector:
            ticker_list = get_sector_portfolio(args.sector)
            if not ticker_list:
                logger.error(f"Unknown sector: {args.sector}")
                sys.exit(1)
            logger.info(f"Loaded {len(ticker_list)} tickers from {args.sector} sector portfolio")
        else:
            ticker_list = [t.upper() for t in args.tickers]
        
        if not ticker_list:
            logger.error("No tickers specified. Use --help for usage instructions.")
            sys.exit(1)
        
        # Filter out existing tickers if --skip-existing is enabled
        original_count = len(ticker_list)
        if getattr(args, 'skip_existing', False):
            logger.info("Checking for existing analysis outputs...")
            filtered_list = []
            skipped_tickers = []
            
            for ticker in ticker_list:
                if check_existing_analysis(ticker):
                    skipped_tickers.append(ticker)
                    logger.debug(f"Skipping {ticker} - analysis outputs already exist")
                else:
                    filtered_list.append(ticker)
            
            ticker_list = filtered_list
            
            if skipped_tickers:
                logger.info(f"Skipped {len(skipped_tickers)} tickers with existing analysis: {', '.join(skipped_tickers[:10])}")
                if len(skipped_tickers) > 10:
                    logger.info(f"... and {len(skipped_tickers) - 10} more")
            
            if not ticker_list:
                logger.info(f"All {original_count} tickers already have analysis outputs. Nothing to process.")
                logger.info("Use without --skip-existing to re-analyze all tickers.")
                print()  # Empty line before exit
                sys.exit(0)
            elif len(ticker_list) < original_count:
                logger.info(f"Processing {len(ticker_list)} new tickers (out of {original_count} total)")
        
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
                        # Removed: include_ai_insights (now using comprehensive AI commentary directly)
                        forced_model=args.model,  # Pass model override if specified
                        quarters=getattr(args, 'quarters', 4),  # Pass quarters argument
                        batch_size=getattr(args, 'batch_size', 10),  # Pass batch size
                        enable_forecasting=not getattr(args, 'forecast_off', False),  # Forecast enabled by default unless --forecast-off
                        forecast_years=getattr(args, 'forecast_years', 1)  # Pass forecast years
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
