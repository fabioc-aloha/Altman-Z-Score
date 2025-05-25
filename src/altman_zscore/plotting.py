"""
Z-Score Trend Plotting Utilities

This module provides functions to plot the Altman Z-Score trend with risk zone bands,
value labels, robust legend, and company profile/model footnote.
Output is saved as PNG to output/.

Note: This code follows PEP 8 style guidelines.
"""

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import os
import sys
import importlib
import numpy as np
models = importlib.import_module('altman_zscore.models')
from altman_zscore.fetch_prices import get_market_data, get_closest_price

# ANSI color codes for terminal output if supported
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_info(msg):
    """Print an info message with cyan color if supported"""
    try:
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {msg}")
    except:
        print(f"[INFO] {msg}")

def print_warning(msg):
    """Print a warning message with yellow color if supported"""
    try:
        print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {msg}")
    except:
        print(f"[WARNING] {msg}")

def print_error(msg):
    """Print an error message with red color if supported"""
    try:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} {msg}")
    except:
        print(f"[ERROR] {msg}")

def plot_zscore_trend(df, ticker, model, out_base, profile_footnote=None):
    """
    Plot the Altman Z-Score trend with colored risk bands and save as PNG.

    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
        profile_footnote (str, optional): Footnote string for chart (company profile/model info)
    
    Returns:
        None. Saves PNG to output/ and prints absolute path.
    
    Notes:
        - Handles missing/invalid data gracefully.
        - Adds value labels, robust legend, and footnote.
        - Output directory is created if missing.
        - Overlays stock price trend on the Z-score chart.
    """
    plot_df = df[df["zscore"].notnull()]
    if plot_df.empty:
        print_warning("No valid Z-Score data to plot.")
        return
    
    print_info("Generating Z-Score trend plot...")
    plt.figure(figsize=(10, 5.5))  # Increased figure height slightly
    
    # Ensure chronological order by sorting by quarter_end
    plot_df = plot_df.copy()
    plot_df['quarter_end'] = pd.to_datetime(plot_df['quarter_end'])
    plot_df = plot_df.sort_values('quarter_end')
    zscores = plot_df["zscore"].astype(float)
    x = plot_df["quarter_end"]
    
    # Fetch stock prices for each quarter end date
    try:
        stock_prices = []
        date_strs = plot_df['quarter_end'].dt.strftime('%Y-%m-%d').tolist()
        
        # Fetch all stock prices
        for date_str in date_strs:
            try:
                # Get market data for the date
                market_data = get_market_data(ticker, date_str)
                price = get_closest_price(market_data, date_str)
                stock_prices.append(price)
            except Exception as e:
                print_warning(f"Could not fetch price for {ticker} on {date_str}: {str(e)}")
                # Use the previous price or None if no previous price
                stock_prices.append(stock_prices[-1] if stock_prices else None)
        
        # Make sure we have prices for all dates
        if len(stock_prices) != len(date_strs) or None in stock_prices:
            # Filter out None values and ensure lengths match
            valid_prices = [(i, p) for i, p in enumerate(stock_prices) if p is not None]
            if len(valid_prices) < len(date_strs):
                print_warning(f"Some stock prices could not be fetched for {ticker}.")
            
            # If we have at least some valid prices, use only those
            if valid_prices:
                indices, prices = zip(*valid_prices)
                stock_prices = list(prices)
                # Adjust plot_df and zscores to match the valid price dates
                plot_df = plot_df.iloc[list(indices)].copy()
                zscores = plot_df["zscore"].astype(float)
                x = plot_df["quarter_end"]
            else:
                print_warning(f"Could not fetch any valid stock prices for {ticker}")
                stock_prices = []
    except Exception as e:
        print_warning(f"Could not fetch stock prices for {ticker}: {str(e)}")
        stock_prices = []

    # Get thresholds for the model
    if model == "original":
        model_thresholds = models.ModelThresholds.original()
    elif model == "private":
        model_thresholds = models.ModelThresholds.private_company()
    elif model in ("public", "em", "service"):
        model_thresholds = models.ModelThresholds.non_manufacturing()
    else:
        model_thresholds = models.ModelThresholds.original()

    # Compute correct y-limits before drawing bands
    z_min = min(zscores.min(), float(model_thresholds.distress_zone))
    z_max = max(zscores.max(), float(model_thresholds.safe_zone))
    margin = 0.5 * (z_max - z_min) * 0.1  # 10% margin
    ymin = z_min - margin
    # Add extra padding to the top for the legend
    legend_padding = (z_max - z_min) * 0.18  # 18% of range for legend space
    ymax = z_max + margin + legend_padding
    plt.ylim(ymin, ymax)

    # Normalize stock prices to fit on the Z-score scale if we have prices
    if stock_prices and len(stock_prices) >= 2:
        # Min-max scaling to fit within Z-score range
        price_min, price_max = min(stock_prices), max(stock_prices)
        
        # Avoid division by zero
        price_range = price_max - price_min
        if price_range == 0:
            # If all prices are the same, center them in the middle of the chart
            norm_stock_prices = [z_min + (z_max - z_min) / 2] * len(stock_prices)
        else:
            # Scale to fit within 80% of the Z-score range
            z_range = z_max - z_min
            norm_stock_prices = [
                z_min + 0.1 * z_range + ((price - price_min) / price_range) * (0.8 * z_range)
                for price in stock_prices
            ]
    else:
        norm_stock_prices = []
    # Draw bands in order: distress (bottom), grey (middle), safe (top)
    plt.axhspan(ymin, float(model_thresholds.distress_zone), color='#ff6666', alpha=0.8, label='Distress Zone', zorder=0)
    plt.axhspan(float(model_thresholds.distress_zone), float(model_thresholds.safe_zone), color='#cccccc', alpha=0.6, label='Grey Zone', zorder=0)
    plt.axhspan(float(model_thresholds.safe_zone), ymax, color='#66ff66', alpha=0.5, label='Safe Zone', zorder=0)
    # Add zone names inside the plot area, aligned to the left and vertically centered in each band
    ax = plt.gca()
    zone_x = 0.1  # Slightly inside the plot area
    ax.text(zone_x, (ymin + float(model_thresholds.distress_zone)) / 2, 'Distress',
            color='#a60000', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    ax.text(zone_x, (float(model_thresholds.distress_zone) + float(model_thresholds.safe_zone)) / 2, 'Grey',
            color='#444444', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    # Lower the 'Safe' label to avoid the legend
    safe_y = (float(model_thresholds.safe_zone) + ymax) / 2
    if safe_y > ymax - (ymax - ymin) * 0.15:
        safe_y = ymax - (ymax - ymin) * 0.15
    ax.text(zone_x, safe_y, 'Safe',
            color='#007a00', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)

    # Use integer positions for x-axis to ensure correct plotting and annotation
    x_dates = plot_df['quarter_end']
    x_quarters = [f"{d.year}Q{((d.month-1)//3)+1}" for d in x_dates]
    x_pos = range(len(x_quarters))
    plt.plot(x_pos, zscores, marker='o', label="Z-Score", color='blue', zorder=2)
    
    # Plot the stock price line if we have data
    if norm_stock_prices and len(norm_stock_prices) == len(x_pos):
        # Plot the stock price line with a different color and style
        plt.plot(x_pos, norm_stock_prices, marker='^', label="Stock Value", 
                 color='green', linestyle='--', zorder=1)
        # Add value labels to each stock price point (show actual price)
        for i, (norm_price, actual_price) in enumerate(zip(norm_stock_prices, stock_prices)):
            try:
                label = f"${actual_price:.2f}"
                ax = plt.gca()
                ax.annotate(label, (i, norm_price), textcoords="offset points", 
                           xytext=(0,-15), ha='center', fontsize=8, color='green')
            except Exception:
                pass
        
    # Add value labels to each Z-Score point
    ax = plt.gca()
    for i, z_val in enumerate(zscores):
        try:
            label = f"{z_val:.2f}"
            ax.annotate(label, (i, z_val), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, color='blue')
        except Exception:
            pass
    # Format x-axis dates to show as quarters (e.g., '2024Q1'), horizontal
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_quarters, rotation=0, ha='center')
    
    # Add a second y-axis for actual stock prices if we have them
    if stock_prices and len(stock_prices) >= 2:
        ax2 = ax.twinx()
        price_min, price_max = min(stock_prices), max(stock_prices)
        price_margin = (price_max - price_min) * 0.1
        ax2.set_ylim(price_min - price_margin, price_max + price_margin)
        ax2.set_ylabel('Stock Price ($)', color='green')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # Plot invisible stock price line on the second axis for reference
        ax2.plot([], [], alpha=0)  # Invisible line to set up the axis
    
    # Get company name and prep title
    company_name = None
    try:
        import yfinance as yf
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        company_name = info.get('shortName') or info.get('longName')
    except Exception:
        company_name = None
    if not company_name:
        company_name = ticker.upper()

    # Create title and subtitle
    if norm_stock_prices:
        plt.title(f"Altman Z-Score Trend and Stock Value for {company_name} ({ticker.upper()})")
    else:
        plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    
    plt.xlabel("Quarter End")
    plt.ylabel("Z-Score")
    plt.grid(True, zorder=1)
    
    # Prepare threshold values for legend
    safe = float(model_thresholds.safe_zone)
    distress = float(model_thresholds.distress_zone)
    
    # Create legend patches
    legend_elements = [
        mpatches.Patch(facecolor='#ff6666', alpha=0.8, label=f'Distress Zone\n≤ {distress}'),
        mpatches.Patch(facecolor='#cccccc', alpha=0.6, label=f'Grey Zone\n{distress} to {safe}'),
        mpatches.Patch(facecolor='#66ff66', alpha=0.5, label=f'Safe Zone\n≥ {safe}'),
        Line2D([0], [0], color='blue', marker='o', label='Z-Score\nTrend Line', 
              markersize=4, linestyle='-', linewidth=1)
    ]
    
    # Add stock price line to legend if available
    if norm_stock_prices:
        legend_elements.append(
            Line2D([0], [0], color='green', marker='^', label='Stock Value\nTrend Line', 
                  markersize=4, linestyle='--', linewidth=1)
        )
    
    # Add legend with 4 columns (or 5 if stock price is included)
    num_cols = 5 if norm_stock_prices else 4
    plt.gcf().subplots_adjust(bottom=0.22)  # Increased bottom margin from 0.2 to 0.22
    plt.legend(handles=legend_elements, ncol=num_cols, bbox_to_anchor=(0.5, -0.25),  # Moved down from -0.15 to -0.25
              loc='center', fontsize=8, frameon=True, framealpha=0.9)
    
    # Add profile info as subtitle if available
    if profile_footnote:
        plt.figtext(0.5, 0.95, profile_footnote, 
                   ha='center', va='top', fontsize=9, color='#666666')
    
    # Ensure output subdirectory for ticker exists
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    
    out_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.png")
    plt.savefig(out_path)
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")
    
    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, 'ps1') or sys.flags.interactive:
        plt.show()
    # In headless or script mode, do not call plt.show() to avoid hangs
