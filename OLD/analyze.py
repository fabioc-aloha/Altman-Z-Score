#!/usr/bin/env python3
"""
Main entry point for the Altman Z-Score Analysis Tool.

This script serves as the primary interface for running the Altman Z-Score financial analysis
on companies, with a focus on AI and technology firms. It handles:

- Environment setup and configuration
- Execution of the main analysis pipeline

Usage:
    python analyze.py [--tickers TICKER1 TICKER2 ...]

The script will:
1. Set up the required directory structure
2. Execute the analysis pipeline defined in src.altman_zscore.portfolio_analyzer

Configuration:
    The script creates and manages the following directories:
    - output/: For analysis results and reports

Notes:
    - The analysis uses both SEC EDGAR data and Yahoo Finance market data
"""

import os
import sys
import shutil
from pathlib import Path
import argparse
import logging
from prometheus_client import start_http_server

from src.altman_zscore.config import Config
from src.altman_zscore.portfolio_analyzer import analyze_portfolio

def main():
    """Main entry point."""
    # First, ensure project root is on path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Start Prometheus metrics server
    metrics_port = int(os.getenv('METRICS_PORT', '8000'))
    start_http_server(metrics_port)
    logging.getLogger().info(f"Prometheus metrics available on port {metrics_port}")

    parser = argparse.ArgumentParser(description="Altman Z-Score Analysis Tool")
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Optional list of tickers to analyze. If not provided, uses default portfolio.",
    )
    args = parser.parse_args()

    try:
        # Initialize config and determine tickers
        config = Config()
        tickers = args.tickers if args.tickers else config.portfolio
        # Run analysis pipeline
        analyze_portfolio(
            config_instance=config,
            tickers=tickers,
            end_date_str=config.period_end_date,
            output_dir_path=config.output_dir,
            price_start_date_str=config.price_start_date,
            price_end_date_str=config.price_end_date
        )

    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
