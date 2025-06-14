"""
Plotting block functions for Altman Z-Score and price trend visualizations.

This module provides modular plotting utilities for use by the main plotting orchestration functions. Functions here are called by plotting_main.py and are designed for composability and testability.
"""

import numpy as np
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline


def plot_zscore(ax, q_pos, q_scores):
    """
    Plot Z-Score values as a line and annotate each point with its value.
    Args:
        ax: Matplotlib axis object.
        q_pos: List or array of x-axis positions for each quarter.
        q_scores: List or array of Z-Score values.
    """
    try:
        # Convert positions and scores to float arrays, handling pandas Series
        positions = [float(pos) for pos in (q_pos.values if hasattr(q_pos, "values") else q_pos)]
        scores = [float(score) for score in (q_scores.values if hasattr(q_scores, "values") else q_scores)]

        # Validate data
        if not positions or not scores or len(positions) != len(scores):
            print("[WARN] Invalid Z-Score data for plotting")
            return

        # Plot Z-Score points
        ax.plot(positions, scores, marker="s", label="Z-Score", color="blue", zorder=2)

        # Add value labels
        for pos, z_val in zip(positions, scores):
            label = f"{z_val:.2f}"
            ax.annotate(
                text=label,
                xy=(pos, z_val),
                textcoords="offset points",
                xytext=(0, 12),
                ha="center",
                fontsize=9,
                color="blue",
            )

    except ValueError as exc:
        print(f"[WARN] Error plotting Z-Score: {exc}")


def plot_price_trend(
    ax2,
    period_positions,
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    price_label,
    using_weekly,
):
    """Plot weekly candlestick chart."""
    # Convert inputs to lists if they are pandas Series
    period_positions = list(period_positions) if hasattr(period_positions, "tolist") else period_positions
    open_prices = list(open_prices) if hasattr(open_prices, "tolist") else open_prices
    high_prices = list(high_prices) if hasattr(high_prices, "tolist") else high_prices
    low_prices = list(low_prices) if hasattr(low_prices, "tolist") else low_prices
    close_prices = list(close_prices) if hasattr(close_prices, "tolist") else close_prices

    # Verify we have valid data to plot
    if (
        not all([period_positions, open_prices, high_prices, low_prices, close_prices])
        or len(period_positions) != len(open_prices)
        or len(period_positions) != len(high_prices)
        or len(period_positions) != len(low_prices)
        or len(period_positions) != len(close_prices)
    ):
        print("[WARN] Insufficient price data for plotting")
        return Line2D(
            [0],
            [0],
            color="#444444",
            marker="o",
            label=price_label,
            markersize=4,
            linestyle="-",
            linewidth=2,
        )

    dark_gray = "#444444"
    candlestick_width = 0.6
    up_color = "#007a00"
    down_color = "#a60000"

    try:
        for x, o, h, l, c in zip(period_positions, open_prices, high_prices, low_prices, close_prices):
            color = up_color if c >= o else down_color
            ax2.vlines(x, l, h, color=color, linewidth=1, zorder=1)
            rect = mpatches.Rectangle(
                (x - candlestick_width / 2, min(o, c)),
                candlestick_width,
                max(abs(c - o), 0.01),
                facecolor=color,
                edgecolor=color,
                linewidth=1,
                zorder=2,
            )
            ax2.add_patch(rect)

        ax2.set_ylabel("Stock Price ($)", color=dark_gray, labelpad=15)
        ax2.tick_params(axis="y", labelcolor=dark_gray, pad=8)

        y_min = min(low_prices)
        y_max = max(high_prices)
        price_range = y_max - y_min
        price_margin = price_range * 0.25
        ax2.set_ylim(bottom=max(0, y_min - price_margin * 0.5), top=y_max + price_margin)

    except ValueError as e:
        print(f"[WARN] Error plotting price trend: {e}")
        return Line2D(
            [0],
            [0],
            color=dark_gray,
            marker="o",
            label=price_label,
            markersize=4,
            linestyle="-",
            linewidth=2,
        )

    return Line2D(
        [0],
        [0],
        color=dark_gray,
        marker="o",
        label=price_label,
        markersize=4,
        linestyle="-",
        linewidth=2,
    )


def format_axes(ax, date_labels, using_weekly, date_range):
    """
    Format the x-axis and y-axis labels, ticks, and grid for the Z-Score plot.
    Args:
        ax: Matplotlib axis object.
        date_labels: List of x-axis labels (usually months).
        using_weekly: Boolean, True if using weekly data.
        date_range: List of datetime objects for the x-axis.
    """
    if using_weekly:
        tick_positions = [i for i, label in enumerate(date_labels) if label]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([date_labels[i] for i in tick_positions], rotation=45, ha="right", fontsize=7)
    else:
        ax.set_xticks(list(range(len(date_range))))
        ax.set_xticklabels(date_labels, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("Z-Score", color="blue", labelpad=6)
    ax.tick_params(axis="y", labelcolor="blue")
    ax.grid(True, zorder=1)


def add_legend_and_save(fig, legend_elements, out_path):
    """
    Add a legend to the plot and save the figure to disk.
    Args:
        fig: Matplotlib figure object.
        legend_elements: List of legend handles.
        out_path: Output file path.
    """
    # Increase bottom margin significantly to prevent overlap with x-axis labels
    # Extra space needed for rotated weekly date labels
    fig.subplots_adjust(left=0.10, bottom=0.35)
    num_cols = len(legend_elements)

    # Position legend higher to ensure clear separation from x-axis labels
    # Move legend up to 22% to provide more space above rotated x-axis labels
    fig.legend(
        handles=legend_elements,
        ncol=num_cols,
        bbox_to_anchor=(0.5, 0.22),
        loc="center",
        fontsize=7,
        frameon=True,
        framealpha=0.9,
    )

    fig.savefig(out_path, bbox_inches="tight", dpi=300)
