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
models = importlib.import_module('altman_zscore.models')

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

def plot_zscore_trend(df, ticker, model, out_base, profile_footnote=None, price_data=None, save_svg=False):
    """
    Plot the Altman Z-Score trend with colored risk bands and optional stock price overlay.

    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
        profile_footnote (str, optional): Footnote string for chart (company profile/model info)
        price_data (pd.DataFrame, optional): DataFrame with stock price data (datetime index and 'Close' column)
        save_svg (bool, optional): If True, also saves the chart as SVG
    
    Returns:
        None. Saves high-resolution PNG (and optionally SVG) to output/ and prints absolute path.
    
    Notes:
        - Handles missing/invalid data gracefully.
        - Adds value labels, robust legend, and footnote.
        - Output directory is created if missing.
        - Supports stock price overlay on secondary y-axis if price_data is provided.
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
    
    # Get primary axis and plot Z-Score
    ax = plt.gca()
    ax.plot(x_pos, zscores, marker='o', label="Z-Score", color='blue', zorder=2)
    
    # Add value labels to each Z-Score point
    for i, z_val in enumerate(zscores):
        try:
            label = f"{z_val:.2f}"
            ax.annotate(label, (i, z_val), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, color='blue')
        except Exception:
            pass
    
    # Handle secondary y-axis for price data if provided
    ax2 = None
    if price_data is not None and not price_data.empty:
        try:
            # Create secondary y-axis for stock price
            ax2 = ax.twinx()
            
            # Match price data with quarter dates - ensure exact alignment with Z-score x positions
            price_at_quarters = []
            
            # Create a dictionary mapping date strings to their corresponding price
            price_dict = {}
            for date_idx, row in price_data.iterrows():
                price_dict[pd.Timestamp(date_idx).strftime('%Y-%m-%d')] = row['Close']
            
            # For each quarter end date (same dates as Z-score data)
            for i, date in enumerate(x_dates):
                # Convert date to string in same format
                date_str = pd.Timestamp(date).strftime('%Y-%m-%d')
                
                # Find the closest date in price_data
                if not price_data.empty:
                    # Calculate absolute difference between each price date and the target date
                    date_diffs = abs(price_data.index.astype('datetime64[ns]') - pd.Timestamp(date).to_datetime64())
                    closest_idx = date_diffs.argmin()
                    closest_date = price_data.index[closest_idx]
                    price = price_data['Close'].iloc[closest_idx]
                    
                    # Add the price at the exact same position as the Z-score point
                    price_at_quarters.append(price)
            
            # Plot stock price on secondary y-axis using exactly the same x positions as Z-score
            ax2.plot(x_pos, price_at_quarters, marker='s', color='green', linestyle='-', linewidth=1.5, 
                     label=f"{ticker} Price", zorder=1)
            
            # Configure secondary axis
            ax2.set_ylabel(f"Stock Price ($)", color='green')
            ax2.tick_params(axis='y', labelcolor='green')
            
            # Optional: Add value labels to price points
            for i, price in enumerate(price_at_quarters):
                try:
                    label = f"${price:.2f}"
                    ax2.annotate(label, (i, price), 
                                textcoords="offset points", xytext=(0,-15), 
                                ha='center', fontsize=9, color='green')
                except Exception:
                    pass
        except Exception as e:
            print_warning(f"Could not plot stock price data: {e}")
    
    # Format x-axis dates to show as quarters (e.g., '2024Q1'), horizontal
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_quarters, rotation=0, ha='center')

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

    # Create title with price overlay indicator if applicable
    if price_data is not None and not price_data.empty:
        plt.title(f"Altman Z-Score Trend with Stock Price Overlay for {company_name} ({ticker.upper()})")
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
    
    # Add stock price to legend if it was plotted
    if ax2 is not None:
        legend_elements.append(
            Line2D([0], [0], color='green', marker='s', label=f'{ticker} Price', 
                  markersize=4, linestyle='-', linewidth=1.5)
        )
    
    # Adjust bottom margin based on legend size
    margin_factor = 0.22 if len(legend_elements) <= 4 else 0.25
    plt.gcf().subplots_adjust(bottom=margin_factor)
    
    # Add legend with appropriate number of columns
    ncols = 4 if len(legend_elements) <= 4 else 5
    plt.legend(handles=legend_elements, ncol=ncols, bbox_to_anchor=(0.5, -0.25),
              loc='center', fontsize=8, frameon=True, framealpha=0.9)
    
    # Add profile info as subtitle if available
    if profile_footnote:
        plt.figtext(0.5, 0.95, profile_footnote, 
                   ha='center', va='top', fontsize=9, color='#666666')
    
    # Add explanation footnote about Z-Score and stock prices
    explanation_footnote = (
        "Z-Score Interpretation: <1.8: High distress risk | 1.8-2.99: Grey zone | ≥3.0: Safe zone\n" +
        "Stock price overlay shows relative price performance during the period analyzed"
    ) if price_data is not None else (
        "Z-Score Interpretation: <1.8: High distress risk | 1.8-2.99: Grey zone | ≥3.0: Safe zone"
    )
    
    plt.figtext(0.5, 0.01, explanation_footnote,
               ha='center', va='bottom', fontsize=8, color='#444444',
               bbox=dict(boxstyle="round,pad=0.5", fc="#f9f9f9", ec="#cccccc", alpha=0.8))
    
    # Ensure output subdirectory for ticker exists
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    
    # Save high-resolution PNG (300 dpi)
    out_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")
    
    # Save as SVG if requested
    if save_svg:
        svg_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.svg")
        try:
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
            print_info(f"Z-Score trend plot also saved as SVG: {os.path.abspath(svg_path)}")
        except Exception as e:
            print_warning(f"Could not save SVG format: {e}")
    
    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, 'ps1') or sys.flags.interactive:
        plt.show()
    # In headless or script mode, do not call plt.show() to avoid hangs
