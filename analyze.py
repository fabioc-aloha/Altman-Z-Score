#!/usr/bin/env python3
"""
Main entry point for the Altman Z-Score Analysis Tool.

This script serves as the primary interface for running the Altman Z-Score financial analysis
on companies, with a focus on AI and technology firms. It handles:

- Environment setup and configuration
- Execution of the main analysis pipeline

Usage:
    python analyze.py

The script will:
1. Set up the required directory structure
2. Execute the analysis pipeline defined in src.altman_zscore.main

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

def main():
    """Main entry point."""
    # First, ensure we can import our package
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        # Import and run analysis
        from src.altman_zscore.main import analyze_portfolio
        analyze_portfolio()
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
