"""
Single Stock Altman Z-Score Trend Analysis (MVP)

Pipeline:
1. Input: ticker, (optional) end_date
2. Fetch: 12 quarters of financials (SEC EDGAR), price history (Yahoo)
3. Validate: Pydantic schemas for each quarter
4. Compute: Altman Z-Score per quarter (industry/maturity calibrated)
5. Report: Table and plot of Z-Score trend (MVP), overlay price (v1)
"""
import os
import argparse
import datetime
from typing import List, Optional
import pandas as pd
from sec_edgar_downloader._Downloader import Downloader
import logging
from altman_zscore.fetch_financials import fetch_financials
from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.industry_classifier import classify_company
from altman_zscore.compute_zscore import FinancialMetrics, compute_zscore, determine_zscore_model
from altman_zscore.data_validation import FinancialDataValidator
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fetch_sec_quarterly_financials(ticker: str, end_date: str) -> list:
    """
    Fetch the latest 12 quarters of financials for the given ticker up to end_date using sec-edgar-downloader.
    Returns a list of dicts (one per quarter) with raw financial data.
    """
    # TODO: Implement actual fetching and XBRL parsing logic
    # 1. Use Downloader to get 10-Q and 10-K filings up to end_date
    # 2. Parse XBRL for each filing to extract required fields
    # 3. Sort by period_end, return last 12 quarters
    return []

def analyze_single_stock_zscore_trend(ticker: str, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Main entry for single-stock Z-Score trend analysis (MVP).
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        end_date: Analysis end date (YYYY-MM-DD), default today
    Returns:
        DataFrame with columns: ['quarter_end', 'zscore', 'valid', 'error', ...]
    """
    logger = logging.getLogger("altman_zscore.one_stock_analysis")
    if not end_date:
        end_date = datetime.today().strftime("%Y-%m-%d")

    import os  # Ensure os is imported before use
    # 1. Classify company (industry, maturity, etc.)
    profile = classify_company(ticker)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out_base = os.path.join(output_dir, f"zscore_{ticker}_{end_date}")
    if not profile or getattr(profile, 'industry', None) in (None, '', 'unknown', 'Unknown'):
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": f"Could not classify company for ticker {ticker}",
            "diagnostic": None,
            "model": None,
            "api_payload": str(profile) if profile else None
        }]
        import pandas as pd
        df = pd.DataFrame(error_result)
        try:
            df.to_csv(f"{out_base}_error.csv", index=False)
            df.to_json(f"{out_base}_error.json", orient="records", indent=2)
            print(f"[INFO] Error output saved to {out_base}_error.csv and {out_base}_error.json")
        except Exception as e:
            print(f"[ERROR] Could not save error output: {e}")
        print(f"[ERROR] Could not classify company for ticker {ticker}. Aborting analysis.")
        import sys
        sys.exit(1)
    # Only print company profile if classification succeeded
    profile_info = (
        f"Company profile for {ticker}:\n"
        f"  Industry: {getattr(profile, 'industry', 'Unknown')}\n"
        f"  Public: {getattr(profile, 'is_public', 'Unknown')}\n"
        f"  Emerging Market: {getattr(profile, 'is_emerging_market', 'Unknown')}\n"
    )
    # Save company profile info to file
    ticker_dir = os.path.join('output', ticker.upper())
    os.makedirs(ticker_dir, exist_ok=True)
    out_base = os.path.join(ticker_dir, f"zscore_{ticker}_{end_date}")
    with open(f"{out_base}_profile.txt", "w", encoding="utf-8") as f:
        f.write(profile_info)

    # 2. Determine Z-Score model before fetching financials
    model = determine_zscore_model(profile)
    # 3. Fetch last 12 quarters of financials, only required fields for model
    fin_info = fetch_financials(ticker, end_date, model)
    import pandas as pd  # Ensure pd is available for all DataFrame and to_numeric usage
    # Only fail if there are zero valid quarters; allow partial data for new/delisted tickers
    valid_quarters = [q for q in fin_info["quarters"] if any(v not in (None, '', 0.0) for k, v in q.items() if k != 'raw_payload')]
    if not fin_info or not fin_info.get("quarters") or len(valid_quarters) == 0:
        raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")

    # Filter to all available quarters up to end_date
    try:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        valid_quarters_sorted = sorted(valid_quarters, key=lambda q: q.get("period_end"), reverse=True)
        filtered_quarters = []
        for q in valid_quarters_sorted:
            period_end = q.get("period_end")
            if period_end:
                try:
                    q_dt = datetime.strptime(str(period_end)[:10], "%Y-%m-%d")
                    if q_dt <= end_dt:
                        filtered_quarters.append(q)
                except Exception:
                    continue
        # Do not limit by number of quarters; use all available
    except Exception as e:
        raise ValueError(f"Invalid end_date format: {end_date}. Error: {e}")
    if not filtered_quarters:
        raise ValueError(f"No financial data for available quarters up to {end_date} for ticker '{ticker}'.")
    quarters = list(reversed(filtered_quarters))  # chronological order

    # 3. Fetch market value of equity for each quarter (using Yahoo)
    yahoo = YahooFinanceClient()
    results = []
    for q in quarters:
        period_end = q.get("period_end")
        try:
            # Convert period_end to datetime.date
            if isinstance(period_end, str):
                try:
                    period_end_dt = datetime.strptime(period_end, "%Y-%m-%d").date()
                except ValueError:
                    # Try parsing with time component
                    period_end_dt = datetime.strptime(period_end.split()[0], "%Y-%m-%d").date()
            else:
                period_end_dt = period_end
            mve, actual_date = yahoo.get_market_cap_on_date(ticker, period_end_dt)
            if mve is None:
                mve = 0.0  # fallback to 0.0 if market cap is missing
            metrics = FinancialMetrics.from_dict(q, mve, period_end_dt)
            validator = FinancialDataValidator()
            issues = validator.validate(q)
            errors = [i.issue for i in issues if i.level.name == "ERROR"]
            if errors:
                results.append({
                    "quarter_end": period_end,
                    "zscore": None,
                    "valid": False,
                    "error": "; ".join(errors)
                })
                continue
            # For private model, pass book_value_equity if present in q, else fallback to mve
            if model == "private":
                metrics_dict = metrics.__dict__.copy()
                metrics_dict["book_value_equity"] = q.get("book_value_equity", mve)
                zscore_obj = compute_zscore(metrics_dict, model)
            else:
                zscore_obj = compute_zscore(metrics.__dict__, model)
            # Store zscore as float for analysis/plotting, and add formatted string for display/export
            zscore_float = float(zscore_obj.z_score) if zscore_obj.z_score is not None else None
            zscore_str = f"{zscore_float:,.2f}" if zscore_float is not None else None
            results.append({
                "quarter_end": period_end,
                "zscore": zscore_float,
                "zscore_str": zscore_str,
                "valid": True,
                "error": None,
                "diagnostic": zscore_obj.diagnostic,
                "model": str(model),
                "api_payload": q.get("raw_payload")
            })
        except Exception as e:
            logger.error(f"Error processing quarter {period_end} for {ticker}: {e}")
            results.append({
                "quarter_end": period_end,
                "zscore": None,
                "valid": False,
                "error": str(e),
                "diagnostic": None,
                "model": str(model),
                "api_payload": q.get("raw_payload")
            })
    # After results are collected, create DataFrame
    import json
    def safe_payload(val):
        if isinstance(val, (dict, list)):
            try:
                return json.dumps(val)
            except Exception:
                return str(val)
        return val
    for r in results:
        if 'api_payload' in r:
            r['api_payload'] = safe_payload(r['api_payload'])
    df = pd.DataFrame(results)
    # Reporting: output to CSV, JSON, and print summary table
    # Ensure output and ticker subdirectory exist
    import os
    if not os.path.exists('output'):
        os.makedirs('output', exist_ok=True)
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    out_base = os.path.join(ticker_dir, f"zscore_{ticker}_{end_date}")
    try:
        df.to_csv(f"{out_base}.csv", index=False)
    except Exception as e:
        print(f"[ERROR] Could not save CSV: {e}")
    try:
        df.to_json(f"{out_base}.json", orient="records", indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save JSON: {e}")
    # Only print warnings and errors
    for _, row in df.iterrows():
        if row.get("error"):
            print(f"[WARN] {row['quarter_end']}: {row['error']}")
    # Save summary table to file, do not print to terminal
    try:
        summary_table = df[["quarter_end", "zscore", "diagnostic", "model", "valid", "error", "api_payload"]].to_string(index=False)
        with open(f"{out_base}_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary_table)
    except Exception as e:
        print(f"[ERROR] Could not save summary table: {e}")
    # Prepare single-line company profile footnote for chart
    industry = getattr(profile, 'industry', 'Unknown')
    is_public = getattr(profile, 'is_public', 'Unknown')
    is_em = getattr(profile, 'is_emerging_market', 'Unknown')
    # Try to extract SIC code if present in industry string
    sic_code = None
    if industry and 'SIC' in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == 'SIC' and i+1 < len(parts):
                sic_code = parts[i+1]
                break
    # Map SIC code to description (minimal mapping for demonstration)
    sic_map = {
        '7372': 'Prepackaged Software',
        # Add more mappings as needed
    }
    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    # Compose industry string for footnote
    if sic_code and sic_desc:
        industry_foot = f"{sic_desc} (SIC {sic_code})"
    elif sic_code:
        industry_foot = f"SIC {sic_code}"
    else:
        industry_foot = industry if industry else 'Unknown industry'
    footnote = f"Industry: {industry_foot} | Public: {is_public} | Emerging Market: {is_em} | Model: {model}"
    # Plot trend (MVP: simple matplotlib line plot)
    try:
        from altman_zscore.plotting import plot_zscore_trend
        plot_zscore_trend(df, ticker, model, out_base, profile_footnote=footnote)
    except ImportError:
        print("[WARN] matplotlib not installed, skipping plot.")
    except Exception as e:
        print(f"[WARN] Could not plot Z-Score trend: {e}")
    # Save any additional output/diagnostic files to the ticker subfolder
    # Example: move bs_columns, bs_index, is_columns, yf_info files if they exist
    diagnostic_files = [
        f"bs_columns_{ticker}_{end_date}.txt",
        f"bs_index_{ticker}_{end_date}.txt",
        f"is_columns_{ticker}_{end_date}.txt",
        f"yf_info_{ticker}.json"
    ]
    # Move diagnostic files and log the move in a file, not terminal
    move_log_path = os.path.join(ticker_dir, f"{ticker}_file_moves.log")
    with open(move_log_path, "a", encoding="utf-8") as move_log:
        for fname in diagnostic_files:
            src_path = os.path.join('output', fname)
            dst_path = os.path.join(ticker_dir, fname)
            if os.path.exists(src_path):
                try:
                    os.replace(src_path, dst_path)
                    move_log.write(f"Moved {fname} to {os.path.abspath(dst_path)}\n")
                except Exception as e:
                    print(f"[WARN] Could not move {fname}: {e}")
    return df

def parse_args():
    parser = argparse.ArgumentParser(description="Single Stock Altman Z-Score Trend Analysis")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--date", type=str, default=datetime.today().date().isoformat(),
                        help="Analysis end date (YYYY-MM-DD), default: today")
    return parser.parse_args()

def main():
    args = parse_args()
    ticker = args.ticker.upper()
    end_date = args.date
    print(f"[INFO] Running Z-Score trend analysis for {ticker} as of {end_date}")

    # 1. Classify company (industry, maturity, etc.)
    profile = classify_company(ticker)
    if not profile:
        print(f"[ERROR] Could not classify company for ticker {ticker}")
        return

    df = analyze_single_stock_zscore_trend(ticker, end_date)
    print(df)

if __name__ == "__main__":
    main()

# Example usage in pipeline:
# profile = classify_company('AAPL')
# print(profile.industry, profile.is_public, profile.is_emerging_market)
