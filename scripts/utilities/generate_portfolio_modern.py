#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modern Portfolio Generator - Replacement for all generate_*_picks.py files

This script serves as a unified replacement for all the individual 
generate_*_picks.py files, providing the same functionality through
a modern, modular architecture.

Original files replaced:
- generate_strong_buys.py / generate_strong_buys_modular.py
- generate_value_picks.py
- generate_growth_picks.py
- generate_dividend_picks.py
- generate_conservative_picks.py
- generate_aggressive_picks.py
- generate_sell_picks.py
- generate_strong_sell_picks.py

Usage (from project root):
    python generate_portfolio_modern.py strong_buy
    python generate_portfolio_modern.py value
    python generate_portfolio_modern.py growth
    python generate_portfolio_modern.py all
"""

import sys
import os
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change working directory to project root so the portfolio generator 
# can find the output directory with company data
os.chdir(PROJECT_ROOT)

from altman_zscore.scripts.generate_portfolio import main

if __name__ == "__main__":
    main()
