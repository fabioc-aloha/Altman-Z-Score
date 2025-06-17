"""
Main plotting orchestration for Altman Z-Score trend and report visualizations.

This module provides high-level functions to plot the Altman Z-Score trend, generate component and full reports, and output results to files. It coordinates the use of modular plotting helpers and block functions, and ensures robust error handling and clear legends in all outputs.

Key Features:
- Plots Z-Score trend with risk zone bands and value labels
- Generates component and full reports with context, formulas, and diagnostics
- Handles missing/invalid data gracefully
- Compatible with Codespaces and local environments
- All outputs saved to output/<TICKER>/
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
import importlib
import matplotlib

matplotlib.use("Agg")
models = importlib.import_module("altman_zscore.models")
from altman_zscore.utils.paths import get_output_dir
from .plot_helpers import prepare_weekly_price_stats_for_plotting
from .plot_blocks import (
    plot_zscore as _plot_zscore,
    format_axes as _format_axes,
    plot_price_trend as _plot_price_trend,
)
from .plotting_terminal import print_info, print_warning
from .plotting_helpers import make_zone_bands, add_zone_labels, make_legend_elements, save_plot_with_legend

def get_output_ticker_dir(ticker):
    """
    Return the absolute output directory for a given ticker, ensuring it exists.
    Args:
        ticker: Stock ticker symbol.
    Returns:
        Absolute path to the output directory for the ticker.
    """
    return get_output_dir(ticker=ticker)


def get_zscore_thresholds(model):
    """
    Return distress and safe zone thresholds for the given model name.
    Args:
        model: Z-Score model name.
    Returns:
        Dict with 'distress_zone' and 'safe_zone' keys as floats.
    """
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

    # Get min and max dates from both Z-Score data and stock prices if available
    x_dates = plot_df["quarter_end"]
    z_score_min = x_dates.min()
    z_score_max = x_dates.max()

    # If we have stock prices, also consider their date range
    if stock_prices is not None and not stock_prices.empty:
        price_dates = pd.to_datetime(stock_prices["week"])
        min_date = min(z_score_min, price_dates.min())
        max_date = max(z_score_max, price_dates.max())
    else:
        min_date = z_score_min
        max_date = z_score_max

    # Always use weekly data for date range calculation
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
        company_name = ticker.upper()
    plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")

    # Set up weekly price overlay if data is provided
    price_stats = None
    price_label = "Weekly\nPrice Range"

    if stock_prices is not None and not stock_prices.empty:
        price_stats = stock_prices.copy()
        price_stats["period"] = pd.to_datetime(price_stats["week"])

    # Adjust figure layout for price axis
    plt.gcf().subplots_adjust(right=0.85)  # Make room for price axis
    # Set Z-Score y-axis label and ticks to blue to match the Z-Score line
    ax = plt.gca()
    ax.set_ylabel("Z-Score", color="blue", labelpad=6)
    ax.tick_params(axis="y", labelcolor="blue")
    plt.grid(True, zorder=1)

    # Prepare threshold values for legend
    safe = float(thresholds["safe_zone"])
    distress = float(thresholds["distress_zone"])

    # Create legend patches using helper function
    legend_elements = make_legend_elements(safe, distress)

    handler_map = None
    if price_stats is not None and not price_stats.empty:
        ax2 = ax.twinx()
        # Use weekly helpers for data prep
        period_positions, open_prices, high_prices, low_prices, close_prices = prepare_weekly_price_stats_for_plotting(
            price_stats, date_to_pos, min_date, max_date
        )
        if not (period_positions and open_prices and high_prices and low_prices and close_prices):
            # No valid data to plot
            pass
        else:
            price_legend = _plot_price_trend(
                ax2,
                period_positions,
                open_prices,
                high_prices,
                low_prices,
                close_prices,
                price_label,
                using_weekly,
            )
            # Wrap the candlestick tuple and its label for the legend
            legend_elements.append((price_legend, price_label))
            # If price_legend is a tuple, set handler_map for HandlerTuple
            if isinstance(price_legend, tuple):
                from matplotlib.legend_handler import HandlerTuple
                handler_map = {tuple: HandlerTuple(ndivide=None)}

    # Add company logo if available
    logo_path = os.path.join(get_output_ticker_dir(ticker), f"{ticker}_logo.png")
    from .plotting_helpers import add_company_logo
    add_company_logo(plt.gcf(), logo_path, position=(0.075, 0.02), zoom=0.2)

    # Add legend extending horizontally in one line
    save_plot_with_legend(
        plt.gcf(),
        legend_elements,
        os.path.join(get_output_ticker_dir(ticker), f"zscore_{ticker}_trend.png"),
        handler_map=handler_map
    )

    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()


def plot_zscore_trend_pipeline(df, ticker, model, out_base):
    """
    Plot the Altman Z-Score trend for use in pipeline workflows (legacy compatibility).
    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
    Returns:
        None. Saves PNG to output/ and prints absolute path.
    """
    import os
    import sys
    import matplotlib.pyplot as plt
    
    # Set stock_prices to None for pipeline version (no price overlay)
    stock_prices = None
    
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
    plot_df["quarter_end"]
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
    # Get min and max dates from both Z-Score data and stock prices if available
    x_dates = plot_df["quarter_end"]
    z_score_min = x_dates.min()
    z_score_max = x_dates.max()

    # If we have stock prices, also consider their date range
    if stock_prices is not None and not stock_prices.empty:
        price_dates = pd.to_datetime(stock_prices["week"])
        min_date = min(z_score_min, price_dates.min())
        max_date = max(z_score_max, price_dates.max())
    else:
        min_date = z_score_min
        max_date = z_score_max

    # Always use weekly data for date range calculation
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
        company_name = ticker.upper()
    plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    # Set up weekly price overlay if data is provided
    price_stats = None
    price_label = "Weekly\nPrice Range"

    if stock_prices is not None and not stock_prices.empty:
        price_stats = stock_prices.copy()
        price_stats["period"] = pd.to_datetime(price_stats["week"])
    # Adjust figure layout for price axis
    plt.gcf().subplots_adjust(right=0.85)  # Make room for price axis
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

    handler_map = None
    if price_stats is not None and not price_stats.empty:
        ax2 = ax.twinx()
        # Use weekly helpers for data prep
        period_positions, open_prices, high_prices, low_prices, close_prices = prepare_weekly_price_stats_for_plotting(
            price_stats, date_to_pos, min_date, max_date
        )
        if not (period_positions and open_prices and high_prices and low_prices and close_prices):
            # No valid data to plot
            pass
        else:
            price_legend = _plot_price_trend(
                ax2,
                period_positions,
                open_prices,
                high_prices,
                low_prices,
                close_prices,
                price_label,
                using_weekly,
            )
            # Wrap the candlestick tuple and its label for the legend
            legend_elements.append((price_legend, price_label))
            # If price_legend is a tuple, set handler_map for HandlerTuple
            if isinstance(price_legend, tuple):
                from matplotlib.legend_handler import HandlerTuple
                handler_map = {tuple: HandlerTuple(ndivide=None)}

    # Add company logo if available
    logo_path = os.path.join(get_output_ticker_dir(ticker), f"{ticker}_logo.png")
    from .plotting_helpers import add_company_logo
    add_company_logo(plt.gcf(), logo_path, position=(0.075, 0.02), zoom=0.2)

    # Add legend extending horizontally in one line
    # Increase left margin for y-axis label, adjust bottom margin and legend position
    save_plot_with_legend(
        plt.gcf(),
        legend_elements,
        os.path.join(get_output_ticker_dir(ticker), f"zscore_{ticker}_trend.png"),
        handler_map=handler_map
    )

    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()
