"""
Plotting building block functions for Altman Z-Score and price trend visualizations.

This module contains modular plotting utilities to be used by the main plotting orchestration functions.

Functions:
    plot_zscore(ax, q_pos, q_scores, show_moving_averages): Plot Z-Score values with moving averages.
    ... (other public plotting block functions documented inline)
"""

import numpy as np
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline


def plot_zscore(ax, q_pos, q_scores):
    """Plot Z-Score values."""
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


def plot_price_trend(ax2, period_positions, avg_prices, min_prices, max_prices, price_label, using_weekly):
    """Plot price trend with error bars and labels, handling edge cases gracefully."""
    import numpy as np

    # Convert inputs to lists if they are pandas Series
    period_positions = list(period_positions) if hasattr(period_positions, "tolist") else period_positions
    avg_prices = list(avg_prices) if hasattr(avg_prices, "tolist") else avg_prices
    min_prices = list(min_prices) if hasattr(min_prices, "tolist") else min_prices
    max_prices = list(max_prices) if hasattr(max_prices, "tolist") else max_prices

    # Verify we have valid data to plot
    if (
        not all([period_positions, avg_prices, min_prices, max_prices])
        or len(period_positions) != len(avg_prices)
        or len(period_positions) != len(min_prices)
        or len(period_positions) != len(max_prices)
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
    marker_size = 3 if using_weekly else 5

    try:
        # Handle pandas Series and convert to floats, filtering invalid values
        valid_data = []
        for pos, avg, min_p, max_p in zip(period_positions, avg_prices, min_prices, max_prices):
            try:
                # Extract values from Series if needed
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
                color=dark_gray,
                marker="o",
                label=price_label,
                markersize=4,
                linestyle="-",
                linewidth=2,
            )

        # Unzip the valid data
        period_positions, avg_prices, min_prices, max_prices = zip(*valid_data)

        try:
            if len(period_positions) >= 4:  # Only use spline for enough points
                x_smooth = np.linspace(min(period_positions), max(period_positions), 300)
                spl = make_interp_spline(period_positions, avg_prices, k=min(3, len(period_positions) - 1))
                y_smooth = spl(x_smooth)
                ax2.plot(
                    x_smooth,
                    y_smooth,
                    color=dark_gray,
                    linestyle="-",
                    linewidth=1,
                    label="_nolegend_",
                    zorder=2,
                )
            ax2.scatter(
                period_positions,
                avg_prices,
                marker="o",
                color=dark_gray,
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
                color=dark_gray,
                linestyle="-",
                linewidth=1,
                markersize=marker_size,
                label=price_label,
                zorder=3,
            )

        # Plot price ranges with I-beam whiskers
        whisker_width = 0.2
        for pos, min_p, max_p in zip(period_positions, min_prices, max_prices):
            ax2.vlines(pos, min_p, max_p, color=dark_gray, alpha=0.6, linewidth=1, zorder=1)
            ax2.hlines(
                min_p,
                pos - whisker_width / 2,
                pos + whisker_width / 2,
                color=dark_gray,
                alpha=0.6,
                linewidth=1,
                zorder=1,
            )
            ax2.hlines(
                max_p,
                pos - whisker_width / 2,
                pos + whisker_width / 2,
                color=dark_gray,
                alpha=0.6,
                linewidth=1,
                zorder=1,
            )

        # Add price labels
        if using_weekly:
            # For weekly data, only label key points
            max(avg_prices)
            min(avg_prices)
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
                    color=dark_gray,
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
                    color=dark_gray,
                    alpha=0.9,
                )

        # Configure the y-axis
        ax2.set_ylabel("Stock Price ($)", color=dark_gray, labelpad=15)
        ax2.tick_params(axis="y", labelcolor=dark_gray, pad=8)

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
