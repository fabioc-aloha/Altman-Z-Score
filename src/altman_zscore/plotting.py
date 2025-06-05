"""
Z-Score Trend Plotting Utilities

This module provides functions to plot the Altman Z-Score trend, generate component and full reports, and output results to files. It supports robust error handling, clear legends, and company profile/model context in all outputs.

Key Features:
- Plots Z-Score trend with risk zone bands and value labels
- Generates component and full reports with context, formulas, and diagnostics
- Handles missing/invalid data gracefully
- Compatible with Codespaces and local environments
- All outputs saved to output/<TICKER>/

Functions:
    print_info(msg): Print an info message with cyan color if supported.
    ... (other public plotting/reporting functions documented inline)
"""

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os
import sys
import importlib
import matplotlib

matplotlib.use("Agg")
models = importlib.import_module("altman_zscore.models")
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.plot_helpers import prepare_weekly_price_stats_for_plotting
from altman_zscore.plot_blocks import (
    plot_zscore as _plot_zscore,
    add_legend_and_save as _add_legend_and_save,
    format_axes as _format_axes,
    plot_price_trend as _plot_price_trend,
)
from altman_zscore.plotting_terminal import print_info, print_warning, print_error
from altman_zscore.plotting_helpers import make_zone_bands, add_zone_labels, make_legend_elements, save_plot_with_legend

def get_output_ticker_dir(ticker):
    """Return the absolute output directory for a given ticker, ensuring it exists."""
    return get_output_dir(ticker=ticker)


def get_zscore_thresholds(model):
    """Return distress and safe zone thresholds for the given model name."""
    from altman_zscore.computation.constants import Z_SCORE_THRESHOLDS
    
    # Get thresholds from centralized constants
    thresholds = Z_SCORE_THRESHOLDS.get(model, Z_SCORE_THRESHOLDS["original"])
    
    return {
        "distress_zone": float(thresholds["distress"]),
        "safe_zone": float(thresholds["safe"])
    }


def plot_zscore_trend(df, ticker, model, out_base, stock_prices=None):
    """
    Plot the Altman Z-Score trend with colored risk bands and save as PNG.
    If stock_prices provided, overlays weekly stock price trend on secondary y-axis.

    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
        stock_prices (pd.DataFrame, optional): DataFrame with columns ['quarter_end', 'price'] for overlaying stock prices
    Returns:
        None. Saves PNG to output/ and prints absolute path.
    Notes:
        - Handles missing/invalid data gracefully.
        - Adds value labels and robust legend.
        - Output directory is created if missing.
        - Shows weekly price trend on secondary y-axis when stock_prices provided.
    """
    plot_df = df[df["zscore"].notnull()]
    if plot_df.empty:
        print_warning("No valid Z-Score data to plot.")
        return

    print_info("Generating Z-Score trend plot...")
    plt.figure(figsize=(12, 5.5))  # Increased height from 5.5 to 7.0 to close gap with legend

    # Ensure chronological order by sorting by quarter_end
    plot_df = plot_df.copy()
    plot_df["quarter_end"] = pd.to_datetime(plot_df["quarter_end"])
    plot_df = plot_df.sort_values("quarter_end")
    zscores = plot_df["zscore"].astype(float)

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

    # Draw bands using helper function
    ax = plt.gca()
    make_zone_bands(ax, ymin, ymax, thresholds)

    # Add zone names inside the plot area using helper function
    add_zone_labels(ax, ymin, ymax, thresholds)

    # Create timeline that spans earliest to latest dates
    x_dates = plot_df["quarter_end"]
    # Get min and max dates from Z-Score data
    z_score_min = x_dates.min()
    z_score_max = x_dates.max()

    # Initialize min_date with a 3-month lookback before first Z-Score
    min_date = (z_score_min - pd.DateOffset(months=3)).replace(day=1)

    # Set max_date to one week before current date
    current_date = pd.Timestamp.now()
    max_date = current_date - pd.Timedelta(days=7)
    # If z_score_max is later than max_date (somehow), use z_score_max
    if z_score_max > max_date:
        max_date = z_score_max

    # Always use weekly data for date range calculation (weekly-only support)
    using_weekly = True
    min_date = min_date - pd.Timedelta(days=min_date.weekday())
    date_range = pd.date_range(start=min_date, end=max_date, freq="W-MON")

    # Create position mappings
    date_to_pos = {date: i for i, date in enumerate(date_range)}

    # Use monthly labels for readability on weekly x-axis
    date_labels = []
    current_month = None
    for i, date in enumerate(date_range):
        # Only show label if it's the first week of a month
        if date.month != current_month:
            date_labels.append(date.strftime("%Y-%m"))
            current_month = date.month
        else:
            date_labels.append("")  # Empty label for other weeks

    # Map quarter dates to their positions
    quarter_positions = []
    for quarter_date in x_dates:
        # Find the Monday of the week containing the quarter date
        monday = quarter_date - pd.Timedelta(days=quarter_date.weekday())
        pos = date_to_pos.get(monday, -1)
        quarter_positions.append(pos)

    # Plot Z-scores at their positions
    valid_quarters = [(pos, zscore) for pos, zscore in zip(quarter_positions, zscores) if pos != -1]
    if valid_quarters:
        q_pos, q_scores = zip(*valid_quarters)
        _plot_zscore(ax, q_pos, q_scores)

    # Format x-axis
    _format_axes(ax, date_labels, using_weekly, date_range)

    # Get company name and prep title
    company_name = None
    try:
        import yfinance as yf

        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        company_name = info.get("shortName") or info.get("longName")
    except KeyError:
        company_name = ticker.upper()
    if not company_name:
        company_name = ticker.upper()  # Create title and subtitle
    plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    # Set up weekly price overlay if data is provided
    price_stats = None
    price_label = "Weekly\nAvg Price/Range"

    if stock_prices is not None and not stock_prices.empty:
        price_stats = stock_prices.copy()
        price_stats["period"] = pd.to_datetime(price_stats["week"])
        print(
            "[DEBUG] Weekly price stats range:",
            price_stats["period"].min(),
            "to",
            price_stats["period"].max(),
        )

    # Adjust figure layout for price axis
    plt.gcf().subplots_adjust(right=0.85)  # Make room for price axis
    # plt.xlabel(time_label)  # Will show "Week" or "Month" based on data type
    # Set Z-Score y-axis label and ticks to blue to match the Z-Score line
    ax = plt.gca()
    ax.set_ylabel("Z-Score", color="blue", labelpad=6)  # Reduce padding to prevent label going outside
    ax.tick_params(axis="y", labelcolor="blue")
    plt.grid(True, zorder=1)

    # Prepare threshold values for legend
    safe = float(thresholds["safe_zone"])
    distress = float(thresholds["distress_zone"])

    # Create legend patches using helper function
    legend_elements = make_legend_elements(safe, distress)

    # If price_stats are provided, plot average and range as the stock price line
    if price_stats is not None and not price_stats.empty:
        ax2 = ax.twinx()
        # Use weekly helpers for data prep
        period_positions, avg_prices, min_prices, max_prices = prepare_weekly_price_stats_for_plotting(
            price_stats, date_to_pos, min_date, max_date
        )
        if not (period_positions and avg_prices and min_prices and max_prices):
            # No valid data to plot
            pass
        else:
            price_legend = _plot_price_trend(
                ax2, period_positions, avg_prices, min_prices, max_prices, price_label, using_weekly
            )
            legend_elements.append(price_legend)

    # Add legend extending horizontally in one line
    # Increase left margin for y-axis label, adjust bottom margin and legend position
    save_plot_with_legend(
        plt.gcf(),
        legend_elements,
        os.path.join(get_output_ticker_dir(ticker), f"zscore_{ticker}_trend.png"),
    )

    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()


def plot_zscore_trend_pipeline(df, ticker, model, out_base):
    import os
    import sys
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    fig = plt.figure(figsize=(12, 5.5))  # Increased height from 5.5 to 7.0 to close gap with legend
    plt.subplots_adjust(right=0.85)
    ax = plt.gca()
    plot_df = df[df["zscore"].notnull()].copy()
    if plot_df.empty:
        print_warning("No valid Z-Score data to plot.")
        return
    plot_df["quarter_end"] = pd.to_datetime(plot_df["quarter_end"])
    plot_df = plot_df.sort_values("quarter_end")
    zscores = plot_df["zscore"].astype(float)
    x_dates = plot_df["quarter_end"]
    thresholds = get_zscore_thresholds(model)
    z_min = min(zscores.min(), float(thresholds["distress_zone"]))
    z_max = max(zscores.max(), float(thresholds["safe_zone"]))
    margin = 0.5 * (z_max - z_min) * 0.15
    ymin = z_min - margin
    legend_padding = (z_max - z_min) * 0.18
    ymax = z_max + margin + legend_padding
    ax.set_ylim(ymin, ymax)
    make_zone_bands(ax, ymin, ymax, thresholds)
    add_zone_labels(ax, ymin, ymax, thresholds)
    # ...existing code for date range, date_to_pos, date_labels, quarter_positions, plotting, formatting, title...
    safe = float(thresholds["safe_zone"])
    distress = float(thresholds["distress_zone"])
    legend_elements = make_legend_elements(safe, distress)
    # ...existing code for price_stats and price_legend...
    out_path = os.path.join(get_output_ticker_dir(ticker), f"zscore_{ticker}_trend.png")
    save_plot_with_legend(fig, legend_elements, out_path)
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")
    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()
