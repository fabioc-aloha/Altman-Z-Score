#!/usr/bin/env python3
"""
Test script to validate the fix for Z-score chart X-axis alignment with stock price overlay.
"""
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.plotting import plot_zscore_trend

def create_test_data():
    # Create synthetic Z-score data
    quarters = pd.date_range(start='2023-01-01', periods=6, freq='3M')
    zscores = [1.5, 2.0, 2.5, 3.0, 2.8, 3.5]
    
    # Create DataFrame for Z-scores
    zscore_df = pd.DataFrame({
        'quarter_end': quarters,
        'zscore': zscores
    })
    
    # Create synthetic price data
    price_dates = pd.date_range(start='2023-01-01', periods=180, freq='D')
    # Generate some price movements that follow a pattern
    base_price = 100
    prices = [base_price + np.sin(i/10) * 20 + i/5 for i in range(len(price_dates))]
    
    # Create DataFrame for prices
    price_df = pd.DataFrame({
        'Close': prices
    }, index=price_dates)
    
    return zscore_df, price_df

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    
    # Create test directory
    test_dir = os.path.join('output', 'TEST')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create synthetic data
    zscore_df, price_df = create_test_data()
    
    # Test the plot_zscore_trend function with our synthetic data
    plot_zscore_trend(
        df=zscore_df,
        ticker="TEST",
        model="original",
        out_base=os.path.join(test_dir, "zscore_TEST"),
        profile_footnote="Test data for alignment validation",
        price_data=price_df,
        save_svg=True
    )
    
    print("Test completed. Check output/TEST/zscore_TEST_trend.png to verify the fix.")