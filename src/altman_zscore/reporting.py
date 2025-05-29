"""
Z-Score Text Reporting Utilities

This module provides functions to generate and save Altman Z-Score text reports and tables.
"""
import os
import tabulate
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.utils.colors import Colors

def print_info(msg):
    """Print an info message with blue color if supported"""
    try:
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {msg}")
    except:
        print(f"[INFO] {msg}")

def report_zscore_full_report(df, model, out_base=None, print_to_console=True, context_info=None, generate_docx=True):
    """
    Generate and save a full Altman Z-Score analysis report in Markdown format, and optionally convert it to DOCX (Word).
    Args:
        df: DataFrame with Z-Score results and mappings
        model: Z-Score model name
        out_base: Output file base name (no extension)
        print_to_console: If True, print the report to stdout
        context_info: Optional dict with company/ticker/industry context
        generate_docx: If True (default), also generate a DOCX version of the report
    """
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
    # --- Model/Threshold Overrides and Assumptions Section ---
    # If the DataFrame contains a ZScoreResult with override_context, log it
    if hasattr(df, 'zscore_results') and df.zscore_results:
        override_context = getattr(df.zscore_results[0], 'override_context', None)
        if override_context:
            lines.append("### Model/Threshold Overrides and Assumptions\n")
            for k, v in override_context.items():
                lines.append(f"- **{k}:** {v}")
            lines.append("")
    elif 'override_context' in df.columns:
        # If override_context is a column (e.g., from DataFrame of results)
        oc = df['override_context'].iloc[0]
        if oc:
            lines.append("### Model/Threshold Overrides and Assumptions\n")
            for k, v in oc.items():
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
    # --- Financial Analysis & Commentary Section ---
    lines.append("\n\n## Financial Analysis & Commentary\n")
    # Compose a summary paragraph using LLM for richer commentary
    try:
        from altman_zscore.api.openai_client import get_llm_qualitative_commentary
        # Compose the context for the LLM: pass the full report so far (excluding the qualitative section)
        llm_commentary = get_llm_qualitative_commentary("\n".join(lines))
        lines.append(llm_commentary.strip() + "\n")
    except Exception as e:
        lines.append("> [LLM commentary unavailable: {}]".format(e))
    import os  # Ensure os is imported for chart embedding logic
    docx_path = None
    out_path = None
    if out_base:
        out_path = get_output_dir(relative_path=f"{out_base}_zscore_full_report.md")
    # --- Chart Section ---
    ticker = context_info.get('Ticker') if context_info else None
    chart_md = None
    if ticker and out_path:
        chart_path = os.path.join('output', ticker, f'zscore_{ticker}_trend.png')
        if os.path.exists(chart_path):
            rel_chart_path = os.path.relpath(chart_path, os.path.dirname(out_path)).replace('\\', '/')
            chart_md = f"\n![Z-Score and Price Trend Chart]({rel_chart_path})\n"
            chart_md += "\n"  # Add a new line before the caption
            chart_md += f"*Figure: Z-Score and stock price trend for {ticker.upper()} (see output folder for full-resolution image)*\n"
    if chart_md:
        lines.append(chart_md)
    lines.append("\n### References and Data Sources\n")
    lines.append("- **Financials:** SEC EDGAR/XBRL filings, Yahoo Finance, and company quarterly/annual reports.")
    lines.append("- **Market Data:** Yahoo Finance (historical prices, market value of equity).")
    lines.append("- **Field Mapping & Validation:** Automated mapping with code-level synonym fallback and Pydantic schema validation. See Raw Data Field Mapping Table above.")
    lines.append("- **Computation:** All Z-Score calculations use the Altman Z-Score model as described in the report, with robust error handling and logging.\n")
    lines.append("---")
    report = "\n".join(lines)
    if print_to_console:
        print(report)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print_info(f"Full report saved to {out_path}")
        if generate_docx:
            try:
                from altman_zscore.md_to_docx import convert_report_md_to_docx
                docx_path = out_path.replace('.md', '.docx')
                convert_report_md_to_docx(out_path, docx_path)
            except Exception as e:
                print_info(f"[DOCX conversion failed: {e}]")
    return report

# (md to docx conversion moved to md_to_docx.py for modularity)
