#!/usr/bin/env python3
"""
Test script to validate that the Z-score chart X-axis and stock price line are properly aligned.
Tests both the original and fixed versions by creating a modified copy of the plotting function.
"""
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from copy import deepcopy

# Add src directory to path for relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from altman_zscore.plotting import plot_zscore_trend as plot_zscore_trend_fixed

# Create a copy of the original plot function for comparison
def plot_zscore_trend_original(df, ticker, model, out_base, profile_footnote=None, price_data=None, save_svg=False):
    """Original plotting function with the alignment issue."""
    import matplotlib.pyplot as plt
    import pandas as pd
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    import os
    import sys
    import importlib
    
    # The rest of the function is copied from the original with the issue
    plot_df = df[df["zscore"].notnull()]
    if plot_df.empty:
        print("No valid Z-Score data to plot.")
        return
    
    plt.figure(figsize=(10, 5.5))
    
    # Ensure chronological order by sorting by quarter_end
    plot_df = plot_df.copy()
    plot_df['quarter_end'] = pd.to_datetime(plot_df['quarter_end'])
    plot_df = plot_df.sort_values('quarter_end')
    zscores = plot_df["zscore"].astype(float)
    x = plot_df["quarter_end"]
    
    # Use dummy model thresholds for test
    class ModelThresholds:
        def __init__(self):
            self.safe_zone = 3.0
            self.distress_zone = 1.8
    
    model_thresholds = ModelThresholds()
    
    # Compute correct y-limits before drawing bands
    z_min = min(zscores.min(), float(model_thresholds.distress_zone))
    z_max = max(zscores.max(), float(model_thresholds.safe_zone))
    margin = 0.5 * (z_max - z_min) * 0.1  # 10% margin
    ymin = z_min - margin
    # Add extra padding to the top for the legend
    legend_padding = (z_max - z_min) * 0.18  # 18% of range for legend space
    ymax = z_max + margin + legend_padding
    plt.ylim(ymin, ymax)
    
    # Use integer positions for x-axis
    x_dates = plot_df['quarter_end']
    x_quarters = [f"{d.year}Q{((d.month-1)//3)+1}" for d in x_dates]
    x_pos = range(len(x_quarters))
    
    # Get primary axis and plot Z-Score
    ax = plt.gca()
    ax.plot(x_pos, zscores, marker='o', label="Z-Score", color='blue', zorder=2)
    
    # Handle secondary y-axis for price data if provided - THIS IS THE ORIGINAL CODE WITH THE ISSUE
    ax2 = None
    if price_data is not None and not price_data.empty:
        try:
            # Create secondary y-axis for stock price
            ax2 = ax.twinx()
            
            # Match price data with quarter dates
            price_at_quarters = []
            for date in x_dates:
                # Convert date to Timestamp if it's not already
                if not isinstance(date, pd.Timestamp):
                    date = pd.Timestamp(date)
                
                # Find closest price data point to the quarter end date
                if not price_data.empty:
                    # Calculate absolute difference between each price date and the target date
                    date_diffs = abs(price_data.index.astype('datetime64[ns]') - date.to_datetime64())
                    closest_idx = date_diffs.argmin()
                    price_at_quarters.append(price_data['Close'].iloc[closest_idx])
            
            # Plot stock price on secondary y-axis
            ax2.plot(x_pos, price_at_quarters, marker='s', linestyle='--', 
                     label="Stock Price", color='#d62728', zorder=1)
            
            # Configure secondary axis
            ax2.set_ylabel(f"Stock Price ($)", color='#d62728')
            ax2.tick_params(axis='y', colors='#d62728')
            
            # Optional: Add value labels to price points
            for i, price in enumerate(price_at_quarters):
                try:
                    label = f"${price:.2f}"
                    ax2.annotate(label, (i, price), textcoords="offset points", 
                                xytext=(0,8), ha='center', fontsize=9, 
                                color='#d62728', rotation=0)
                except Exception:
                    pass
        except Exception as e:
            print(f"Could not plot stock price data: {e}")
    
    # Format x-axis dates to show as quarters (e.g., '2024Q1'), horizontal
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_quarters, rotation=0, ha='center')
    
    plt.title(f"ORIGINAL: Chart with Alignment Issue")
    plt.xlabel("Quarter End")
    plt.ylabel("Z-Score")
    plt.grid(True, zorder=1)
    
    # Save the chart
    plt.savefig(f"{out_base}_original.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_test_data():
    """Creates test data with distinct patterns for better visualization of the alignment issue."""
    # Create synthetic Z-score data with a clear pattern
    quarters = pd.date_range(start='2023-01-01', periods=8, freq='3M')
    zscores = [1.5, 2.0, 2.5, 3.0, 2.8, 3.5, 3.2, 2.9]
    
    # Create DataFrame for Z-scores
    zscore_df = pd.DataFrame({
        'quarter_end': quarters,
        'zscore': zscores
    })
    
    # Create synthetic price data with an inverted pattern compared to Z-scores
    # This will make alignment issues more obvious
    price_dates = pd.date_range(start='2023-01-01', periods=240, freq='D')
    
    # Generate price data that follows a different pattern from Z-score
    # Start high and then drop, while Z-score starts low and increases
    base_price = 150
    prices = []
    for i in range(len(price_dates)):
        day_of_period = i % 90  # days within each quarter
        quarter_idx = i // 90   # which quarter we're in
        
        if quarter_idx >= len(zscores):
            quarter_idx = len(zscores) - 1
            
        # Create alignment pattern where prices drop when Z-scores rise and vice versa
        # This will make misalignment more obvious visually
        quarter_pattern = 90 - day_of_period  # descending within quarter
        price = base_price - (zscores[quarter_idx] * 10) + (quarter_pattern / 10)
        prices.append(price)
    
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
    
    # Test the original plot_zscore_trend function (with the alignment issue)
    plot_zscore_trend_original(
        df=zscore_df,
        ticker="TEST",
        model="original",
        out_base=os.path.join(test_dir, "zscore_alignment_test"),
        profile_footnote="Test data for alignment validation",
        price_data=price_df
    )
    
    # Test the fixed plot_zscore_trend function
    plot_zscore_trend_fixed(
        df=zscore_df,
        ticker="TEST",
        model="original",
        out_base=os.path.join(test_dir, "zscore_alignment_test_fixed"),
        profile_footnote="Test data for alignment validation",
        price_data=price_df,
        save_svg=True
    )
    
    print("Alignment test completed.")
    print("Check the following files to compare:")
    print(f"1. Original (with issue): {os.path.join(test_dir, 'zscore_alignment_test_original.png')}")
    print(f"2. Fixed version: {os.path.join(test_dir, 'zscore_alignment_test_fixed_trend.png')}")