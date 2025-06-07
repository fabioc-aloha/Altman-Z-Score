"""
Plotting block functions for Altman Z-Score and price trend visualizations.

This module provides modular plotting utilities for use by the main plotting orchestration functions.
Functions here are called by plotting_main.py and are designed for composability and testability.
"""
import numpy as np
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline
from .colors import ColorScheme

def plot_zscore(ax, q_pos, q_scores):
    """
    Plot Z-Score values as a line and annotate each point with its value.
    Args:
        ax: Matplotlib axis object.
        q_pos: List or array of x-axis positions for each quarter.
        q_scores: List or array of Z-Score values.
    """
    try:
        # Plot Z-score line and points
        ax.plot(
            q_pos,
            q_scores,
            color=ColorScheme.ZSCORE_LINE,
            marker="s",
            markersize=4,
            linestyle="-",
            linewidth=1,
            label="Z-Score",
            zorder=3,
        )

        for pos, score in zip(q_pos, q_scores):
            ax.annotate(
                f"{score:.2f}",
                xy=(pos, score),
                xytext=(0, -20 if score > np.mean(q_scores) else 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color=ColorScheme.ZSCORE_LINE,
            )
    except ValueError as exc:
        print(f"[WARN] Error plotting Z-Score: {exc}")

def plot_price_trend(ax2, period_positions, avg_prices, min_prices, max_prices, price_label, using_weekly):
    """
    Plot the stock price trend as a line with error bars and annotate key points.
    Args:
        ax2: Matplotlib secondary axis object.
        period_positions: List of x-axis positions for each period.
        avg_prices: List of average prices per period.
        min_prices: List of minimum prices per period.
        max_prices: List of maximum prices per period.
        price_label: Label for the price trend line.
        using_weekly: Boolean, True if using weekly data.
    Returns:
        Matplotlib Line2D object for legend.
    """
    period_positions = list(period_positions) if hasattr(period_positions, "tolist") else period_positions
    avg_prices = list(avg_prices) if hasattr(avg_prices, "tolist") else avg_prices
    min_prices = list(min_prices) if hasattr(min_prices, "tolist") else min_prices
    max_prices = list(max_prices) if hasattr(max_prices, "tolist") else max_prices

    if not all([period_positions, avg_prices, min_prices, max_prices]) or not all(
        len(period_positions) == len(x) for x in [avg_prices, min_prices, max_prices]
    ):
        print("[WARN] Insufficient price data for plotting")
        return Line2D(
            [0],
            [0],
            color=ColorScheme.DARK_GREY,
            marker="o",
            label=price_label,
            markersize=4,
            linestyle="-",
            linewidth=2,
        )

    marker_size = 3 if using_weekly else 5
    try:
        valid_data = []
        for pos, avg, min_p, max_p in zip(period_positions, avg_prices, min_prices, max_prices):
            try:
                pos_val = float(pos.item() if hasattr(pos, "item") else pos)
                avg_val = float(avg.item() if hasattr(avg, "item") else avg)
                min_val = float(min_p.item() if hasattr(min_p, "item") else min_p)
                max_val = float(max_p.item() if hasattr(max_p, "item") else max_p)
                if not any(np.isnan([pos_val, avg_val, min_val, max_val])):
                    valid_data.append((pos_val, avg_val, min_val, max_val))
            except (TypeError, ValueError) as e:
                print(f"[DEBUG] Skipping invalid data point: {e}")

        if not valid_data:
            print("[WARN] No valid price data points after filtering")
            return Line2D(
                [0],
                [0],
                color=ColorScheme.DARK_GREY,
                marker="o",
                label=price_label,
                markersize=4,
                linestyle="-",
                linewidth=2,
            )

        period_positions, avg_prices, min_prices, max_prices = zip(*valid_data)

        try:
            if len(period_positions) >= 4:
                x_smooth = np.linspace(min(period_positions), max(period_positions), 300)
                spl = make_interp_spline(period_positions, avg_prices, k=min(3, len(period_positions) - 1))
                y_smooth = spl(x_smooth)
                ax2.plot(
                    x_smooth,
                    y_smooth,
                    color=ColorScheme.DARK_GREY,
                    linestyle="-",
                    linewidth=1,
                    label="_nolegend_",
                    zorder=2,
                )
            ax2.scatter(
                period_positions,
                avg_prices,
                marker="o",
                color=ColorScheme.DARK_GREY,
                s=marker_size**2,
                label=price_label,
                zorder=4,
            )
        except Exception as e:
            print(f"[WARN] Falling back to simple line plot: {e}")
            ax2.plot(
                period_positions,
                avg_prices,
                marker="o",
                color=ColorScheme.DARK_GREY,
                linestyle="-",
                linewidth=1,
                markersize=marker_size,
                label=price_label,
                zorder=3,
            )

        # Plot price ranges with I-beam whiskers
        whisker_width = 0.2
        for pos, min_p, max_p in zip(period_positions, min_prices, max_prices):
            ax2.vlines(pos, min_p, max_p, color=ColorScheme.DARK_GREY, alpha=0.6, linewidth=1, zorder=1)
            ax2.hlines(
                min_p,
                pos - whisker_width / 2,
                pos + whisker_width / 2,
                color=ColorScheme.DARK_GREY,
                alpha=0.6,
                linewidth=1,
                zorder=1,
            )
            ax2.hlines(
                max_p,
                pos - whisker_width / 2,
                pos + whisker_width / 2,
                color=ColorScheme.DARK_GREY,
                alpha=0.6,
                linewidth=1,
                zorder=1,
            )

        # Add price labels
        if using_weekly:
            key_indices = {
                0,  # First point
                len(avg_prices) - 1,  # Last point
                max(range(len(avg_prices)), key=lambda i: avg_prices[i]),  # Max value
                min(range(len(avg_prices)), key=lambda i: avg_prices[i]),  # Min value
            }
            for idx in key_indices:
                pos = period_positions[idx]
                avg = avg_prices[idx]
                label = f"${avg:.2f}"
                y_offset = 12 if idx in {0, len(avg_prices) - 1} else -18
                ax2.annotate(
                    text=label,
                    xy=(pos, avg),
                    textcoords="offset points",
                    xytext=(0, y_offset),
                    ha="center",
                    fontsize=8,
                    color=ColorScheme.DARK_GREY,
                    alpha=0.9,
                )
        else:
            # For monthly data, label all points
            for pos, avg in zip(period_positions, avg_prices):
                label = f"${avg:.2f}"
                ax2.annotate(
                    text=label,
                    xy=(pos, avg),
                    textcoords="offset points",
                    xytext=(0, 12),
                    ha="center",
                    fontsize=8,
                    color=ColorScheme.DARK_GREY,
                    alpha=0.9,
                )

        # Configure the y-axis
        ax2.set_ylabel("Stock Price ($)", color=ColorScheme.DARK_GREY, labelpad=15)
        ax2.tick_params(axis="y", labelcolor=ColorScheme.DARK_GREY, pad=8)

        # Set the y-axis limits with margin
        y_min, y_max = min(min_prices), max(max_prices)
        price_range = y_max - y_min
        price_margin = price_range * 0.25
        ax2.set_ylim(bottom=max(0, y_min - price_margin * 0.5), top=y_max + price_margin)

    except ValueError as e:
        print(f"[WARN] Error plotting price trend: {e}")
        return Line2D(
            [0],
            [0],
            color=ColorScheme.DARK_GREY,
            marker="o",
            label=price_label,
            markersize=4,
            linestyle="-",
            linewidth=2,
        )

    return Line2D(
        [0],
        [0],
        color=ColorScheme.DARK_GREY,
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
    ax.set_ylabel("Z-Score", color=ColorScheme.ZSCORE_LINE, labelpad=6)
    ax.tick_params(axis="y", labelcolor=ColorScheme.ZSCORE_LINE)
    ax.grid(True, zorder=1)

def add_legend_and_save(fig, legend_elements, out_path):
    """
    Add a legend to the plot and save the figure to disk.
    Args:
        fig: Matplotlib figure object.
        legend_elements: List of legend handles.
        out_path: Output file path.
    """
    # Increase bottom margin for rotated labels
    fig.subplots_adjust(left=0.10, bottom=0.35)
    num_cols = len(legend_elements)

    # Position legend above rotated x-axis labels
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
