"""
Z-Score Text Reporting Utilities

This module provides functions to generate and save Altman Z-Score text reports and tables.
"""
import os
import tabulate

def print_info(msg):
    try:
        from altman_zscore.plotting import Colors
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {msg}")
    except Exception:
        print(f"[INFO] {msg}")

def report_zscore_components_table(df, model, out_base=None, print_to_console=True):
    # ...moved from plotting.py...
    model = str(model).lower()
    if model in ("original", "private"):
        x_cols = ["X1", "X2", "X3", "X4", "X5"]
    else:
        x_cols = ["X1", "X2", "X3", "X4"]
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
    header = ["Quarter"] + x_cols + ["Z-Score"]
    table_str = tabulate.tabulate(rows, headers=header, tablefmt="github")
    if print_to_console:
        print("\nZ-Score Component Table (by Quarter):")
        print(table_str)
    if out_base:
        out_path = f"{out_base}_zscore_components.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(table_str + "\n")
        print_info(f"Component table saved to {out_path}")

def report_zscore_full_report(df, model, out_base=None, print_to_console=True, context_info=None):
    # ...full function body moved from plotting.py...
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
    if company_name and context_info and "Ticker" in context_info:
        title = f"# Altman Z-Score Analysis Report: {company_name} ({context_info['Ticker'].upper()})\n"
    else:
        title = "# Altman Z-Score Analysis Report\n"
    lines = [title]
    lines.append("")
    lines.append("## Analysis Context and Decisions\n")
    if context_info:
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
        if idx < len(df) - 1:
            mapping_rows.append(["---", "---", "---", "---", "---"])
    mapping_table_str = tabulate.tabulate(mapping_rows, headers=mapping_header, tablefmt="github")
    lines.append("## Raw Data Field Mapping Table (by Quarter)")
    lines.append(mapping_table_str)
    lines.append("")
    lines.append("All values are shown in millions of USD as reported by the data source. Missing fields are indicated in the 'Missing' column.")
    lines.append("")
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
        row_vals.append(diag or "")
        rows.append(row_vals)
    header = ["Quarter"] + x_cols + ["Z-Score", "Diagnostic"]
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
