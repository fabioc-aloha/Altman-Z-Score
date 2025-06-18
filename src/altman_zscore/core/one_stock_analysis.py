"""
Main pipeline orchestration for single-stock Altman Z-Score analysis.

This module coordinates the fetching, processing, and reporting of Z-Score trends
for a specified stock ticker, using the appropriate Z-Score model for the company's
profile.
"""

import json
import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.computation.compute import compute_zscore
from altman_zscore.data_fetching.financials import fetch_and_reconcile_financials
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.models.industry_classifier import classify_company
from altman_zscore.company.company_status_helpers import check_company_status, handle_special_status
from altman_zscore.models.factory import ModelRegistry
from altman_zscore.plotting.plotting_terminal import print_info, print_warning, print_error
from altman_zscore.models.financial_metrics import FinancialMetrics
from altman_zscore.validation.data_validation import FinancialDataValidator
from altman_zscore.data_fetching.prices import get_weekly_price_stats, save_price_data_to_disk

import logging

logger = logging.getLogger(__name__)

"""
One Stock Analysis Module for Altman Z-Score.
Currently limited to U.S.-based companies only.

This module serves as the main orchestrator for analyzing a single stock's Altman Z-Score.
It coordinates data fetching, validation, computation, and reporting by delegating to specialized modules.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional, Any

import pandas as pd
from dotenv import load_dotenv

from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.computation.compute import compute_zscore
from altman_zscore.data_fetching.financials import fetch_and_reconcile_financials
from altman_zscore.data_fetching.prices import get_weekly_price_stats
from altman_zscore.validation.data_validation import FinancialDataValidator
from altman_zscore.models.industry_classifier import classify_company
from altman_zscore.company.company_status_helpers import check_company_status, handle_special_status
from altman_zscore.company.company_profile import is_us_company
from altman_zscore.models.base import ZScoreModel  # Add ZScoreModel import

# Import core modules
from altman_zscore.core.progress_tracking import create_progress_tracker
from altman_zscore.core.output_generation import generate_llm_report, generate_chart, finalize_outputs
from altman_zscore.core.data_processing import prepare_context_info, filter_valid_quarters, extract_sic_code_from_industry
from altman_zscore.core.file_operations import get_zscore_path, save_results_to_disk, save_metadata_to_disk
from altman_zscore.core.reporting import report_zscore_full_report

# Import model modules
from altman_zscore.models.factory import ModelRegistry

# Import utility modules
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.utils.io import save_dataframe
from altman_zscore.plotting.plotting_main import plot_zscore_trend
from altman_zscore.plotting.plotting_terminal import print_info, print_warning, print_error
from altman_zscore.company.sic_lookup import sic_map


# ANSI color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_info(msg):
    logging.info(msg)


def print_success(msg):
    logging.info(msg)


def print_warning(msg):
    logging.warning(msg)


def print_error(msg):
    logging.error(msg)


def print_header(msg):
    logging.info(msg)


load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_zscore_path(ticker, ext=None):
    """
    Return the path for Z-Score output files in the ticker's directory.

    Args:
        ticker: Stock ticker symbol.
        ext: Optional file extension (e.g., 'csv', 'json').
    Returns:
        Path to the Z-Score output file as a string.
    Raises:
        ValueError: If the ticker is invalid or the extension is unsupported.
    """
    # Use the ticker directory as base, not a subdirectory called 'zscore'
    base = get_output_dir(None, ticker=ticker)
    return f"{os.path.join(base, f'zscore_{ticker}')}{ext if ext else ''}"


def check_company_status_and_handle(ticker: str):
    """
    Centralized company status check and special status handling.

    Args:
        ticker: Stock ticker symbol.
    Returns:
        Status object or value from check_company_status.
    Raises:
        ValueError: If the company has an invalid status that prevents analysis.
    """
    status = check_company_status(ticker)
    if handle_special_status(status):
        # Instead of sys.exit(), raise an exception to allow graceful handling
        raise ValueError(f"Cannot analyze {ticker}: Company status prevents analysis (invalid ticker, delisted, or non-U.S. company)")
    return status


def classify_and_prepare_output(ticker: str):
    """
    Classify company and prepare output directory.

    Args:
        ticker: Stock ticker symbol.
    Returns:
        Tuple of (profile, out_base) where profile is the classified company profile and out_base is the output base path.
    """
    # Fetch raw profile and normalize defaults
    raw_profile = classify_company(ticker) or {}
    # Normalize profile with default values for missing keys
    profile = {
        'industry': raw_profile.get('industry', 'Unknown'),
        'sector': raw_profile.get('sector', 'Unknown'),
        'is_public': raw_profile.get('is_public', True)
    }
    logger.debug(f"Company profile for {ticker}: {profile}")
    # Prepare output base path
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")
    # Always return a valid profile dict; no early abort
    return profile, out_base


def filter_valid_quarters(fin_info, start_date: str):
    """
    Filter valid quarters based on financial info and start date.

    Args:
        fin_info: Dictionary with a 'quarters' key containing a list of quarter dicts.
        start_date: Start date in 'YYYY-MM-DD' format. Only quarters ending on or after this date are included.
    Returns:
        List of valid quarter dicts.
    """
    valid_quarters = [
        q for q in fin_info["quarters"] if any(v not in (None, "", 0.0) for k, v in q.items() if k != "raw_payload")
    ]
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            valid_quarters = [
                q
                for q in valid_quarters
                if "period_end" in q
                and q["period_end"]
                and datetime.strptime(str(q["period_end"])[:10], "%Y-%m-%d").date() >= start_dt
            ]
        except (ValueError, KeyError) as e:
            print_warning(f"Could not filter quarters by start_date: {e}")
    return valid_quarters


def _extract_sic_code_from_industry(industry):
    """
    Extract SIC code from industry string if present.

    Args:
        industry: Industry string (may contain 'SIC <digits>').
    Returns:
        SIC code as string if found, else None.
    """
    if industry and "SIC" in str(industry):
        parts = str(industry).split()
        for i, p in enumerate(parts):
            if p == "SIC" and i + 1 < len(parts):
                return parts[i + 1]
    return None


def _select_zscore_model_from_profile(profile) -> 'ZScoreModel':
    """Select appropriate Z-Score model based on company profile or profile dict.
    
    Args:
        profile: CompanyProfile instance or dict with keys 'industry' and 'is_public'
    Returns:
        ZScoreModel instance appropriate for the company
    """
    # Extract industry and public status from profile
    if isinstance(profile, dict):
        industry = profile.get('industry', '')
        is_public = profile.get('is_public', True)
    else:
        industry = getattr(profile, 'industry', '')
        is_public = getattr(profile, 'is_public', True)
    # Extract SIC code from industry string and convert to int if valid
    sic_str = extract_sic_code_from_industry(industry)
    sic_code = int(sic_str) if isinstance(sic_str, str) and sic_str.isdigit() else None
    # Select model type key
    from altman_zscore.computation.model_selection import select_zscore_model
    model_type_key = select_zscore_model(sic_code, is_public)
    # Create enum from key and instantiate model
    from altman_zscore.models.base import ModelType
    try:
        model_type_enum = ModelType(model_type_key.lower())
    except Exception:
        # fallback for legacy keys
        key = model_type_key.lower()
        if key == 'zeta':
            model_type_enum = ModelType.ZETA
        elif key == 'retail':
            model_type_enum = ModelType.RETAIL
        elif key == 'financial':
            model_type_enum = ModelType.FINANCIAL
        elif key == 'private':
            model_type_enum = ModelType.PRIVATE
        else:
            model_type_enum = ModelType.ORIGINAL
    return ModelRegistry.create_model(model_type_enum)


def _fetch_and_validate_financials(ticker: str, model: str, start_date: str, out_base: str):
    """
    Fetch and validate financials for a given ticker and model.

    Args:
        ticker: Stock ticker symbol.
        model: Z-Score model type.
        start_date: Analysis start date.
        out_base: Base output path.
    Returns:
        Tuple of (fin_info, valid_quarters).
    """
    # Use LLM-based reconciliation instead of legacy fetch
    logger = logging.getLogger("altman_zscore.one_stock_analysis")
    
    fin_info = fetch_and_reconcile_financials(ticker, datetime.now().strftime("%Y-%m-%d"), model, start_date)
    
    if fin_info is None or (isinstance(fin_info, dict) and not fin_info.get("quarters")):
        error_result = [{
            "quarter_end": None,
            "zscore": None,
            "valid": False,
            "error": f"No financial data available for {ticker}. The company may be delisted, never public, or data is missing from yfinance/SEC.",
            "diagnostic": None,
            "model": model,
            "api_payload": None,
        }]
        df = pd.DataFrame(error_result)
        _save_results_to_disk(df, out_base, error=True)
        print_error(f"No financial data available for {ticker}. Analysis cannot proceed.")
        print_warning(f"This may be due to: company not being listed, recent IPO, or missing data in sources.")
        raise ValueError(f"No financial data available for {ticker}. Analysis cannot proceed.")
        
    # Get all valid quarters that fall within the date range
    valid_quarters = []
    if fin_info and "quarters" in fin_info:
        quarters = fin_info["quarters"]
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                quarters = [
                    q for q in quarters
                    if "period_end" in q 
                    and q["period_end"] 
                    and datetime.strptime(str(q["period_end"])[:10], "%Y-%m-%d").date() >= start_dt
                ]
            except (ValueError, KeyError) as e:
                logger.warning(f"Could not filter quarters by start_date: {e}")
        valid_quarters = list(reversed(quarters))  # Most recent first
        
    if len(valid_quarters) == 0:
        raise ValueError(
            f"No usable financial data found for ticker '{ticker}' from {start_date} onwards. The company may not exist or was not listed in the requested period."
        )
        
    return fin_info, valid_quarters


def _process_quarters_and_compute_zscores(quarters, ticker, model, raw_quarters=None):
    """
    Compute Altman Z-Scores and perform validation for each quarter in the input list.

    For each quarter, this function:
    - Checks if all required financial fields are present and nonzero. If not, marks the quarter as invalid and records a diagnostic error.
    - Fetches market value of equity for the period end date using Yahoo Finance.
    - Constructs financial metrics and validates the data, collecting any validation or consistency issues.
    - Computes the Z-Score using the selected model if data is sufficient.
    - Appends a result dict for each quarter, including Z-Score, diagnostics, and any errors or warnings.

    Args:
        quarters (list[dict]): List of quarter financial data dicts.
        ticker (str): Stock ticker symbol.
        model (str): Z-Score model name (e.g., 'public', 'private').
        raw_quarters (list[dict], optional): Original raw quarters data for reference (optional).

    Returns:
        pandas.DataFrame: DataFrame with Z-Score results, diagnostics, and error/warning columns for each quarter.
        If a quarter is missing all required fields, the result will indicate calculation was not possible for that quarter.
    """
    yahoo = YahooFinanceClient()
    results = []
    REQUIRED_FIELDS = [
        "current_assets", "current_liabilities", "retained_earnings", "ebit", "market_value_equity", "total_assets", "total_liabilities", "sales"
    ]

    # Sort quarters by date first to ensure chronological order
    quarters = sorted(quarters, key=lambda x: x["period_end"])
    
    for q in quarters:
        period_end = q["period_end"] if isinstance(q, dict) and "period_end" in q else None
        # --- PATCH: skip/report empty quarters ---
        if not any(q.get(field) not in (None, "", 0.0) for field in REQUIRED_FIELDS):
            results.append({
                "quarter_end": period_end,
                "zscore": None,
                "valid": False,
                "error": "No usable financial data for this quarter. All required fields are missing or zero.",
                "diagnostic": "[ERROR] All required fields missing or zero.",
                "model": str(model),
                "api_payload": q.get("raw_payload") if isinstance(q, dict) else getattr(q, "raw_payload", None),
            })
            continue
        try:
            if isinstance(period_end, str):
                try:
                    period_end_dt = datetime.strptime(period_end, "%Y-%m-%d").date()
                except ValueError:
                    period_end_dt = datetime.strptime(period_end.split()[0], "%Y-%m-%d").date()
            else:
                period_end_dt = period_end
                
            # Fetch market value for the quarter
            mve, actual_date = yahoo.get_market_cap_on_date(ticker, period_end_dt)
            if mve is None:
                mve = 0.0
                
            # Prepare metrics for Z-Score calculation
            metrics = {
                "current_assets": float(q.get("current_assets", 0)),
                "current_liabilities": float(q.get("current_liabilities", 0)),
                "total_assets": float(q.get("total_assets", 0)),
                "total_liabilities": float(q.get("total_liabilities", 0)),
                "retained_earnings": float(q.get("retained_earnings", 0)),
                "ebit": float(q.get("ebit", 0)),
                "market_value_equity": float(mve),
                "sales": float(q.get("sales", 0))
            }
            
            # Validate the data
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
                    "diagnostic": diagnostic,
                    "model": str(model),
                    "api_payload": q.get("raw_payload") if isinstance(q, dict) else getattr(q, "raw_payload", None),
                })
            else:
                # Compute Z-Score using the computation module
                result = compute_zscore(metrics, model_key=model)
                
                if result.z_score is not None:
                    results.append({
                        "quarter_end": period_end,
                        "zscore": result.z_score,
                        "valid": True,
                        "error": None,
                        "diagnostic": result.diagnostic,
                        "model": str(model),
                        "api_payload": q.get("raw_payload") if isinstance(q, dict) else getattr(q, "raw_payload", None),
                    })
                else:
                    results.append({
                        "quarter_end": period_end,
                        "zscore": None,
                        "valid": False,
                        "error": "Z-Score computation failed",
                        "diagnostic": diagnostic,
                        "model": str(model),
                        "api_payload": q.get("raw_payload") if isinstance(q, dict) else getattr(q, "raw_payload", None),
                    })
        except Exception as e:
            # Log useful debug info but don't expose sensitive details in user-facing error
            logger.debug(f"Error processing quarter {period_end}: {str(e)}")
            results.append({
                "quarter_end": period_end,
                "zscore": None,
                "valid": False,
                "error": f"Failed to process quarter: {e.__class__.__name__}",
                "diagnostic": f"[ERROR] {str(e)}",
                "model": str(model),
                "api_payload": q.get("raw_payload") if isinstance(q, dict) else getattr(q, "raw_payload", None),
            })

    return pd.DataFrame(results)


def _save_results_to_disk(df, out_base, error=False):
    """
    Save analysis results to CSV and JSON.

    Args:
        df: DataFrame with analysis results.
        out_base: Base output path.
        error: Whether this is an error result (adds '_error' to filenames).
    Returns:
        None. Files are saved to disk.
    """
    suffix = "_error" if error else ""
    csv_path = f"{out_base}{suffix}.csv"
    json_path = f"{out_base}{suffix}.json"
    try:
        save_dataframe(df, csv_path, fmt="csv")
        print_info(f"Results saved to CSV: {csv_path}")
    except Exception as e:
        print_error(f"Could not save CSV: {e}")
    try:
        save_dataframe(df, json_path, fmt="json")
        print_info(f"Results saved to JSON: {json_path}")
    except Exception as e:
        print_error(f"Could not save JSON: {e}")


def _fetch_and_save_weekly_prices(ticker, df, out_base, start_date=None):
    """
    Fetch and save weekly price stats for the specified historical range (from start_date onward).

    Args:
        ticker: Stock ticker symbol.
        df: DataFrame with Z-Score results.
        out_base: Base output path.
        start_date: Optional start date (YYYY-MM-DD) to restrict price data.
    Returns:
        DataFrame with weekly price statistics, or None on error.
    """
    stock_prices = None
    weekly_stats = None
    try:
        import yfinance as yf
        # Get the full available date range for the ticker
        yf_ticker = yf.Ticker(ticker)
        hist = yf_ticker.history(period="max")
        if hist is None or hist.empty:
            raise ValueError(f"No historical price data found for {ticker}")
        # Use the provided start_date if given, else use the earliest available
        if start_date:
            try:
                # Ensure start_date is not before the available data
                min_date = hist.index.min().strftime("%Y-%m-%d")
                start_date_effective = max(start_date, min_date)
            except Exception:
                start_date_effective = start_date
        else:
            start_date_effective = hist.index.min().strftime("%Y-%m-%d")
        end_date = hist.index.max().strftime("%Y-%m-%d")
        weekly_stats = get_weekly_price_stats(ticker, start_date_effective, end_date)
        stock_prices = weekly_stats
        try:
            from altman_zscore.data_fetching.prices import save_price_data_to_disk
            if not weekly_stats.empty:
                csv_path, json_path = save_price_data_to_disk(weekly_stats, ticker, "weekly_prices")
                print_info(
                    f"Weekly price statistics saved to {os.path.basename(csv_path)} and {os.path.basename(json_path)}"
                )
        except (ImportError, AttributeError):
            print_warning("Price data saving to disk is not available or failed")
    except Exception as e:
        logger.warning(f"Could not fetch stock prices for overlay: {e}")
    return stock_prices


def _prepare_context_info(ticker, profile, model, sic_code):
    """
    Prepare context info dict for reporting.

    Args:
        ticker: Stock ticker symbol.
        profile: Company profile object.
        model: Z-Score model name.
        sic_code: SIC code string.
    Returns:
        Dictionary with context fields for reporting.
    """
    industry = getattr(profile, "industry", "Unknown")
    is_public = getattr(profile, "is_public", "Unknown")
    maturity = getattr(profile, "maturity", None)
    maturity_map = {
        "early": "Early Stage",
        "growth": "Growth Stage",
        "mature": "Mature Company",
        "private": "Private Company",
        "public": "Public Company",
    }

    sic_desc = sic_map.get(str(sic_code)) if sic_code else None
    if sic_desc:
        industry_for_context = sic_desc
    elif sic_code:
        industry_for_context = f"SIC {sic_code}"
    else:
        industry_for_context = industry
    return {
        "Ticker": ticker,
        "Industry": industry_for_context,
        "Public": is_public,
        "Maturity": (
            maturity_map.get(str(maturity).lower(), "Mature Company")
            if maturity
            else ("Mature Company" if str(is_public).lower() == "true" else "Unknown")
        ),
        "Model": model,
        "SIC Code": sic_code or "N/A",
        "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
    }


def analyze_single_stock_zscore_trend(ticker: str, start_date: str = "2024-01-01", 
                            progress_callback=None, force_model: str = None) -> pd.DataFrame:
    """
    Analyze a single stock's Altman Z-Score trend with optional progress tracking.

    This function orchestrates the full pipeline for a single ticker, including input validation, 
    data fetching, validation, computation, reporting, and output generation. Progress can be 
    tracked via an optional callback.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date for analysis in YYYY-MM-DD format.
        progress_callback: Optional function to call with progress updates.
                         Should accept (step_name: str, step_index: int, total_steps: int).
        force_model: Optional model type to force instead of using automatic selection.
                    Values: 'original', 'private', 'emerging', 'financial', 'zeta', 'retail'
    Returns:
        DataFrame with Z-Score analysis results.
    
    Raises:
        ValueError: If the ticker cannot be analyzed due to invalid status, missing data, or other issues.
    """
    logger = logging.getLogger("altman_zscore.one_stock_analysis")
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")
    
    # Create progress tracker or get update function and total steps
    tracker = create_progress_tracker(progress_callback)
    if isinstance(tracker, tuple):
        update_progress, total_steps = tracker
    else:
        update_progress = tracker.update
        total_steps = tracker.total_steps
    
    try:
        # Step 1: Input Validation
        update_progress("Input Validation")
        check_company_status_and_handle(ticker)
        
        # Step 2: Fetch Company Profile
        update_progress("Fetch Company Profile")
        profile, out_base = classify_and_prepare_output(ticker)
        
        # Handle model selection - either forced or automatic
        current_model = None  # Will store the model name
        if force_model:
            from ..models.base import ModelType
            from ..models.model_validation import validate_model_appropriateness
            
            try:
                model_type = ModelType(force_model)
                
                # Validate model appropriateness
                is_appropriate, warning_level, message = validate_model_appropriateness(profile, model_type)
                
                if warning_level == 'warning':
                    logger.warning(f"WARNING: {message}")
                elif warning_level == 'caution':
                    logger.info(f"CAUTION: {message}")
                if not is_appropriate:
                    logger.warning("Consider using automatic model selection instead: python main.py %s", ticker)
                
                logger.info(f"Proceeding with forced model type: {force_model}")
                model = ModelRegistry.create_model(model_type)
                current_model = force_model  # Store model name
                
            except ValueError:
                logger.warning(f"Invalid model type '{force_model}', falling back to automatic selection")
                model = _select_zscore_model_from_profile(profile)
                current_model = model.get_model_type().value if hasattr(model, 'get_model_type') else 'original'
        else:
            model = _select_zscore_model_from_profile(profile)
            current_model = model.get_model_type().value if hasattr(model, 'get_model_type') else 'original'
        
        # Step 3: Fetch Financials (SEC)
        update_progress("Fetch Financials (SEC)")
        fin_info, quarters = _fetch_and_validate_financials(ticker, current_model, start_date, out_base)
        raw_quarters = fin_info["quarters"] if fin_info and "quarters" in fin_info else None

        if not fin_info or not quarters:
            error_msg = f"No financial data available for {ticker}. This may indicate the company is delisted, not publicly traded, or has insufficient SEC filings."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 4: Z-Score Computation
        update_progress("Z-Score Computation")
        df = _process_quarters_and_compute_zscores(quarters, ticker, current_model, raw_quarters=raw_quarters)
        
        # Check if Z-Score computation was successful
        if df is None or df.empty:
            error_msg = f"Z-Score calculation failed for {ticker}. Insufficient or invalid financial data."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if any valid Z-Scores were calculated
        valid_scores = df[df['zscore'].notnull()] if 'zscore' in df.columns else pd.DataFrame()
        if valid_scores.empty:
            error_msg = f"No valid Z-Scores could be calculated for {ticker}. Financial data may be incomplete or corrupted."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 5: Raw Data Output (CSV/JSON)
        update_progress("Raw Data Output (CSV/JSON)")
        _save_results_to_disk(df, out_base)
        for _, row in df.iterrows():
            if isinstance(row, dict):
                has_error = row.get("error")
            else:
                has_error = getattr(row, "error", None)
            if has_error:
                print_warning(f"{row['quarter_end']}: {row['error']}")

        # Step 6: Fetch Market Data (Prices, Splits, Dividends)
        update_progress("Fetch Market Data (Prices, Splits, Dividends)")
        try:
            stock_prices = _fetch_and_save_weekly_prices(ticker, df, out_base, start_date=start_date)
        except Exception as e:
            logger.warning(f"Failed to fetch market data for {ticker}: {e}")
            stock_prices = pd.DataFrame()  # Continue with empty DataFrame

        # Step 7: LLM Prompt Construction
        update_progress("LLM Prompt Construction")
        context_info = prepare_context_info(ticker, profile, model)
        # Add additional context information if available
        if "raw_quarters" in locals():
            context_info["raw_quarters"] = raw_quarters
        if "quarters" in locals():
            context_info["quarters"] = quarters
        context_info["weekly_prices"] = stock_prices        
        
        # Step 8: LLM Report Generation
        update_progress("LLM Report Generation")
        try:
            llm_report = generate_llm_report(df, model, out_base, context_info, ticker, stock_prices)
        except Exception as e:
            logger.warning(f"LLM report generation failed for {ticker}: {e}")
            llm_report = None

        # Step 9: Chart Generation
        update_progress("Chart Generation")
        try:
            chart_path = generate_chart(df, model, out_base, ticker, stock_prices)
        except Exception as e:
            logger.warning(f"Chart generation failed for {ticker}: {e}")
            chart_path = None

        # Step 10: Final File Output
        update_progress("Final File Output")
        try:
            finalize_outputs(df, model, out_base, context_info, ticker, stock_prices, llm_report, chart_path)
        except Exception as e:
            logger.warning(f"Final output generation failed for {ticker}: {e}")

        return df
        
    except ValueError as ve:
        # Re-raise ValueError with original message for graceful handling by main()
        raise ve
    except Exception as e:
        # Convert other exceptions to ValueError for consistent error handling
        error_msg = f"Unexpected error analyzing {ticker}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
