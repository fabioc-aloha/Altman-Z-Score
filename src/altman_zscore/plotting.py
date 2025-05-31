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

# ANSI color codes for terminal output if supported
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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


def plot_zscore_trend(df, ticker, model, out_base, stock_prices=None, show_moving_averages=False):
    """
    Plot the Altman Z-Score trend with colored risk bands and save as PNG.
    If stock_prices provided, overlays weekly stock price trend on secondary y-axis.

    Args:
        df (pd.DataFrame): DataFrame with columns ['quarter_end', 'zscore']
        ticker (str): Stock ticker symbol
        model (str): Z-Score model name
        out_base (str): Output file base path (without extension)
        stock_prices (pd.DataFrame, optional): DataFrame with columns ['quarter_end', 'price'] for overlaying stock prices
        show_moving_averages (bool, optional): Whether to show moving averages for Z-Score and price trends. Default: False
    Returns:
        None. Saves PNG to output/ and prints absolute path.
    Notes:
        - Handles missing/invalid data gracefully.
        - Adds value labels and robust legend.        - Output directory is created if missing.
        - Shows weekly price trend on secondary y-axis when stock_prices provided.
        - Moving averages: 3-period for Z-Score, 5-period for price data.
    """
    plot_df = df[df["zscore"].notnull()]
    if plot_df.empty:
        print_warning("No valid Z-Score data to plot.")
        return

    print_info("Generating Z-Score trend plot...")
    plt.figure(figsize=(10, 5.5))  # Increased figure height slightly

    # Ensure chronological order by sorting by quarter_end
    plot_df = plot_df.copy()
    plot_df["quarter_end"] = pd.to_datetime(plot_df["quarter_end"])
    plot_df = plot_df.sort_values("quarter_end")
    zscores = plot_df["zscore"].astype(float)
    plot_df["quarter_end"]

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
    plt.axhspan(
        ymin,
        float(thresholds["distress_zone"]),
        color="#ff6666",
        alpha=0.8,
        label="Distress Zone",
        zorder=0,
    )
    plt.axhspan(
        float(thresholds["distress_zone"]),
        float(thresholds["safe_zone"]),
        color="#cccccc",
        alpha=0.6,
        label="Grey Zone",
        zorder=0,
    )
    plt.axhspan(
        float(thresholds["safe_zone"]),
        ymax,
        color="#66ff66",
        alpha=0.5,
        label="Safe Zone",
        zorder=0,
    )

    # Add zone names inside the plot area
    ax = plt.gca()

    # Calculate y positions within each zone
    distress_y = ymin + (float(thresholds["distress_zone"]) - ymin) * 0.5
    grey_y = (
        float(thresholds["distress_zone"]) + (float(thresholds["safe_zone"]) - float(thresholds["distress_zone"])) * 0.5
    )
    safe_y = float(thresholds["safe_zone"]) + (ymax - float(thresholds["safe_zone"])) * 0.3
    # Add the zone labels at the start of the x-axis
    # Use transform to place labels in axes coordinates (0 = left, 1 = right)
    ax.text(
        0.02,
        (distress_y - ymin) / (ymax - ymin),
        "Distress",
        transform=ax.transAxes,
        color="#a60000",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

    ax.text(
        0.02,
        (grey_y - ymin) / (ymax - ymin),
        "Grey",
        transform=ax.transAxes,
        color="#444444",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

    ax.text(
        0.02,
        (safe_y - ymin) / (ymax - ymin),
        "Safe",
        transform=ax.transAxes,
        color="#007a00",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

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
        _plot_zscore(ax, q_pos, q_scores, show_moving_averages)

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

    # Create legend patches
    legend_elements = [
        mpatches.Patch(facecolor="#ff6666", alpha=0.8, label=f"Distress Zone\n≤ {distress}"),
        mpatches.Patch(facecolor="#cccccc", alpha=0.6, label=f"Grey Zone\n{distress} to {safe}"),
        mpatches.Patch(facecolor="#66ff66", alpha=0.5, label=f"Safe Zone\n≥ {safe}"),
        Line2D(
            [0],
            [0],
            color="blue",
            marker="s",
            label="Z-Score\nTrend Line",
            markersize=4,
            linestyle="-",
            linewidth=1,
        ),
    ]
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
    _add_legend_and_save(
        plt.gcf(),
        legend_elements,
        os.path.join(get_output_ticker_dir(ticker), f"zscore_{ticker}_trend.png"),
    )

    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()


def plot_zscore_trend_pipeline(df, ticker, model, out_base, show_moving_averages=False):
    """
    Orchestrates the Z-Score and weekly price trend plotting pipeline.
    Only processes and saves the data necessary for the plot.
    """
    import os
    import sys

    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    # Configure figure size and layout
    fig = plt.figure(figsize=(10, 5.5))
    plt.subplots_adjust(right=0.85)  # Make room for price axis
    ax = plt.gca()

    # Filter and prep Z-Score data
    plot_df = df[df["zscore"].notnull()].copy()
    if plot_df.empty:
        print("[WARN] No valid Z-Score data to plot.")
        return

    plot_df["quarter_end"] = pd.to_datetime(plot_df["quarter_end"])
    plot_df = plot_df.sort_values("quarter_end")
    zscores = plot_df["zscore"].astype(float)
    x_dates = plot_df["quarter_end"]

    # Get thresholds and y-limits
    thresholds = get_zscore_thresholds(model)
    z_min = min(zscores.min(), float(thresholds["distress_zone"]))
    z_max = max(zscores.max(), float(thresholds["safe_zone"]))
    margin = 0.5 * (z_max - z_min) * 0.15
    ymin = z_min - margin
    legend_padding = (z_max - z_min) * 0.18
    ymax = z_max + margin + legend_padding

    # Date range setup
    z_score_min = x_dates.min()
    z_score_max = x_dates.max()
    min_date = (z_score_min - pd.DateOffset(months=3)).replace(day=1)
    current_date = pd.Timestamp.now()
    max_date = current_date - pd.Timedelta(days=7)
    if z_score_max > max_date:
        max_date = z_score_max
        # Always use weekly approach (monthly functionality removed)
    using_weekly = True
    # Configure date range and positions (weekly only)
    min_date = min_date - pd.Timedelta(days=min_date.weekday())
    date_range = pd.date_range(start=min_date, end=max_date, freq="W-MON")

    date_to_pos = {date: i for i, date in enumerate(date_range)}

    # Format x-axis labels (monthly labels on weekly axis for readability)
    date_labels = []
    current_month = None
    for i, date in enumerate(date_range):
        if date.month != current_month:
            date_labels.append(date.strftime("%Y-%m"))
            current_month = date.month
        else:
            date_labels.append("")
            # Map quarter dates to positions (weekly only)
    quarter_positions = []
    for quarter_date in x_dates:
        monday = quarter_date - pd.Timedelta(days=quarter_date.weekday())
        pos = date_to_pos.get(monday, -1)
        quarter_positions.append(pos)

    # Plot Z-Score data
    valid_quarters = [(pos, zscore) for pos, zscore in zip(quarter_positions, zscores) if pos != -1]
    if not valid_quarters:
        print("[WARN] No valid Z-Score data to plot after mapping.")
        return
    q_pos, q_scores = zip(*valid_quarters)

    # Configure Z-Score axis and plot risk bands
    ax.set_ylim(ymin, ymax)
    ax.axhspan(
        ymin,
        float(thresholds["distress_zone"]),
        color="#ff6666",
        alpha=0.8,
        label="Distress Zone",
        zorder=0,
    )
    ax.axhspan(
        float(thresholds["distress_zone"]),
        float(thresholds["safe_zone"]),
        color="#cccccc",
        alpha=0.6,
        label="Grey Zone",
        zorder=0,
    )
    ax.axhspan(
        float(thresholds["safe_zone"]),
        ymax,
        color="#66ff66",
        alpha=0.5,
        label="Safe Zone",
        zorder=0,
    )

    # Add zone labels
    distress_y = ymin + (float(thresholds["distress_zone"]) - ymin) * 0.5
    grey_y = (
        float(thresholds["distress_zone"]) + (float(thresholds["safe_zone"]) - float(thresholds["distress_zone"])) * 0.5
    )
    safe_y = float(thresholds["safe_zone"]) + (ymax - float(thresholds["safe_zone"])) * 0.3
    ax.text(
        0.02,
        (distress_y - ymin) / (ymax - ymin),
        "Distress",
        transform=ax.transAxes,
        color="#a60000",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )
    ax.text(
        0.02,
        (grey_y - ymin) / (ymax - ymin),
        "Grey",
        transform=ax.transAxes,
        color="#444444",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )
    ax.text(
        0.02,
        (safe_y - ymin) / (ymax - ymin),
        "Safe",
        transform=ax.transAxes,
        color="#007a00",
        fontsize=9,  # Decreased font size
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

    # Plot Z-Score
    _plot_zscore(ax, q_pos, q_scores, show_moving_averages)

    # Format axes
    _format_axes(ax, date_labels, using_weekly, date_range)

    # Set up title
    company_name = ticker.upper()
    try:
        import yfinance as yf

        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        company_name = info.get("shortName") or info.get("longName") or ticker.upper()
    except KeyError:
        pass
    ax.set_title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    # plt.xlabel("Week" if using_weekly else "Month")

    # Set up legend elements
    safe = float(thresholds["safe_zone"])
    distress = float(thresholds["distress_zone"])
    legend_elements = [
        mpatches.Patch(facecolor="#ff6666", alpha=0.8, label=f"Distress Zone\n≤ {distress}"),
        mpatches.Patch(facecolor="#cccccc", alpha=0.6, label=f"Grey Zone\n{distress} to {safe}"),
        mpatches.Patch(facecolor="#66ff66", alpha=0.5, label=f"Safe Zone\n≥ {safe}"),
        Line2D(
            [0],
            [0],
            color="blue",
            marker="s",
            label="Z-Score\nTrend Line",
            markersize=4,
            linestyle="-",
            linewidth=1,
        ),
    ]

    # Handle price overlay (weekly only)
    # Note: stock_prices parameter would need to be passed to this function for price overlay
    # Currently this function doesn't accept stock_prices parameter, so no price overlay will be shown
    price_stats = None
    price_label = "Weekly\nAvg Price/Range"

    # Stock price overlay logic would go here if stock_prices parameter was available
    if price_stats is not None and not price_stats.empty:
        ax2 = ax.twinx()
        print("[DEBUG] Created secondary y-axis")
        # Always use weekly price stats preparation
        period_positions, avg_prices, min_prices, max_prices = prepare_weekly_price_stats_for_plotting(
            price_stats, date_to_pos, min_date, max_date
        )

        if period_positions and avg_prices and min_prices and max_prices:
            legend_elements.append(
                _plot_price_trend(
                    ax2,
                    period_positions,
                    avg_prices,
                    min_prices,
                    max_prices,
                    price_label,
                    using_weekly,
                )
            )
            print("[DEBUG] Added price trend to plot")

    # Save the plot
    ticker_dir = get_output_ticker_dir(ticker)
    out_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.png")
    _add_legend_and_save(fig, legend_elements, out_path)
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")

    if hasattr(sys, "ps1") or sys.flags.interactive:
        plt.show()
