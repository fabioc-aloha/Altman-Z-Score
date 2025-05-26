#!/usr/bin/env python3
"""
Test script to reproduce the Z-score chart alignment issue with stock price overlay.
"""
import os
import sys
import matplotlib.pyplot as plt

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.one_stock_analysis import analyze_single_stock_zscore_trend

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    # Using MSFT as mentioned in the problem statement
    analyze_single_stock_zscore_trend("MSFT")
    print("Test completed.")