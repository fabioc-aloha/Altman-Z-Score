import pandas as pd
import sys
import os
import datetime
import time
from typing import List, Optional
import logging
from sec_edgar_downloader._Downloader import Downloader
from altman_zscore.data_fetching.financials import fetch_financials
from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.industry_classifier import classify_company
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.compute_zscore import FinancialMetrics, compute_zscore, determine_zscore_model
from altman_zscore.data_validation import FinancialDataValidator
from datetime import datetime, timedelta
from dotenv import load_dotenv
from altman_zscore.sic_lookup import sic_map
from altman_zscore.compute_zscore import select_zscore_model_by_sic
import json
from altman_zscore.data_fetching.prices import get_quarterly_prices, get_monthly_price_stats
from altman_zscore.plotting import plot_zscore_trend, report_zscore_full_report
from altman_zscore.utils.paths import get_output_dir

# ANSI color codes for terminal output
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
    """Print an info message with cyan color"""
    print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {msg}")

def print_success(msg):
    """Print a success message with green color"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {msg}")

def print_warning(msg):
    """Print a warning message with yellow color"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {msg}")

def print_error(msg):
    """Print an error message with red color"""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {msg}")

def print_header(msg):
    """Print a header with bold blue color"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{msg}{Colors.ENDC}\n")

load_dotenv()

def fetch_sec_quarterly_financials(ticker: str, end_date: str) -> list:
    """
    Placeholder for future SEC EDGAR integration. Currently unused.
    Returns an empty list. All financials are fetched via Yahoo Finance in fetch_financials().
    """
    # Note: Implementation moved to fetch_financials module, which uses Yahoo Finance
    # Future version will integrate direct SEC EDGAR API access
    return []

def get_zscore_path(ticker, ext=None):
    """Return the path for Z-Score output files in the ticker's directory."""
    # Use the ticker directory as base, not a subdirectory called 'zscore'
    base = get_output_dir(None, ticker=ticker)
    return f"{os.path.join(base, f'zscore_{ticker}')}{ext if ext else ''}"

def analyze_single_stock_zscore_trend(ticker: str, start_date: str = "2024-01-01") -> pd.DataFrame:
    """
    Main entry point for single-stock Altman Z-Score trend analysis.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        start_date (str, optional): Only include quarters ending on or after this date (YYYY-MM-DD)
    Returns:
        pd.DataFrame: DataFrame with columns: ['quarter_end', 'zscore', 'valid', 'error', ...]

    Workflow:
        1. Classify company (industry, maturity, etc.)
        2. Select Z-Score model based on profile and SIC code
        3. Fetch last 12 quarters of financials (robust fallback logic)
        4. Validate and compute Z-Score for each quarter
        5. Output results to CSV, JSON, and plot
        6. Save all diagnostics and error reports to output/
    """
    logger = logging.getLogger("altman_zscore.one_stock_analysis")    # Setup base output directory using absolute path    # 1. Classify company (industry, maturity, etc.)
    profile = classify_company(ticker)
    
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")    # All outputs for this ticker go to ./output/<TICKER>/
    if not profile or getattr(profile, 'industry', None) in (None, '', 'unknown', 'Unknown'):
        from altman_zscore.utils.paths import write_ticker_not_available
        print_error(f"Could not classify company for ticker {Colors.BOLD}{ticker}{Colors.ENDC}.")
        print_error(f"Possible causes:")
        print_error(f" - The ticker symbol {ticker} may not exist")
        print_error(f" - The company may be delisted")
        print_error(f" - Industry/sector information is unavailable")
        print_error(f"Analysis aborted.")
        write_ticker_not_available(ticker, reason="Classification failed: industry/sector not found or ticker does not exist.")
        sys.exit(1)

    # Only print company profile if classification succeeded
    # (Removed: profile_info and writing zscore_<TICKER>_profile.txt)

    # Extract company profile fields immediately after classification
    industry = getattr(profile, 'industry', 'Unknown')
    is_public = getattr(profile, 'is_public', 'Unknown')
    is_em = getattr(profile, 'is_emerging_market', 'Unknown')
    maturity = getattr(profile, 'maturity', None)

    # 2. Determine Z-Score model before fetching financials
    # Prefer robust SIC-based model selection
    model = None
    # Try to extract SIC code if present in industry string
    sic_code = None
    if industry and 'SIC' in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == 'SIC' and i+1 < len(parts):
                sic_code = parts[i+1]
                break
    maturity_str = str(maturity) if maturity is not None else ''
    # Always call select_zscore_model_by_sic with a string, even if sic_code is None
    model = select_zscore_model_by_sic(str(sic_code or ''), is_public=(str(is_public).lower() == 'true'), maturity=maturity_str)
    if not model:
        model = determine_zscore_model(profile)

    # 3. Fetch last 12 quarters of financials, only required fields for model
    # Pass an empty string for end_date (fetch_financials requires str, but we ignore it)
    fin_info = fetch_financials(ticker, "", model)
    if fin_info is None:
        # Save a user-friendly error report to output and exit cleanly
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": f"No financial data available for {ticker}. The company may be delisted, never public, or data is missing from yfinance/SEC.",
            "diagnostic": None,
            "model": model,
            "api_payload": None
        }]
        df = pd.DataFrame(error_result)
        try:
            df.to_csv(f"{out_base}_error.csv", index=False)
            df.to_json(f"{out_base}_error.json", orient="records", indent=2)
            print_info(f"Error output saved to {out_base}_error.csv and {out_base}_error.json")
        except Exception as e:
            print_error(f"Could not save error output: {e}")
        print_error(f"No financial data available for {ticker}. Analysis cannot proceed.")
        print_warning(f"This may be due to: company not being listed, recent IPO, or missing data in sources.")
        sys.exit(1)
    # Only fail if there are zero valid quarters; allow partial data for new/delisted tickers
    valid_quarters = [q for q in fin_info["quarters"] if any(v not in (None, '', 0.0) for k, v in q.items() if k != 'raw_payload')]
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            valid_quarters = [q for q in valid_quarters if 'period_end' in q and q['period_end'] and datetime.strptime(str(q['period_end'])[:10], "%Y-%m-%d").date() >= start_dt]
        except Exception as e:
            print_warning(f"Could not filter quarters by start_date: {e}")
    if not fin_info or not fin_info.get("quarters") or len(valid_quarters) == 0:
        raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")

    # Use all available quarters (no end_date filtering)
    quarters = list(reversed(valid_quarters))  # chronological order

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
            diagnostic = validator.summarize_issues(issues)
            errors = [i.issue for i in issues if i.level.name == "ERROR"]
            if errors:
                results.append({
                    "quarter_end": period_end,
                    "zscore": None,
                    "valid": False,
                    "error": "; ".join(errors),
                    "diagnostic": None,  # No risk area if errors prevent computation
                    "validation_summary": diagnostic
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
                "components": zscore_obj.components,  # <-- Add this line
                "valid": True,
                "error": None,
                "diagnostic": zscore_obj.diagnostic,  # Set to risk area
                "validation_summary": diagnostic,     # Store validation summary separately
                "model": str(model),
                "api_payload": q.get("raw_payload"),
                "field_mapping": q.get("field_mapping")  # <-- Ensure field_mapping is included
            })
        except Exception as e:
            logger.error(f"Error processing quarter {period_end} for {ticker}: {e}")
            results.append({
                "quarter_end": period_end,
                "zscore": None,
                "valid": False,
                "error": str(e),
                "diagnostic": f"[ERROR] Exception: {e}",
                "model": str(model),
                "api_payload": q.get("raw_payload")
            })    # After results are collected, create DataFrame
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
    df = pd.DataFrame(results)    # Reporting: output to CSV, JSON, and print summary table
    try:
        df.to_csv(f"{out_base}.csv", index=False)
        print_info(f"Results saved to CSV: {out_base}.csv")
    except Exception as e:
        print_error(f"Could not save CSV: {e}")
    try:
        df.to_json(f"{out_base}.json", orient="records", indent=2)
        print_info(f"Results saved to JSON: {out_base}.json")
    except Exception as e:
        print_error(f"Could not save JSON: {e}")# Only print warnings and errors
    for _, row in df.iterrows():
        if row.get("error"):
            print_warning(f"{row['quarter_end']}: {row['error']}")
    # Save summary table to file, do not print to terminal
    # (Removed: summary table and writing zscore_<TICKER>_summary.txt)
    # Prepare single-line company profile footnote for chart
    industry = getattr(profile, 'industry', 'Unknown')
    is_public = getattr(profile, 'is_public', 'Unknown')
    is_em = getattr(profile, 'is_emerging_market', 'Unknown')
    maturity = getattr(profile, 'maturity', None)
    maturity_map = {
        'early': 'Early Stage',
        'growth': 'Growth Stage',
        'mature': 'Mature Company',
        'emerging': 'Emerging Market',
        'private': 'Private Company',
        'public': 'Public Company',
        # Add more as needed
    }
    maturity_desc = maturity_map.get(str(maturity).lower(), maturity) if maturity else 'Unknown'
    # Try to extract SIC code if present in industry string
    sic_code = None
    if industry and 'SIC' in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == 'SIC' and i+1 < len(parts):
                sic_code = parts[i+1]
                break
    # Map SIC code to description (expanded mapping) now imported from sic_lookup.py
    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    # Refine model selection using decoded maturity and SIC code
    model_hint = None
    if sic_code:
        if str(sic_code).startswith('37') or str(sic_code).startswith('36'):
            model_hint = 'original'  # Manufacturing/industrial
        elif str(sic_code).startswith('73'):
            model_hint = 'tech'      # Software/tech
        elif str(sic_code).startswith('60') or str(sic_code).startswith('61'):
            model_hint = 'service'   # Financial services
        elif str(sic_code).startswith('87') or str(sic_code).startswith('89'):
            model_hint = 'service'   # Research/consulting/services
        # Add more rules as needed
    if maturity and str(maturity).lower() in ['private', 'emerging']:
        model_hint = 'private'
    if model_hint:
        model = model_hint
    else:
        model = determine_zscore_model(profile)
        
    # Compose industry string for footnote
    if sic_code and sic_desc:
        industry_foot = f"{sic_desc} (SIC {sic_code})"
    elif sic_code:
        industry_foot = f"SIC {sic_code}"
    else:
        industry_foot = industry if industry else 'Unknown industry'
    footnote = f"Industry: {industry_foot} | Maturity: {maturity_desc} | Public: {is_public} | Emerging Market: {is_em} | Model: {model}"
    
    # Fetch stock prices for the Z-Score period
    stock_prices = None
    monthly_stats = None  # Initialize monthly_stats to None to avoid unbound variable issue
    try:
        # Extract start and end dates from our Z-Score dataframe
        quarters = pd.to_datetime(df['quarter_end'])
        start_date = quarters.min().strftime('%Y-%m-%d')
        end_date = quarters.max().strftime('%Y-%m-%d')
          
        # Fetch monthly price stats and quarterly prices
        monthly_stats = get_monthly_price_stats(ticker, start_date, end_date)
        stock_prices = get_quarterly_prices(ticker, df['quarter_end'].tolist())
        # Save price data to disk
        try:
            from altman_zscore.data_fetching.prices import save_price_data_to_disk
            if not monthly_stats.empty:
                csv_path, json_path = save_price_data_to_disk(monthly_stats, ticker, "monthly_prices")
                print_info(f"Monthly price statistics saved to {os.path.basename(csv_path)} and {os.path.basename(json_path)}")
            if not stock_prices.empty:
                csv_path, json_path = save_price_data_to_disk(stock_prices, ticker, "quarterly_prices")
                print_info(f"Quarterly prices saved to {os.path.basename(csv_path)} and {os.path.basename(json_path)}")
        except (ImportError, AttributeError):
            # If save_price_data_to_disk is not available or fails
            print_warning("Price data saving to disk is not available or failed")
    except Exception as e:
        print(f"[WARN] Could not fetch stock prices for overlay: {e}")
    
    # Generate and print/save the X1..X5/z-score report table before plotting
    try:
        # Compose context info for the report
        # Use mapped industry name if available, else fallback to raw industry string
        if sic_desc:
            industry_for_context = sic_desc
        elif sic_code:
            industry_for_context = f"SIC {sic_code}"
        else:
            industry_for_context = industry
        context_info = {
            "Ticker": ticker,
            "Industry": industry_for_context,
            "Public": is_public,
            "Emerging Market": is_em,
            "Maturity": maturity,
            "Model": model,
            "SIC Code": sic_code or "N/A",
            "Analysis Date": datetime.now().strftime("%Y-%m-%d")
        }
        from altman_zscore.plotting import report_zscore_full_report
        report_zscore_full_report(df, model, out_base, print_to_console=True, context_info=context_info)
    except Exception as e:
        print_warning(f"Could not generate full Z-Score report: {e}")
        
    # Plot trend with stock price overlay if available
    try:
        # Pass monthly_stats as a separate parameter
        plot_zscore_trend(df, ticker, model, out_base, profile_footnote=footnote, stock_prices=stock_prices, monthly_stats=monthly_stats)
    except ImportError:
        print("[WARN] matplotlib not installed, skipping plot.")
    except Exception as e:
        print(f"[WARN] Could not plot Z-Score trend: {e}")
        
    # Save any additional output/diagnostic files to the ticker subfolder
    # (No move needed: diagnostics are now written directly to ticker_dir)
    return df

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="Run Altman Z-Score analysis for a single stock.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., MSFT)")
    parser.add_argument("--start_date", type=str, default="2024-01-01", help="Start date for analysis (YYYY-MM-DD)")
    args = parser.parse_args()
    analyze_single_stock_zscore_trend(args.ticker, args.start_date)
