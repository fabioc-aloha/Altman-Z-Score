"""
Z-Score Trend Plotting Utilities

This module provides functions to plot the Altman Z-Score trend with risk zone bands.
"""
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from altman_zscore import models as zscore_models

def plot_zscore_trend(df, ticker, model, out_base, profile_footnote=None):
    """
    Plot the Altman Z-Score trend with colored risk bands and save as PNG.
    Args:
        df: DataFrame with columns ['quarter_end', 'zscore']
        ticker: Stock ticker symbol
        model: Z-Score model name
        out_base: Output file base path (without extension)
    """
    plot_df = df[df["zscore"].notnull()]
    if plot_df.empty:
        print("[WARN] No valid Z-Score data to plot.")
        return
    plt.figure(figsize=(10, 5))
    zscores = plot_df["zscore"].astype(float)
    x = plot_df["quarter_end"]

    # Get thresholds for the model
    if model == "original":
        model_thresholds = zscore_models.ModelThresholds.original()
    elif model == "private":
        model_thresholds = zscore_models.ModelThresholds.private_company()
    elif model in ("public", "em", "service"):
        model_thresholds = zscore_models.ModelThresholds.non_manufacturing()
    else:
        model_thresholds = zscore_models.ModelThresholds.original()

    # Draw colored bands for Z-Score zones (distress=red, grey=yellow, safe=green)
    # Compute correct y-limits before drawing bands
    z_min = min(zscores.min(), float(model_thresholds.distress_zone))
    z_max = max(zscores.max(), float(model_thresholds.safe_zone))
    margin = 0.5 * (z_max - z_min) * 0.1  # 10% margin
    ymin = z_min - margin
    # Add extra padding to the top for the legend
    legend_padding = (z_max - z_min) * 0.18  # 18% of range for legend space
    ymax = z_max + margin + legend_padding
    plt.ylim(ymin, ymax)
    # Draw bands in order: safe (bottom), grey (middle), distress (top)
    plt.axhspan(ymin, float(model_thresholds.distress_zone), color='#ff6666', alpha=0.8, label='Distress Zone', zorder=0)
    plt.axhspan(float(model_thresholds.distress_zone), float(model_thresholds.safe_zone), color='#fff700', alpha=0.6, label='Grey Zone', zorder=0)
    plt.axhspan(float(model_thresholds.safe_zone), ymax, color='#66ff66', alpha=0.5, label='Safe Zone', zorder=0)

    # Add zone names inside the plot area, aligned to the left and vertically centered in each band
    ax = plt.gca()
    zone_x = 0.02 * (len(x) - 1) if len(x) > 1 else 0  # 2% from the left edge
    ax.text(zone_x, (ymin + float(model_thresholds.distress_zone)) / 2, 'Distress', color='#a60000', fontsize=11, ha='left', va='center', alpha=0.7, fontweight='bold', clip_on=True)
    ax.text(zone_x, (float(model_thresholds.distress_zone) + float(model_thresholds.safe_zone)) / 2, 'Grey', color='#b3a100', fontsize=11, ha='left', va='center', alpha=0.7, fontweight='bold', clip_on=True)
    ax.text(zone_x, (float(model_thresholds.safe_zone) + ymax) / 2, 'Safe', color='#007a00', fontsize=11, ha='left', va='center', alpha=0.7, fontweight='bold', clip_on=True)

    # Re-plot Z-Score line above the bands for visibility
    plt.plot(x, zscores, marker='o', label="Z-Score", color='blue', zorder=2)
    # Add value labels to each Z-Score point
    ax = plt.gca()
    for i, (x_val, z_val) in enumerate(zip(x, zscores)):
        try:
            label = f"{z_val:.2f}"
            ax.annotate(label, (i, z_val), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, color='blue')
        except Exception:
            pass

    # Format x-axis dates to show as quarters (e.g., '2024Q1'), horizontal
    ax = plt.gca()
    try:
        x_dates = pd.to_datetime(x)
        x_quarters = [f"{d.year}Q{((d.month-1)//3)+1}" for d in x_dates]
        ax.set_xticks(range(len(x_quarters)))
        ax.set_xticklabels(x_quarters, rotation=0, ha='center')
    except Exception:
        plt.xticks(rotation=0)

    plt.title(f"Altman Z-Score Trend for {ticker}")
    plt.xlabel("Quarter End")
    plt.ylabel("Z-Score")
    plt.grid(True, zorder=1)
    # Prepare threshold values for legend
    safe = float(model_thresholds.safe_zone)
    distress = float(model_thresholds.distress_zone)
    grey = f"{distress} to {safe}"

    # Create custom legend handles for each risk zone
    distress_patch = mpatches.Patch(color='#ff6666', alpha=0.8, label=f"Distress Zone (≤ {distress})")
    grey_patch = mpatches.Patch(color='#fff700', alpha=0.6, label=f"Grey Zone ({grey})")
    safe_patch = mpatches.Patch(color='#66ff66', alpha=0.5, label=f"Safe Zone (≥ {safe})")
    zscore_handle, = plt.plot([], [], color='blue', marker='o', label='Z-Score')
    custom_handles = [distress_patch, grey_patch, safe_patch, zscore_handle]
    custom_labels = [
        f"Distress Zone (≤ {distress})",
        f"Grey Zone ({grey})",
        f"Safe Zone (≥ {safe})",
        "Z-Score"
    ]
    plt.legend(custom_handles, custom_labels, loc='upper left', title='Risk Zones & Z-Score')
    plt.tight_layout()
    # Add footnote if provided
    if profile_footnote:
        plt.figtext(0.5, 0.01, profile_footnote, wrap=True, horizontalalignment='center', fontsize=9, color='gray', alpha=0.85)
    # Ensure output subdirectory for ticker exists
    import os
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    out_path = os.path.join(ticker_dir, os.path.basename(f"{out_base}_trend.png"))
    plt.savefig(out_path)
    print(f"[INFO] Z-Score trend plot saved to {os.path.abspath(out_path)}")
    plt.show()
