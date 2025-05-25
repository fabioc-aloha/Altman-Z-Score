#!/usr/bin/env python3
"""
Test script for the Altman Z-Score plotting module with stock price overlay.
This script tests the plotting functionality independently of the full pipeline.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.plotting import plot_zscore_trend

# Create a simple ModelThresholds mock class for testing
class MockModelThresholds:
    @staticmethod
    def original():
        class Thresholds:
            safe_zone = 3.0
            distress_zone = 1.8
        return Thresholds()

# Monkey patch the models module reference in the plotting module
import sys
import types
mock_models = types.ModuleType('mock_models')
mock_models.ModelThresholds = MockModelThresholds
sys.modules['altman_zscore.models'] = mock_models

def test_zscore_with_price_overlay():
    """Test the Z-Score plotting with price overlay."""
    # Create sample data
    quarters = pd.date_range(start='2023-01-01', periods=8, freq='3M')
    zscores = [2.5, 2.7, 2.9, 3.1, 3.0, 2.8, 2.6, 2.4]
    
    # Create DataFrame with quarter_end and zscore columns
    df = pd.DataFrame({
        'quarter_end': quarters,
        'zscore': zscores
    })
    
    # Create sample price data (daily)
    price_dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    price_data = pd.DataFrame(
        index=price_dates,
        data={'Close': np.linspace(100, 150, len(price_dates)) + np.sin(np.linspace(0, 8*np.pi, len(price_dates)))*10}
    )
    
    # Create output directory if it doesn't exist
    if not os.path.exists('output/TEST'):
        os.makedirs('output/TEST', exist_ok=True)
    
    # Test plotting with and without price overlay
    print("Testing Z-Score plot without price overlay...")
    plot_zscore_trend(df, 'TEST', 'original', 'output/TEST/without_price', 
                      profile_footnote="Test Company | Model: original", 
                      price_data=None, save_svg=True)
    
    print("Testing Z-Score plot with price overlay...")
    plot_zscore_trend(df, 'TEST', 'original', 'output/TEST/with_price', 
                      profile_footnote="Test Company | Model: original", 
                      price_data=price_data, save_svg=True)
    
    print("Test completed. Check output/TEST/ directory for the generated plots.")

if __name__ == "__main__":
    test_zscore_with_price_overlay()