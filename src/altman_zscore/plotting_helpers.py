"""
Plotting and matplotlib axis/legend helpers for Z-Score trend plots.
"""
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

def make_zone_bands(ax, ymin, ymax, thresholds):
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

def add_zone_labels(ax, ymin, ymax, thresholds):
    distress_y = ymin + (float(thresholds["distress_zone"]) - ymin) * 0.5
    grey_y = float(thresholds["distress_zone"]) + (float(thresholds["safe_zone"]) - float(thresholds["distress_zone"])) * 0.5
    safe_y = float(thresholds["safe_zone"]) + (ymax - float(thresholds["safe_zone"])) * 0.3
    ax.text(
        0.02,
        (distress_y - ymin) / (ymax - ymin),
        "Distress",
        transform=ax.transAxes,
        color="#a60000",
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
        color="#444444",
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
        color="#007a00",
        fontsize=9,
        ha="left",
        va="center",
        fontweight="bold",
        zorder=1000,
    )

def make_legend_elements(safe, distress):
    return [
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

def save_plot_with_legend(fig, legend_elements, out_path):
    fig.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=len(legend_elements))
    fig.savefig(out_path, bbox_inches="tight")
