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

def report_zscore_components_table(df, model, out_base=None, print_to_console=True):
    """
    Generate and print/save a table showing Z-Score components (X1..X5 or X1..X4) and z-score by quarter.

    Args:
        df (pd.DataFrame): DataFrame with columns: quarter_end, zscore, components (dict), etc.
        model (str): Z-Score model name (determines which X components to show)
        out_base (str, optional): Output file base path (without extension)
        print_to_console (bool): Whether to print the table to the console
    Returns:
        None. Prints and/or saves the table as a text file.
    """
    # Determine which X components are present for the model
    model = str(model).lower()
    if model in ("original", "private"):
        x_cols = ["X1", "X2", "X3", "X4", "X5"]
    else:
        x_cols = ["X1", "X2", "X3", "X4"]
    # Build table rows
    rows = []
    for _, row in df.iterrows():
        q = row.get("quarter_end")
        # Format quarter as 'YYYY Qn' if possible
        q_str = str(q)
        try:
            import pandas as pd
            dt = pd.to_datetime(q)
            q_str = f"{dt.year} Q{((dt.month-1)//3)+1}"
        except Exception:
            pass
        z = row.get("zscore")
        comps = row.get("components")
        if isinstance(comps, str):
            try:
                import json
                comps = json.loads(comps)
            except Exception:
                comps = {}
        if not isinstance(comps, dict):
            comps = {}
        row_vals = [q_str]
        for x in x_cols:
            val = comps.get(x)
            row_vals.append(f"{val:.3f}" if val is not None else "")
        row_vals.append(f"{z:.3f}" if z is not None else "")
        rows.append(row_vals)
    # Prepare header
    header = ["Quarter"] + x_cols + ["Z-Score"]
    # Format as table
    import tabulate
    table_str = tabulate.tabulate(rows, headers=header, tablefmt="github")
    if print_to_console:
        print("\nZ-Score Component Table (by Quarter):")
        print(table_str)
    # Save to file if out_base provided
    if out_base:
        out_path = f"{out_base}_zscore_components.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(table_str + "\n")
        print_info(f"Component table saved to {out_path}")

def report_zscore_full_report(df, model, out_base=None, print_to_console=True, context_info=None):
    """
    Generate a full formatted report including:
    - Context/decisions (model, classification, etc.)
    - Calculation formulas for X1..X5 (or X1..X4)
    - Table of all quarters with X components, Z-Score, and diagnostic
    - Raw data mapping table (values in millions of USD)

    Args:
        df (pd.DataFrame): DataFrame with Z-Score results and mapping info
        model (str): Z-Score model name
        out_base (str, optional): Output file base path (without extension)
        print_to_console (bool): Whether to print the report to the console
        context_info (dict, optional): Contextual info for the report header
    Returns:
        None. Prints and/or saves the report as a text file.
    """
    # Get company name for the report title
    company_name = None
    try:
        import yfinance as yf
        yf_ticker = yf.Ticker(context_info["Ticker"]) if context_info and "Ticker" in context_info else None
        if yf_ticker:
            info = yf_ticker.info
            company_name = info.get('shortName') or info.get('longName')
    except Exception:
        company_name = None
    if not company_name and context_info and "Ticker" in context_info:
        company_name = context_info["Ticker"].upper()
    # Title with company name and ticker
    if company_name and context_info and "Ticker" in context_info:
        title = f"# Altman Z-Score Analysis Report: {company_name} ({context_info['Ticker'].upper()})\n"
    else:
        title = "# Altman Z-Score Analysis Report\n"
    lines = [title]
    # Add spacing between sections
    lines.append("")
    lines.append("## Analysis Context and Decisions\n")
    if context_info:
        # Combine industry and SIC code into a single line
        industry_val = context_info.get("Industry")
        sic_val = context_info.get("SIC Code")
        if industry_val and sic_val and industry_val != "Unknown":
            lines.append(f"- **Industry:** {industry_val} (SIC {sic_val})")
        else:
            lines.append(f"- **Industry:** {industry_val or sic_val}")
        for k, v in context_info.items():
            if k in ("Industry", "SIC Code"):
                continue
            lines.append(f"- **{k}:** {v}")
        lines.append("")
    # 2. Calculation formulas
    model = str(model).lower()
    lines.append("")
    if model == "original":
        lines.append("## Altman Z-Score (Original) Formula\n")
        lines.append("Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5")
        lines.append("- X1 = (Current Assets - Current Liabilities) / Total Assets")
        lines.append("- X2 = Retained Earnings / Total Assets")
        lines.append("- X3 = EBIT / Total Assets")
        lines.append("- X4 = Market Value of Equity / Total Liabilities")
        lines.append("- X5 = Sales / Total Assets\n")
        x_cols = ["X1", "X2", "X3", "X4", "X5"]
    elif model == "private":
        lines.append("## Altman Z-Score (Private) Formula\n")
        lines.append("Z' = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5")
        lines.append("- X1 = (Current Assets - Current Liabilities) / Total Assets")
        lines.append("- X2 = Retained Earnings / Total Assets")
        lines.append("- X3 = EBIT / Total Assets")
        lines.append("- X4 = Book Value of Equity / Total Liabilities")
        lines.append("- X5 = Sales / Total Assets\n")
        x_cols = ["X1", "X2", "X3", "X4", "X5"]
    else:
        lines.append(f"## Altman Z-Score ({model.title()}) Formula\n")
        lines.append("Z = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4")
        lines.append("- X1 = (Current Assets - Current Liabilities) / Total Assets")
        lines.append("- X2 = Retained Earnings / Total Assets")
        lines.append("- X3 = EBIT / Total Assets")
        lines.append("- X4 = Market Value of Equity / Total Liabilities\n")
        x_cols = ["X1", "X2", "X3", "X4"]
    lines.append("")
    # 2.5. Table of raw data used in calculation (field mapping)
    # Format numbers in millions USD for the raw data table
    def format_number_millions(val):
        try:
            if val is None or val == "":
                return ""
            val = float(val)
            val_m = val / 1_000_000
            return f"{val_m:,.1f}"
        except Exception:
            return str(val)
    mapping_rows = []
    mapping_header = ["Quarter", "Canonical Field", "Mapped Raw Field", "Value (USD millions)", "Missing"]
    last_quarter = None
    for idx, row in enumerate(df.iterrows()):
        _, row = row
        q = row.get("quarter_end")
        q_str = str(q)
        try:
            import pandas as pd
            dt = pd.to_datetime(q)
            q_str = f"{dt.year} Q{((dt.month-1)//3)+1}"
        except Exception:
            pass
        field_mapping = row.get("field_mapping")
        if isinstance(field_mapping, str):
            try:
                import json
                field_mapping = json.loads(field_mapping)
            except Exception:
                field_mapping = {}
        if not isinstance(field_mapping, dict):
            field_mapping = {}
        for canon, mapping in field_mapping.items():
            mapped_raw = mapping.get("mapped_raw_field")
            val = mapping.get("value")
            missing = mapping.get("missing")
            mapping_rows.append([
                q_str,
                canon,
                mapped_raw if mapped_raw is not None else "",
                format_number_millions(val),
                "Yes" if missing else ""
            ])
        # Add a separator row after each quarter (if not last row)
        if idx < len(df) - 1:
            mapping_rows.append(["---", "---", "---", "---", "---"])
    import tabulate
    mapping_table_str = tabulate.tabulate(mapping_rows, headers=mapping_header, tablefmt="github")
    lines.append("## Raw Data Field Mapping Table (by Quarter)")
    lines.append(mapping_table_str)
    lines.append("")
    lines.append("All values are shown in millions of USD as reported by the data source. Missing fields are indicated in the 'Missing' column.")
    lines.append("")
    # 3. Table with diagnostics
    rows = []
    for _, row in df.iterrows():
        q = row.get("quarter_end")
        q_str = str(q)
        try:
            import pandas as pd
            dt = pd.to_datetime(q)
            q_str = f"{dt.year} Q{((dt.month-1)//3)+1}"
        except Exception:
            pass
        z = row.get("zscore")
        comps = row.get("components")
        diag = row.get("diagnostic")
        # Use the risk area (diagnostic) as the Diagnostic column
        if isinstance(comps, str):
            try:
                import json
                comps = json.loads(comps)
            except Exception:
                comps = {}
        if not isinstance(comps, dict):
            comps = {}
        row_vals = [q_str]
        for x in x_cols:
            val = comps.get(x)
            row_vals.append(f"{val:.3f}" if val is not None else "")
        row_vals.append(f"{z:.3f}" if z is not None else "")
        # Show only the risk area (e.g., 'Safe Zone', 'Distress Zone', 'Grey Zone')
        row_vals.append(diag or "")
        rows.append(row_vals)
    header = ["Quarter"] + x_cols + ["Z-Score", "Diagnostic"]
    import tabulate
    table_str = tabulate.tabulate(rows, headers=header, tablefmt="github")
    lines.append("## Z-Score Component Table (by Quarter)")
    lines.append(table_str)
    report = "\n".join(lines)
    if print_to_console:
        print(report)
    if out_base:
        out_path = f"{out_base}_zscore_full_report.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print_info(f"Full report saved to {out_path}")

def plot_zscore_trend(df, ticker, model, out_base, profile_footnote=None, stock_prices=None):
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
    if model == "original":
        model_thresholds = models.ModelThresholds.original()
    elif model == "private":
        model_thresholds = models.ModelThresholds.private_company()
    elif model in ("public", "em", "service"):
        model_thresholds = models.ModelThresholds.non_manufacturing()
    else:
        model_thresholds = models.ModelThresholds.original()

    # Compute correct y-limits before drawing bands
    z_min = min(zscores.min(), float(model_thresholds.distress_zone))
    z_max = max(zscores.max(), float(model_thresholds.safe_zone))
    margin = 0.5 * (z_max - z_min) * 0.1  # 10% margin
    ymin = z_min - margin
    # Add extra padding to the top for the legend
    legend_padding = (z_max - z_min) * 0.18  # 18% of range for legend space
    ymax = z_max + margin + legend_padding
    plt.ylim(ymin, ymax)
    # Draw bands in order: distress (bottom), grey (middle), safe (top)
    plt.axhspan(ymin, float(model_thresholds.distress_zone), color='#ff6666', alpha=0.8, label='Distress Zone', zorder=0)
    plt.axhspan(float(model_thresholds.distress_zone), float(model_thresholds.safe_zone), color='#cccccc', alpha=0.6, label='Grey Zone', zorder=0)
    plt.axhspan(float(model_thresholds.safe_zone), ymax, color='#66ff66', alpha=0.5, label='Safe Zone', zorder=0)
    # Add zone names inside the plot area, aligned to the left and vertically centered in each band
    ax = plt.gca()
    zone_x = 0.1  # Slightly inside the plot area
    ax.text(zone_x, (ymin + float(model_thresholds.distress_zone)) / 2, 'Distress',
            color='#a60000', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    ax.text(zone_x, (float(model_thresholds.distress_zone) + float(model_thresholds.safe_zone)) / 2, 'Grey',
            color='#444444', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)
    # Lower the 'Safe' label to avoid the legend
    safe_y = (float(model_thresholds.safe_zone) + ymax) / 2
    if safe_y > ymax - (ymax - ymin) * 0.15:
        safe_y = ymax - (ymax - ymin) * 0.15
    ax.text(zone_x, safe_y, 'Safe',
            color='#007a00', fontsize=11, ha='left', va='center',
            alpha=0.95, fontweight='bold', zorder=1000, clip_on=False)

    # Use integer positions for x-axis to ensure correct plotting and annotation
    x_dates = plot_df['quarter_end']
    x_quarters = [f"{d.year}Q{((d.month-1)//3)+1}" for d in x_dates]
    x_pos = range(len(x_quarters))
    plt.plot(x_pos, zscores, marker='o', label="Z-Score", color='blue', zorder=2)
    # Add value labels to each Z-Score point
    ax = plt.gca()
    for i, z_val in enumerate(zscores):
        try:
            label = f"{z_val:.2f}"
            ax.annotate(label, (i, z_val), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, color='blue')
        except Exception:
            pass
    # Format x-axis dates to show as quarters (e.g., '2024Q1'), horizontal
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_quarters, rotation=0, ha='center')

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
        company_name = ticker.upper()

    # Create title and subtitle
    plt.title(f"Altman Z-Score Trend for {company_name} ({ticker.upper()})")
    
    plt.xlabel("Quarter End")
    plt.ylabel("Z-Score")
    plt.grid(True, zorder=1)
    
    # Prepare threshold values for legend
    safe = float(model_thresholds.safe_zone)
    distress = float(model_thresholds.distress_zone)
    
    # Create legend patches
    legend_elements = [
        mpatches.Patch(facecolor='#ff6666', alpha=0.8, label=f'Distress Zone\n≤ {distress}'),
        mpatches.Patch(facecolor='#cccccc', alpha=0.6, label=f'Grey Zone\n{distress} to {safe}'),
        mpatches.Patch(facecolor='#66ff66', alpha=0.5, label=f'Safe Zone\n≥ {safe}'),
        Line2D([0], [0], color='blue', marker='o', label='Z-Score\nTrend Line', 
              markersize=4, linestyle='-', linewidth=1)
    ]
    
    # If stock prices are provided, add them on a secondary y-axis
    if stock_prices is not None and not stock_prices.empty:
        # Create a secondary y-axis for stock prices
        ax2 = ax.twinx()
        
        # Ensure stock prices dataframe has quarter_end and price columns
        if 'quarter_end' in stock_prices.columns and 'price' in stock_prices.columns:
            # Convert quarter_end to datetime if not already
            stock_prices['quarter_end'] = pd.to_datetime(stock_prices['quarter_end'])
            
            # Filter to just the quarters we have z-score data for
            common_quarters = set(pd.to_datetime(df['quarter_end']).dt.strftime('%Y-%m-%d'))
            stock_prices = stock_prices[stock_prices['quarter_end'].dt.strftime('%Y-%m-%d').isin(common_quarters)]
            
            if not stock_prices.empty:
                # Sort by quarter_end to ensure chronological order
                stock_prices = stock_prices.sort_values('quarter_end')
                
                # Create mapping from quarter_end to x position
                quarter_to_xpos = {q.strftime('%Y-%m-%d'): pos for q, pos in zip(x_dates, x_pos)}
                
                # Map each stock price quarter to its x-position
                stock_x_pos = [quarter_to_xpos.get(q.strftime('%Y-%m-%d'), -1) for q in stock_prices['quarter_end']]
                stock_prices_valid = stock_prices[~pd.Series(stock_x_pos).eq(-1)]
                stock_x_pos_valid = [x for x in stock_x_pos if x != -1]
                
                # Plot the stock prices on the secondary y-axis
                ax2.plot(stock_x_pos_valid, stock_prices_valid['price'], 
                      marker='s', color='green', linestyle='-', linewidth=1.5, 
                      label=f"{ticker} Price", zorder=3)
                
                # Add value labels to each stock price point
                for i, (x, price) in enumerate(zip(stock_x_pos_valid, stock_prices_valid['price'])):
                    try:
                        price_label = f"${price:.2f}"
                        ax2.annotate(price_label, (x, price), 
                                    textcoords="offset points", xytext=(0,-15), 
                                    ha='center', fontsize=9, color='green')
                    except Exception:
                        pass
                  # Set y-label for the secondary axis
                ax2.set_ylabel("Stock Price ($)", color='green')
                ax2.tick_params(axis='y', labelcolor='green')
                
                # Force the y-axis for stock prices to start at 0
                y_min, y_max = ax2.get_ylim()
                ax2.set_ylim(bottom=0, top=y_max * 1.1)  # Start at 0, add 10% padding to the top
                
                # Add stock price line to legend_elements
                legend_elements.append(
                    Line2D([0], [0], color='green', marker='s', label=f'{ticker} Price', 
                           markersize=4, linestyle='-', linewidth=1.5)
                )

    # Add legend with appropriate number of columns
    plt.gcf().subplots_adjust(bottom=0.22)  # Increased bottom margin from 0.2 to 0.22
    num_cols = 5 if stock_prices is not None and not stock_prices.empty else 4
    plt.legend(handles=legend_elements, ncol=num_cols, bbox_to_anchor=(0.5, -0.25),  # Moved down from -0.15 to -0.25
              loc='center', fontsize=8, frameon=True, framealpha=0.9)
    
    # Add profile info as subtitle if available
    if profile_footnote:
        plt.figtext(0.5, 0.95, profile_footnote, 
                   ha='center', va='top', fontsize=9, color='#666666')
    
    # Ensure output subdirectory for ticker exists
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    
    out_path = os.path.join(ticker_dir, f"zscore_{ticker}_trend.png")
    plt.savefig(out_path)
    print_info(f"Z-Score trend plot saved to {os.path.abspath(out_path)}")
    
    # Only show the plot if running interactively (not in headless environment)
    if hasattr(sys, 'ps1') or sys.flags.interactive:
        plt.show()
    # In headless or script mode, do not call plt.show() to avoid hangs
