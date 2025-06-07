"""
Plotting helpers for Altman Z-Score trend visualizations.

This module provides utility functions for zone band drawing, legend creation, date alignment, and price statistics preparation.
All helpers are designed for modular use in the main plotting pipeline and are imported by plotting_main.py and blocks.py.
"""

import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import pandas as pd
from .colors import ColorScheme

def make_zone_bands(ax, ymin, ymax, thresholds):
    """
    Draw colored horizontal bands for distress, grey, and safe zones on the Z-Score plot.
    Args:
        ax: Matplotlib axis object.
        ymin: Minimum y-axis value.
        ymax: Maximum y-axis value.
        thresholds: Dict with 'distress_zone' and 'safe_zone' keys.
    """
    ax.axhspan(
        ymin,
        float(thresholds["distress_zone"]),
        color=ColorScheme.DISTRESS_ZONE,
        alpha=ColorScheme.DISTRESS_ALPHA,
        label="Distress Zone",
        zorder=0,
    )
    ax.axhspan(
        float(thresholds["distress_zone"]),
        float(thresholds["safe_zone"]),
        color=ColorScheme.GREY_ZONE,
        alpha=ColorScheme.GREY_ALPHA,
        label="Grey Zone",
        zorder=0,
    )
    ax.axhspan(
        float(thresholds["safe_zone"]),
        ymax,
        color=ColorScheme.SAFE_ZONE,
        alpha=ColorScheme.SAFE_ALPHA,
        label="Safe Zone",
        zorder=0,
    )

def add_zone_labels(ax, ymin, ymax, thresholds):
    """
    Add text labels ('Distress', 'Grey', 'Safe') to the corresponding risk zones on the plot.
    Args:
        ax: Matplotlib axis object.
        ymin: Minimum y-axis value.
        ymax: Maximum y-axis value.
        thresholds: Dict with 'distress_zone' and 'safe_zone' keys.
    """
    distress_y = ymin + (float(thresholds["distress_zone"]) - ymin) * 0.5
    grey_y = float(thresholds["distress_zone"]) + (float(thresholds["safe_zone"]) - float(thresholds["distress_zone"])) * 0.5
    safe_y = float(thresholds["safe_zone"]) + (ymax - float(thresholds["safe_zone"])) * 0.3

    ax.text(
        0.02,
        (distress_y - ymin) / (ymax - ymin),
        "Distress",
        transform=ax.transAxes,
        color=ColorScheme.DISTRESS_LABEL,
        fontsize=9,
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
        color=ColorScheme.GREY_LABEL,
        fontsize=9,
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
        color=ColorScheme.SAFE_LABEL,
        fontsize=9,
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

def make_legend_elements(safe, distress):
    """
    Create legend elements (patches and line) for the Z-Score trend plot legend.
    Args:
        safe: Safe zone threshold value.
        distress: Distress zone threshold value.
    Returns:
        List of matplotlib legend handles.
    """
    return [
        mpatches.Patch(
            facecolor=ColorScheme.DISTRESS_ZONE,
            alpha=ColorScheme.DISTRESS_ALPHA,
            label=f"Distress Zone\n≤ {distress}"
        ),
        mpatches.Patch(
            facecolor=ColorScheme.GREY_ZONE,
            alpha=ColorScheme.GREY_ALPHA,
            label=f"Grey Zone\n{distress} to {safe}"
        ),
        mpatches.Patch(
            facecolor=ColorScheme.SAFE_ZONE,
            alpha=ColorScheme.SAFE_ALPHA,
            label=f"Safe Zone\n≥ {safe}"
        ),
        Line2D(
            [0],
            [0],
            color=ColorScheme.ZSCORE_LINE,
            marker="s",
            label="Z-Score\nTrend Line",
            markersize=4,
            linestyle="-",
            linewidth=1,
        ),
    ]

def align_dates_to_grid(date_series, freq="W"):
    """
    Align a pandas Series of dates to a regular grid (weekly or monthly).
    Args:
        date_series: Pandas Series of datetime-like values.
        freq: 'W' for weekly, 'M' for monthly.
    Returns:
        Pandas Series of aligned dates.
    """
    dates = pd.to_datetime(date_series)
    if freq == "W":
        return dates - pd.Timedelta(days=dates.dt.weekday)
    elif freq == "M":
        return dates.dt.to_period("M").dt.to_timestamp()
    return dates

def prepare_price_stats_for_plotting(price_stats, using_weekly, date_to_pos, min_date, max_date):
    """
    Prepare and filter price statistics for plotting overlays on the Z-Score trend plot.
    Args:
        price_stats: DataFrame with price statistics (must include 'week' or 'month' columns).
        using_weekly: Boolean, True if using weekly data.
        date_to_pos: Dict mapping dates to x-axis positions.
        min_date: Minimum date to include.
        max_date: Maximum date to include.
    Returns:
        Tuple of (period_positions, avg_prices, min_prices, max_prices) or (None, ...)
    """
    if price_stats is None or price_stats.empty:
        return None, None, None, None
    
    price_stats = price_stats.copy()
    if using_weekly:
        price_stats["period"] = align_dates_to_grid(price_stats["week"], "W")
    else:
        price_stats["period"] = align_dates_to_grid(price_stats["month"], "M")
        
    mask = (price_stats["period"] >= min_date) & (price_stats["period"] <= max_date)
    price_stats = price_stats[mask].copy()

    period_positions = []
    for period in price_stats["period"]:
        pos = date_to_pos.get(period, -1)
        period_positions.append(pos)

    valid_indices = [i for i, pos in enumerate(period_positions) if pos != -1]
    if not valid_indices:
        return None, None, None, None

    period_positions = [period_positions[i] for i in valid_indices]
    avg_prices = [float(price_stats.iloc[i]["avg_price"]) for i in valid_indices]
    min_prices = [float(price_stats.iloc[i]["min_price"]) for i in valid_indices]
    max_prices = [float(price_stats.iloc[i]["max_price"]) for i in valid_indices]

    data = list(zip(period_positions, avg_prices, min_prices, max_prices))
    data.sort(key=lambda x: x[0])
    period_positions, avg_prices, min_prices, max_prices = zip(*data)
    
    return list(period_positions), list(avg_prices), list(min_prices), list(max_prices)

def save_plot_with_legend(fig, legend_elements, out_path):
    """
    Save the plot to disk with the legend positioned below the plot area.
    Args:
        fig: Matplotlib figure object.
        legend_elements: List of legend handles.
        out_path: Output file path.
    """
    fig.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=len(legend_elements)
    )
    fig.savefig(out_path, bbox_inches="tight")
