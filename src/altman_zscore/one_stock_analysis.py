import pandas as pd
import sys
import os
import datetime
import time
from typing import List, Optional
import logging
from sec_edgar_downloader._Downloader import Downloader
from altman_zscore.fetch_financials import fetch_financials
from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.industry_classifier import classify_company
from altman_zscore.compute_zscore import FinancialMetrics, compute_zscore, determine_zscore_model
from altman_zscore.data_validation import FinancialDataValidator
from datetime import datetime, timedelta
from dotenv import load_dotenv
from altman_zscore.sic_lookup import sic_map
from altman_zscore.compute_zscore import select_zscore_model_by_sic
import json
from altman_zscore.fetch_prices import get_quarterly_prices
from altman_zscore.plotting import plot_zscore_trend, report_zscore_components_table

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
    Fetch the latest 12 quarters of financials for the given ticker up to end_date using sec-edgar-downloader.
    Returns a list of dicts (one per quarter) with raw financial data.
    
    Note: This function is a placeholder for future SEC EDGAR integration.
    Currently, the implementation relies on Yahoo Finance API through fetch_financials().
    """
    # Note: Implementation moved to fetch_financials module, which uses Yahoo Finance
    # Future version will integrate direct SEC EDGAR API access
    return []

def analyze_single_stock_zscore_trend(ticker: str, start_date: str = "2024-01-01") -> pd.DataFrame:
    """
    Main entry for single-stock Z-Score trend analysis (MVP).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        start_date (str, optional): Only include quarters ending on or after this date (YYYY-MM-DD)
    Returns:
        pd.DataFrame: DataFrame with columns: ['quarter_end', 'zscore', 'valid', 'error', ...]
    
    Steps:
        1. Classify company (industry, maturity, etc.)
        2. Select Z-Score model based on profile
        3. Fetch last 12 quarters of financials (robust fallback logic)
        4. Validate and compute Z-Score for each quarter
        5. Output results to CSV, JSON, and plot
        6. Save all diagnostics and error reports to output/
    """
    logger = logging.getLogger("altman_zscore.one_stock_analysis")

    # 1. Classify company (industry, maturity, etc.)
    profile = classify_company(ticker)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out_base = os.path.join(output_dir, f"zscore_{ticker}")    # If profile is None or lacks industry, treat as not found and exit gracefully
    if not profile or getattr(profile, 'industry', None) in (None, '', 'unknown', 'Unknown'):
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": f"Could not classify company for ticker {ticker}. The ticker may not exist, may be delisted, or lacks industry/sector info.",
            "diagnostic": None,
            "model": None,
            "api_payload": str(profile) if profile else None
        }]
        ticker_dir = os.path.join('output', ticker.upper())
        os.makedirs(ticker_dir, exist_ok=True)
        out_base = os.path.join(ticker_dir, f"zscore_{ticker}")
        df = pd.DataFrame(error_result)
        try:
            df.to_csv(f"{out_base}_error.csv", index=False)
            df.to_json(f"{out_base}_error.json", orient="records", indent=2)
            print_info(f"Error output saved to {out_base}_error.csv and {out_base}_error.json")
        except Exception as e:
            print_error(f"Could not save error output: {e}")
        
        print_error(f"Could not classify company for ticker {Colors.BOLD}{ticker}{Colors.ENDC}.")
        print_error(f"Possible causes:")
        print_error(f" - The ticker symbol {ticker} may not exist")
        print_error(f" - The company may be delisted")
        print_error(f" - Industry/sector information is unavailable")
        print_error(f"Analysis aborted.")
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
    out_base = os.path.join(ticker_dir, f"zscore_{ticker}")
    with open(f"{out_base}_profile.txt", "w", encoding="utf-8") as f:
        f.write(profile_info)

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
    if sic_code:
        model = select_zscore_model_by_sic(sic_code, is_public=(str(is_public).lower() == 'true'), maturity=maturity_str)
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
        ticker_dir = os.path.join('output', ticker.upper())
        os.makedirs(ticker_dir, exist_ok=True)
        out_base = os.path.join(ticker_dir, f"zscore_{ticker}")
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
                    "diagnostic": diagnostic
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
                "diagnostic": diagnostic,
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
                "diagnostic": f"[ERROR] Exception: {e}",
                "model": str(model),
                "api_payload": q.get("raw_payload")
            })
    # After results are collected, create DataFrame
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
    if not os.path.exists('output'):
        os.makedirs('output', exist_ok=True)
    ticker_dir = os.path.join('output', ticker.upper())
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir, exist_ok=True)
    out_base = os.path.join(ticker_dir, f"zscore_{ticker}")
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
    try:
        # Only include columns that exist in the DataFrame
        summary_cols = [col for col in ["quarter_end", "zscore", "diagnostic", "model", "valid", "error", "api_payload"] if col in df.columns]
        summary_table = df[summary_cols].to_string(index=False)
        with open(f"{out_base}_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary_table)
    except Exception as e:
        print(f"[ERROR] Could not save summary table: {e}")
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
    
    # Fetch stock prices for the quarters in our Z-Score dataframe
    stock_prices = None
    try:
        # Extract the quarter_end dates from our Z-Score dataframe
        quarters_list = df['quarter_end'].tolist()
        # Fetch stock prices for these quarters
        stock_prices = get_quarterly_prices(ticker, quarters_list)
    except Exception as e:
        print(f"[WARN] Could not fetch stock prices for overlay: {e}")
    
    # Generate and print/save the X1..X5/z-score report table before plotting
    try:
        # Compose context info for the report
        context_info = {
            "Ticker": ticker,
            "Industry": industry,
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
    
    # Generate and print/save the X1..X5/z-score report table before plotting
    try:
        report_zscore_components_table(df, model, out_base, print_to_console=True)
    except Exception as e:
        print_warning(f"Could not generate Z-Score component table: {e}")
    # Plot trend with stock price overlay if available
    try:
        plot_zscore_trend(df, ticker, model, out_base, profile_footnote=footnote, stock_prices=stock_prices)
    except ImportError:
        print("[WARN] matplotlib not installed, skipping plot.")
    except Exception as e:
        print(f"[WARN] Could not plot Z-Score trend: {e}")
    # Save any additional output/diagnostic files to the ticker subfolder
    # Example: move bs_columns, bs_index, is_columns, yf_info files if they exist
    diagnostic_files = [
        f"bs_columns_{ticker}.txt",
        f"bs_index_{ticker}.txt",
        f"is_columns_{ticker}.txt",
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
