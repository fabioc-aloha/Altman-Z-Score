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

class CompanyClassificationError(Exception):
    """Exception raised when company classification fails."""
    pass

class FinancialDataError(Exception):
    """Exception raised when financial data cannot be retrieved or processed."""
    pass

def save_error_report(ticker: str, error_result: list, out_base: str) -> None:
    """
    Save error report to CSV and JSON files.
    
    Args:
        ticker (str): Stock ticker symbol
        error_result (list): List of error data dictionaries
        out_base (str): Output file base path
    """
    df = pd.DataFrame(error_result)
    try:
        df.to_csv(f"{out_base}_error.csv", index=False)
        df.to_json(f"{out_base}_error.json", orient="records", indent=2)
        print_info(f"Error output saved to {out_base}_error.csv and {out_base}_error.json")
    except Exception as e:
        print_error(f"Could not save error output: {e}")

def extract_sic_code(industry: str) -> str:
    """
    Extract SIC code from industry string if present.
    
    Args:
        industry (str): Industry string that may contain SIC code
    
    Returns:
        str: SIC code or None if not found
    """
    sic_code = None
    if industry and 'SIC' in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == 'SIC' and i+1 < len(parts):
                sic_code = parts[i+1]
                break
    return sic_code

def determine_model_from_sic(sic_code: str, maturity: str) -> str:
    """
    Determine Z-Score model based on SIC code and maturity.
    
    Args:
        sic_code (str): SIC code
        maturity (str): Company maturity
        
    Returns:
        str: Model hint or None
    """
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
    return model_hint

def create_output_directory(ticker: str) -> tuple:
    """
    Create output directory structure for ticker.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        tuple: (output_dir, ticker_dir, out_base) paths
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    ticker_dir = os.path.join('output', ticker.upper())
    os.makedirs(ticker_dir, exist_ok=True)
    out_base = os.path.join(ticker_dir, f"zscore_{ticker}")
    return output_dir, ticker_dir, out_base

def process_company_profile(ticker: str, profile: any) -> tuple:
    """
    Process company profile and save profile info.
    
    Args:
        ticker (str): Stock ticker symbol
        profile: Company profile object
    
    Returns:
        tuple: (industry, is_public, is_em, maturity, out_base) information
    """
    industry = getattr(profile, 'industry', 'Unknown')
    is_public = getattr(profile, 'is_public', 'Unknown')
    is_em = getattr(profile, 'is_emerging_market', 'Unknown')
    maturity = getattr(profile, 'maturity', None)
    
    # Create profile info string
    profile_info = (
        f"Company profile for {ticker}:\n"
        f"  Industry: {industry}\n"
        f"  Public: {is_public}\n"
        f"  Emerging Market: {is_em}\n"
    )
    
    # Save company profile info to file
    _, ticker_dir, out_base = create_output_directory(ticker)
    with open(f"{out_base}_profile.txt", "w", encoding="utf-8") as f:
        f.write(profile_info)
        
    return industry, is_public, is_em, maturity, out_base

def process_quarter_data(q: dict, ticker: str, period_end, yahoo, model: str) -> dict:
    """
    Process a single quarter's financial data.
    
    Args:
        q (dict): Quarter financial data
        ticker (str): Stock ticker symbol
        period_end: Period end date
        yahoo: Yahoo Finance client instance
        model (str): Z-Score model to use
    
    Returns:
        dict: Processed quarter results
    """
    # Convert period_end to datetime.date
    if isinstance(period_end, str):
        try:
            period_end_dt = datetime.strptime(period_end, "%Y-%m-%d").date()
        except ValueError:
            # Try parsing with time component
            period_end_dt = datetime.strptime(period_end.split()[0], "%Y-%m-%d").date()
    else:
        period_end_dt = period_end
        
    # Get market value
    mve, actual_date = yahoo.get_market_cap_on_date(ticker, period_end_dt)
    if mve is None:
        mve = 0.0  # fallback to 0.0 if market cap is missing
        
    # Create metrics and validate
    metrics = FinancialMetrics.from_dict(q, mve, period_end_dt)
    validator = FinancialDataValidator()
    issues = validator.validate(q)
    diagnostic = validator.summarize_issues(issues)
    errors = [i.issue for i in issues if i.level.name == "ERROR"]
    
    if errors:
        return {
            "quarter_end": period_end,
            "zscore": None,
            "valid": False,
            "error": "; ".join(errors),
            "diagnostic": diagnostic
        }
        
    # Compute Z-Score
    if model == "private":
        metrics_dict = metrics.__dict__.copy()
        metrics_dict["book_value_equity"] = q.get("book_value_equity", mve)
        zscore_obj = compute_zscore(metrics_dict, model)
    else:
        zscore_obj = compute_zscore(metrics.__dict__, model)
        
    # Format results
    zscore_float = float(zscore_obj.z_score) if zscore_obj.z_score is not None else None
    zscore_str = f"{zscore_float:,.2f}" if zscore_float is not None else None
    
    return {
        "quarter_end": period_end,
        "zscore": zscore_float,
        "zscore_str": zscore_str,
        "valid": True,
        "error": None,
        "diagnostic": diagnostic,
        "model": str(model),
        "api_payload": q.get("raw_payload")
    }

def save_results_to_files(df: pd.DataFrame, ticker: str, out_base: str) -> None:
    """
    Save results to CSV, JSON, and summary files.
    
    Args:
        df (pd.DataFrame): Results dataframe
        ticker (str): Stock ticker symbol
        out_base (str): Output file base path
    """
    try:
        df.to_csv(f"{out_base}.csv", index=False)
        print_info(f"Results saved to CSV: {out_base}.csv")
    except Exception as e:
        print_error(f"Could not save CSV: {e}")
        
    try:
        df.to_json(f"{out_base}.json", orient="records", indent=2)
        print_info(f"Results saved to JSON: {out_base}.json")
    except Exception as e:
        print_error(f"Could not save JSON: {e}")
        
    # Only print warnings and errors
    for _, row in df.iterrows():
        if row.get("error"):
            print_warning(f"{row['quarter_end']}: {row['error']}")
            
    # Save summary table to file
    try:
        summary_table = df[["quarter_end", "zscore", "diagnostic", "model", "valid", "error", "api_payload"]].to_string(index=False)
        with open(f"{out_base}_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary_table)
    except Exception as e:
        print_error(f"Could not save summary table: {e}")

def create_profile_footnote(profile, model: str, sic_code: str = None) -> str:
    """
    Create profile footnote for chart.
    
    Args:
        profile: Company profile object
        model (str): Z-Score model used
        sic_code (str, optional): SIC code if available
    
    Returns:
        str: Profile footnote text
    """
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
    }
    maturity_desc = maturity_map.get(str(maturity).lower(), maturity) if maturity else 'Unknown'
    
    # Extract SIC code if not provided
    if not sic_code:
        sic_code = extract_sic_code(industry)
        
    # Get SIC description
    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    
    # Compose industry string for footnote
    if sic_code and sic_desc:
        industry_foot = f"{sic_desc} (SIC {sic_code})"
    elif sic_code:
        industry_foot = f"SIC {sic_code}"
    else:
        industry_foot = industry if industry else 'Unknown industry'
        
    return f"Industry: {industry_foot} | Maturity: {maturity_desc} | Public: {is_public} | Emerging Market: {is_em} | Model: {model}"

def move_diagnostic_files(ticker: str, ticker_dir: str) -> None:
    """
    Move diagnostic files to ticker directory.
    
    Args:
        ticker (str): Stock ticker symbol
        ticker_dir (str): Ticker directory path
    """
    diagnostic_files = [
        f"bs_columns_{ticker}.txt",
        f"bs_index_{ticker}.txt",
        f"is_columns_{ticker}.txt",
        f"yf_info_{ticker}.json"
    ]
    
    # Move diagnostic files and log the move in a file
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
                    print_warning(f"Could not move {fname}: {e}")

def analyze_single_stock_zscore_trend(ticker: str) -> pd.DataFrame:
    """
    Main entry for single-stock Z-Score trend analysis (MVP).

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
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

    # 1. Setup output directories
    output_dir, ticker_dir, out_base = create_output_directory(ticker)
    
    # 2. Classify company
    profile = classify_company(ticker)
    if not profile or getattr(profile, 'industry', None) in (None, '', 'unknown', 'Unknown'):
        error_msg = f"Could not classify company for ticker {ticker}. The ticker may not exist, may be delisted, or lacks industry/sector info."
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": error_msg,
            "diagnostic": None,
            "model": None,
            "api_payload": str(profile) if profile else None
        }]
        save_error_report(ticker, error_result, out_base)
        
        print_error(f"Could not classify company for ticker {Colors.BOLD}{ticker}{Colors.ENDC}.")
        print_error(f"Possible causes:")
        print_error(f" - The ticker symbol {ticker} may not exist")
        print_error(f" - The company may be delisted")
        print_error(f" - Industry/sector information is unavailable")
        print_error(f"Analysis aborted.")
        raise CompanyClassificationError(error_msg)
    
    # 3. Process company profile
    industry, is_public, is_em, maturity, out_base = process_company_profile(ticker, profile)
    
    # 4. Determine Z-Score model
    sic_code = extract_sic_code(industry)
    model_hint = determine_model_from_sic(sic_code, maturity)
    model = model_hint if model_hint else determine_zscore_model(profile)
    
    # 5. Fetch financial data
    fin_info = fetch_financials(ticker, "", model)
    if fin_info is None:
        error_msg = f"No financial data available for {ticker}. The company may be delisted, never public, or data is missing from yfinance/SEC."
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": error_msg,
            "diagnostic": None,
            "model": model,
            "api_payload": None
        }]
        save_error_report(ticker, error_result, out_base)
        
        print_error(f"No financial data available for {ticker}. Analysis cannot proceed.")
        print_warning(f"This may be due to: company not being listed, recent IPO, or missing data in sources.")
        raise FinancialDataError(error_msg)
    
    # 6. Filter and sort quarters
    valid_quarters = [q for q in fin_info["quarters"] if any(v not in (None, '', 0.0) for k, v in q.items() if k != 'raw_payload')]
    if not fin_info or not fin_info.get("quarters") or len(valid_quarters) == 0:
        raise ValueError(f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period.")

    quarters = list(reversed(valid_quarters))  # chronological order
    
    # 7. Process each quarter
    yahoo = YahooFinanceClient()
    results = []
    
    for q in quarters:
        period_end = q.get("period_end")
        try:
            result = process_quarter_data(q, ticker, period_end, yahoo, model)
            results.append(result)
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
    
    # 8. Format results and create DataFrame
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
    
    # 9. Save results to files
    save_results_to_files(df, ticker, out_base)
    
    # 10. Create chart
    footnote = create_profile_footnote(profile, model, sic_code)
    try:
        from altman_zscore.plotting import plot_zscore_trend
        plot_zscore_trend(df, ticker, model, out_base, profile_footnote=footnote)
    except ImportError:
        print_warning("matplotlib not installed, skipping plot.")
    except Exception as e:
        print_warning(f"Could not plot Z-Score trend: {e}")
    
    # 11. Move diagnostic files
    move_diagnostic_files(ticker, ticker_dir)
    
    return df
