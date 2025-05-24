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
from datetime import datetime
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
    print(f"[INFO] Company profile for {ticker}:")
    print(f"  Industry: {getattr(profile, 'industry', 'Unknown')}")
    print(f"  Public: {getattr(profile, 'is_public', 'Unknown')}")
    print(f"  Emerging Market: {getattr(profile, 'is_emerging_market', 'Unknown')}")
    print()

    # 2. Determine Z-Score model before fetching financials
    model = determine_zscore_model(profile)
    # 3. Fetch last 12 quarters of financials, only required fields for model
    fin_info = fetch_financials(ticker, end_date, model)
    import pandas as pd  # Ensure pd is available for all DataFrame and to_numeric usage
    if not fin_info or not fin_info.get("quarters"):
        logger.error(f"Failed to fetch financials for {ticker}")
        return pd.DataFrame([{"quarter_end": None, "zscore": None, "valid": False, "error": "No data"}])

    # 3. Fetch market value of equity for each quarter (using Yahoo)
    yahoo = YahooFinanceClient()
    quarters = fin_info["quarters"]
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
            # Format z-score with thousand separators and 2 decimal places
            zscore_val = f"{zscore_obj.z_score:,.2f}" if zscore_obj.z_score is not None else None
            results.append({
                "quarter_end": period_end,
                "zscore": zscore_val,
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
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out_base = os.path.join(output_dir, f"zscore_{ticker}_{end_date}")
    try:
        df.to_csv(f"{out_base}.csv", index=False)
        print(f"[INFO] Z-Score trend saved to {out_base}.csv")
    except Exception as e:
        print(f"[ERROR] Could not save CSV: {e}")
    try:
        df.to_json(f"{out_base}.json", orient="records", indent=2)
        print(f"[INFO] Z-Score trend saved to {out_base}.json")
    except Exception as e:
        print(f"[ERROR] Could not save JSON: {e}")
    # Print summary table to stdout
    try:
        print("\nZ-Score Trend Table:")
        print(df[["quarter_end", "zscore", "diagnostic", "model", "valid", "error", "api_payload"]].to_string(index=False))
    except Exception as e:
        print(f"[ERROR] Could not print summary table: {e}")
    # Plot trend (MVP: simple matplotlib line plot)
    try:
        import matplotlib.pyplot as plt
        plot_df = df[df["zscore"].notnull()]
        if not plot_df.empty:
            plt.figure(figsize=(10, 5))
            try:
                zscores = plot_df["zscore"].astype(float)
            except Exception:
                zscores = pd.to_numeric(plot_df["zscore"], errors="coerce")
            plt.plot(plot_df["quarter_end"], zscores, marker='o', label="Z-Score")
            plt.title(f"Altman Z-Score Trend for {ticker}")
            plt.xlabel("Quarter End")
            plt.ylabel("Z-Score")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{out_base}_trend.png")
            print(f"[INFO] Z-Score trend plot saved to {out_base}_trend.png")
            plt.show()
        else:
            print("[WARN] No valid Z-Score data to plot.")
    except ImportError:
        print("[WARN] matplotlib not installed, skipping plot.")
    except Exception as e:
        print(f"[WARN] Could not plot Z-Score trend: {e}")
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
