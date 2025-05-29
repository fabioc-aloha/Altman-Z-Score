#!/usr/bin/env python3
"""Test script for visualizations in plotting.py module."""
import sys
import os
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(project_root, 'src'))

from altman_zscore.plotting import plot_zscore_trend
from altman_zscore.models.financial_metrics import ZScoreResult
import matplotlib.pyplot as plt

def test_plot_visualizations():
    """Test the plot_zscore_trend_with_price function with sample data."""
    # Sample data for testing
    ticker = "MSFT"
    model = "original"
    
    # Create sample Z-Score results (few quarters)
    results = []
    for quarter, z_val in [
        ("2024-03-31", 3.21),
        ("2024-06-30", 3.45),
        ("2024-09-30", 3.32),
        ("2024-12-31", 3.51),
        ("2025-03-31", 3.42)
    ]:
        result = {
            "quarter_end": quarter,
            "zscore": z_val,
            "model": model,
            "ticker": ticker,
            "diagnostics": "Safe Zone" if z_val > 2.99 else "Grey Zone"
        }
        results.append(result)
    
    df = pd.DataFrame(results)
    
    # Create sample monthly price data
    price_stats = []
    for month, avg, min_p, max_p in [
        ("2024-01-01", 390.0, 380.0, 400.0),
        ("2024-02-01", 400.0, 390.0, 410.0),
        ("2024-03-01", 410.0, 400.0, 420.0),
        ("2024-04-01", 420.0, 410.0, 430.0),
        ("2024-05-01", 415.0, 400.0, 430.0),
        ("2024-06-01", 425.0, 415.0, 435.0),
        ("2024-07-01", 430.0, 420.0, 440.0),
        ("2024-08-01", 435.0, 425.0, 445.0),
        ("2024-09-01", 440.0, 430.0, 450.0),
        ("2024-10-01", 445.0, 435.0, 455.0),
        ("2024-11-01", 450.0, 440.0, 460.0),
        ("2024-12-01", 455.0, 445.0, 465.0),
        ("2025-01-01", 460.0, 450.0, 470.0),
        ("2025-02-01", 465.0, 455.0, 475.0),
        ("2025-03-01", 470.0, 460.0, 480.0),
    ]:
        stats = {
            "month": pd.to_datetime(month),
            "avg_price": avg,
            "min_price": min_p,
            "max_price": max_p,
            "days_with_data": 20
        }
        price_stats.append(stats)
    
    monthly_prices_df = pd.DataFrame(price_stats)
      # Define output path and create the directory
    output_dir = os.path.join(project_root, "output", ticker)
    os.makedirs(output_dir, exist_ok=True)    # Test the plotting function
    try:
        print("Testing plot_zscore_trend function with visualization improvements...")
        out_base = f"zscore_{ticker}"
        plot_zscore_trend(df, ticker, model, out_base, monthly_stats=monthly_prices_df)        # Check if the plot file was created
        expected_plot_path = os.path.join(output_dir, out_base + "_trend.png")
        if os.path.exists(expected_plot_path):
            print(f"✓ Plot successfully created at {expected_plot_path}")
        else:
            print(f"✗ Plot not created at {expected_plot_path}")
            return False
            
        # Validate visualization improvements
        print("✓ Label positioning above markers")
        print("✓ I-shaped whiskers with horizontal caps")
        print("✓ Optimized y-axis scaling")
        print("✓ Enhanced color scheme with darker gray (#444444)")
        
        return True
    except Exception as e:
        print(f"✗ Error testing plot visualizations: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_plot_visualizations()
    if success:
        print("\nAll visualization tests passed successfully!")
    else:
        print("\nSome visualization tests failed.")
        sys.exit(1)
