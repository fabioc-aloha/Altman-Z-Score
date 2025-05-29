"""
Z-Score Trend Plotting Utilities

This module provides functions to plot the Altman Z-Score trend, generate component and full reports, and output results to files. It supports robust error handling, clear legends, and company profile/model context in all outputs.

Key Features:
- Plots Z-Score trend with risk zone bands and value labels
- Generates component and full reports with context, formulas, and diagnostics
- Handles missing/invalid data gracefully
- Compatible with Codespaces and local environments
- All outputs saved to output/<TICKER>/
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
from altman_zscore.reporting import report_zscore_full_report
from altman_zscore.utils.paths import get_output_dir

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

def get_output_ticker_dir(ticker):
    """Return the absolute output directory for a given ticker, ensuring it exists."""
    return get_output_dir(ticker=ticker)

def get_zscore_thresholds(model):
    """Return distress and safe zone thresholds for the given model name."""
    # These values are based on standard Altman Z-Score literature
    if model == "original":
        return {"distress_zone": 1.81, "safe_zone": 2.99}
    elif model == "private":
        return {"distress_zone": 1.23, "safe_zone": 2.90}
    elif model in ("public", "em", "service", "tech"):
        return {"distress_zone": 1.1, "safe_zone": 2.6}
    else:
        # Fallback to original model thresholds
        return {"distress_zone": 1.81, "safe_zone": 2.99}

def plot_zscore_trend(df, ticker, model, out_base, profile_footnote=None, stock_prices=None, monthly_stats=None):
    """
    Plot the Altman Z-Score trend with colored risk bands and save as PNG.
    If stock_prices provided, overlays stock price trend on secondary y-axis.

    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
        profile_footnote (str, optional): Footnote string for chart (company profile/model info)
        stock_prices (pd.DataFrame, optional): DataFrame with columns ['quarter_end', 'price'] for overlaying stock prices
        monthly_stats (pd.DataFrame, optional): DataFrame with monthly price statistics
    Returns:
        None. Saves PNG to output/ and prints absolute path.
    Notes:
        - Handles missing/invalid data gracefully.
        - Adds value labels, robust legend, and footnote.
        - Output directory is created if missing.
        - When stock_prices provided, shows price trend on secondary y-axis.
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
    thresholds = get_zscore_thresholds(model)

    # Compute correct y-limits before drawing bands
    z_min = min(zscores.min(), float(thresholds["distress_zone"]))
    z_max = max(zscores.max(), float(thresholds["safe_zone"]))
    margin = 0.5 * (z_max - z_min) * 0.15  # Increased margin from 0.1 to 0.15
    ymin = z_min - margin
    # Add extra padding to the top for the legend
    legend_padding = (z_max - z_min) * 0.18  # 18% of range for legend space
    ymax = z_max + margin + legend_padding
    plt.ylim(ymin, ymax)
    # Draw bands in order: distress (bottom), grey (middle), safe (top)
    plt.axhspan(ymin, float(thresholds["distress_zone"]), color='#ff6666', alpha=0.8, label='Distress Zone', zorder=0)
    plt.axhspan(float(thresholds["distress_zone"]), float(thresholds["safe_zone"]), color='#cccccc', alpha=0.6, label='Grey Zone', zorder=0)
    plt.axhspan(float(thresholds["safe_zone"]), ymax, color='#66ff66', alpha=0.5, label='Safe Zone', zorder=0)
    # Add zone names inside the plot area, aligned to the left and vertically centered in each band
    ax = plt.gca()
    zone_x = 0.1  # Slightly inside the plot area
    ax.text(zone_x, (ymin + float(thresholds["distress_zone"])) / 2, 'Distress',
            color='#a60000', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    ax.text(zone_x, (float(thresholds["distress_zone"]) + float(thresholds["safe_zone"])) / 2, 'Grey',
            color='#444444', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    # Lower the 'Safe' label to avoid the legend
    safe_y = (float(thresholds["safe_zone"]) + ymax) / 2
    if safe_y > ymax - (ymax - ymin) * 0.15:
        safe_y = ymax - (ymax - ymin) * 0.15
    ax.text(zone_x, safe_y, 'Safe',
            color='#007a00', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)    # Create monthly timeline that spans from earliest to latest dates
    x_dates = plot_df['quarter_end']
    
    # Determine the full date range including monthly data if available
    min_date = x_dates.min()
    max_date = x_dates.max()
    
    # If monthly stats are available, extend the range to include all months
    if monthly_stats is not None and not monthly_stats.empty:
        monthly_dates = pd.to_datetime(monthly_stats['month'])
        min_date = min(min_date, monthly_dates.min())
        max_date = max(max_date, monthly_dates.max())
    
    # Create monthly timeline from min to max date
    month_range = pd.date_range(start=min_date.replace(day=1), 
                               end=max_date.replace(day=1), 
                               freq='MS')  # Month Start frequency
    
    # Create position mapping: each month gets an integer position
    month_to_pos = {month: i for i, month in enumerate(month_range)}
    
    # Map quarter dates to their corresponding month positions
    quarter_positions = []
    for quarter_date in x_dates:
        quarter_month = quarter_date.replace(day=1)
        quarter_positions.append(month_to_pos.get(quarter_month, -1))
    
    # Plot Z-scores at their quarter positions
    valid_quarters = [(pos, zscore) for pos, zscore in zip(quarter_positions, zscores) if pos != -1]
    if valid_quarters:
        q_pos, q_scores = zip(*valid_quarters)
        plt.plot(q_pos, q_scores, marker='o', label="Z-Score", color='blue', zorder=2)
          # Add value labels to each Z-Score point
        ax = plt.gca()
        for pos, z_val in zip(q_pos, q_scores):
            try:
                label = f"{z_val:.2f}"
                ax.annotate(text=label, xy=(pos, z_val), textcoords="offset points", xytext=(0,12), ha='center', fontsize=9, color='blue')
            except Exception:
                pass
    
    # Format x-axis to show months
    month_labels = [f"{month.strftime('%Y-%m')}" for month in month_range]
    ax = plt.gca()
    ax.set_xticks(list(range(len(month_range))))
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    
    # Store the month range and position mapping for stock price plotting
    global_month_range = month_range
    global_month_to_pos = month_to_pos

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
        company_name = ticker.upper()    # Create title and subtitle
    plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    
    plt.xlabel("Month")
    plt.ylabel("Z-Score")
    plt.grid(True, zorder=1)
    
    # Prepare threshold values for legend
    safe = float(thresholds["safe_zone"])
    distress = float(thresholds["distress_zone"])
    
    # Create legend patches
    legend_elements = [
        mpatches.Patch(facecolor='#ff6666', alpha=0.8, label=f'Distress Zone\n≤ {distress}'),
        mpatches.Patch(facecolor='#cccccc', alpha=0.6, label=f'Grey Zone\n{distress} to {safe}'),
        mpatches.Patch(facecolor='#66ff66', alpha=0.5, label=f'Safe Zone\n≥ {safe}'),
        Line2D([0], [0], color='blue', marker='o', label='Z-Score\nTrend Line', 
              markersize=4, linestyle='-', linewidth=1)
    ]
    
    # If monthly_stats are provided, plot monthly average and range as the stock price line
    if monthly_stats is not None and not monthly_stats.empty:
        ax2 = ax.twinx()
        monthly_stats['month'] = pd.to_datetime(monthly_stats['month'])
        # Sort by month
        monthly_stats = monthly_stats.sort_values('month')
        # Map months to positions
        month_positions = [global_month_to_pos.get(month, -1) for month in monthly_stats['month']]
        # Only keep valid positions
        valid = [i for i, pos in enumerate(month_positions) if pos != -1]
        month_positions = [month_positions[i] for i in valid]
        avg_prices = [monthly_stats.iloc[i]['avg_price'] for i in valid]
        min_prices = [monthly_stats.iloc[i]['min_price'] for i in valid]
        max_prices = [monthly_stats.iloc[i]['max_price'] for i in valid]
        
        # Plot price data with adjusted axis
        dark_gray = '#444444'  # Darker gray for better visibility
        ax2.plot(month_positions, avg_prices, marker='o', color=dark_gray, 
                linestyle='-', linewidth=2, label='Monthly Avg Price', zorder=3)
        
        # Plot I-shaped whiskers for min/max range
        whisker_width = 0.3  # Width of the horizontal caps
        for pos, min_p, max_p in zip(month_positions, min_prices, max_prices):
            # Vertical line
            ax2.vlines(pos, min_p, max_p, color=dark_gray, alpha=0.8, linewidth=1, zorder=2)
            # Horizontal caps at top and bottom
            ax2.hlines(min_p, pos - whisker_width/2, pos + whisker_width/2, 
                      color=dark_gray, alpha=0.8, linewidth=1, zorder=2)
            ax2.hlines(max_p, pos - whisker_width/2, pos + whisker_width/2, 
                      color=dark_gray, alpha=0.8, linewidth=1, zorder=2)
        
        # Add value labels with more space
        for pos, avg in zip(month_positions, avg_prices):
            try:
                avg_label = f"${avg:.2f}"
                ax2.annotate(text=avg_label, xy=(pos, avg), 
                           textcoords="offset points", xytext=(0,12),  # Position closer to data point
                           ha='center', fontsize=7, color=dark_gray, alpha=0.8)
            except Exception:
                pass
        
        # Adjust price axis appearance and limits
        ax2.set_ylabel("Stock Price ($)", color=dark_gray, labelpad=15)  # Add padding between axis and label
        ax2.tick_params(axis='y', labelcolor=dark_gray, pad=8)  # Add padding between axis and tick labels
        y_min, y_max = ax2.get_ylim()
        price_range = y_max - y_min
        price_margin = price_range * 0.25  # 25% margin for price axis
        ax2.set_ylim(bottom=max(0, y_min - price_margin * 0.5),  # Less margin at bottom
                    top=y_max + price_margin)  # More margin at top for labels
        
        # Update legend for monthly stats
        legend_elements.append(
            Line2D([0], [0], color=dark_gray, marker='o', label='Monthly Avg Price', 
                  markersize=4, linestyle='-', linewidth=2)
        )
        legend_elements.append(
            Line2D([0], [0], color=dark_gray, label='Monthly Range', 
                  markersize=4, linestyle='-', linewidth=2, alpha=0.8)
        )
    # Add legend extending horizontally in one line
    plt.gcf().subplots_adjust(bottom=0.22)  # Increased bottom margin for horizontal legend
    # Use all elements in a single horizontal row
    num_cols = len(legend_elements)
    plt.legend(handles=legend_elements, ncol=num_cols, bbox_to_anchor=(0.5, -0.25),
              loc='center', fontsize=8, frameon=True, framealpha=0.9)
    
    # Add profile info as subtitle if available
    if profile_footnote:
        plt.figtext(0.5, 0.95, profile_footnote, 
                   ha='center', va='top', fontsize=9, color='#555555')
    # Use utility for output directory
    ticker_dir = get_output_ticker_dir(ticker)
    out_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.png")
    plt.savefig(out_path)
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")
    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, 'ps1') or sys.flags.interactive:
        plt.show()
