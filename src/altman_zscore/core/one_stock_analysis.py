"""
One Stock Analysis Module for Altman Z-Score.

This module serves as the main orchestrator for analyzing a single stock's Altman Z-Score. It coordinates data fetching, validation, computation, and reporting by delegating to specialized modules. All functions are designed for modular use, robust error handling, and progress tracking.
"""

import json
import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from altman_zscore.api.yahoo_client import YahooFinanceClient
from altman_zscore.computation.compute_zscore import compute_zscore
from altman_zscore.data_fetching.financials import fetch_financials
from altman_zscore.data_fetching.prices import get_weekly_price_stats
from altman_zscore.validation.data_validation import FinancialDataValidator
from altman_zscore.models.industry_classifier import classify_company
from altman_zscore.models.financial_metrics import FinancialMetrics
from altman_zscore.computation.model_selection import select_zscore_model
from altman_zscore.company.company_status_helpers import check_company_status, handle_special_status

# Import core modules
from altman_zscore.core.progress_tracking import create_progress_tracker, PIPELINE_STEPS
from altman_zscore.core.output_generation import generate_llm_report, generate_chart, finalize_outputs
from altman_zscore.core.data_processing import prepare_context_info, filter_valid_quarters, extract_sic_code_from_industry
from altman_zscore.core.file_operations import get_zscore_path, save_results_to_disk, save_metadata_to_disk
from altman_zscore.core.reporting import report_zscore_full_report

# Import utility modules
from altman_zscore.utils.paths import get_output_dir
from altman_zscore.utils.io import save_dataframe
from altman_zscore.plotting.plotting_main import plot_zscore_trend
from altman_zscore.plotting.plotting_terminal import print_info, print_warning, print_error
from altman_zscore.company.sic_lookup import sic_map
from altman_zscore.utils.logging import setup_logging


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
    """
    status = check_company_status(ticker)
    if handle_special_status(status):
        import sys
        sys.exit(1)
    return status


def classify_and_prepare_output(ticker: str):
    """
    Classify company and prepare output directory.

    Args:
        ticker: Stock ticker symbol.
    Returns:
        Tuple of (profile, out_base) where profile is the classified company profile and out_base is the output base path.
    """
    profile = classify_company(ticker)
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")
    if not profile or getattr(profile, "industry", None) in (None, "", "unknown", "Unknown"):
        print_error(f"Could not classify company for ticker {ticker}. Analysis aborted.")
        sys.exit(1)
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


def _select_zscore_model_from_profile(profile):
    """
    Select Z-Score model using profile fields and SIC code.

    Args:
        profile: Company profile object.
    Returns:
        Tuple of (model, sic_code).
    """
    industry = getattr(profile, "industry", "Unknown")
    is_public = getattr(profile, "is_public", "Unknown")
    maturity = getattr(profile, "maturity", None)
    sic_code = _extract_sic_code_from_industry(industry)
    maturity_str = str(maturity) if maturity is not None else ""
    is_emerging = (maturity_str == "emerging") if maturity_str else False
    model = select_zscore_model(
        int(sic_code) if sic_code else None,
        (str(is_public).lower() == "true"),
        is_emerging
    )
    return model, sic_code


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
    fin_info = fetch_financials(ticker, "", model)
    if fin_info is None:
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
        sys.exit(1)
    valid_quarters = filter_valid_quarters(fin_info, start_date)
    if not fin_info or not fin_info.get("quarters") or len(valid_quarters) == 0:
        raise ValueError(
            f"No usable financial data found for ticker '{ticker}'. The company may not exist or was not listed in the requested period."
        )
    return fin_info, list(reversed(valid_quarters))


def _process_quarters_and_compute_zscores(quarters, ticker, model, raw_quarters=None):
    """
    Compute Z-Scores and validation for each quarter. Attach raw_quarters if provided.

    Args:
        quarters: List of quarter dicts.
        ticker: Stock ticker symbol.
        model: Z-Score model name.
        raw_quarters: Optional, original raw quarters data.
    Returns:
        DataFrame with Z-Score results and diagnostics.
    """
    yahoo = YahooFinanceClient()
    results = []
    for q in quarters:
        period_end = q.get("period_end")
        try:
            if isinstance(period_end, str):
                try:
                    period_end_dt = datetime.strptime(period_end, "%Y-%m-%d").date()
                except ValueError:
                    period_end_dt = datetime.strptime(period_end.split()[0], "%Y-%m-%d").date()
            else:
                period_end_dt = period_end
            mve, actual_date = yahoo.get_market_cap_on_date(ticker, period_end_dt)
            if mve is None:
                mve = 0.0
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
                    "diagnostic": None,
                    "validation_summary": diagnostic,
                })
                continue
            consistency_issues = validator.check_consistency(q)
            consistency_summary = validator.summarize_issues(consistency_issues)
            if consistency_issues:
                print_warning(f"Quarter {period_end}: CONSISTENCY WARNING: {consistency_summary}")
            if model == "private":
                metrics_dict = metrics.__dict__.copy()
                metrics_dict["book_value_equity"] = q.get("book_value_equity", mve)
                zscore_obj = compute_zscore(metrics_dict, model)
            else:
                zscore_obj = compute_zscore(metrics.__dict__, model)
            zscore_float = float(zscore_obj.z_score) if zscore_obj.z_score is not None else None
            zscore_str = f"{zscore_float:,.2f}" if zscore_float is not None else None
            results.append({
                "quarter_end": period_end,
                "zscore": zscore_float,
                "zscore_str": zscore_str,
                "components": zscore_obj.components,
                "valid": True,
                "error": None,
                "diagnostic": zscore_obj.diagnostic,
                "validation_summary": diagnostic,
                "consistency_warning": consistency_summary if consistency_issues else None,
                "model": str(model),
                "api_payload": q.get("raw_payload"),
                "field_mapping": q.get("field_mapping"),
            })
        except Exception as e:
            logger = logging.getLogger("altman_zscore.one_stock_analysis")
            logger.error(f"Error processing quarter {period_end} for {ticker}: {e}")
            results.append({
                "quarter_end": period_end,
                "zscore": None,
                "valid": False,
                "error": str(e),
                "diagnostic": f"[ERROR] Exception: {e}",
                "model": str(model),
                "api_payload": q.get("raw_payload"),
            })
    def safe_payload(val):
        if isinstance(val, (dict, list)):
            try:
                return json.dumps(val)
            except Exception:
                return str(val)
        return val
    for r in results:
        if "api_payload" in r:
            r["api_payload"] = safe_payload(r["api_payload"])
    df = pd.DataFrame(results)
    # Do NOT assign custom attributes to DataFrame
    return df


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


def _fetch_and_save_weekly_prices(ticker, df, out_base):
    """
    Fetch and save weekly price stats for the Z-Score period.

    Args:
        ticker: Stock ticker symbol.
        df: DataFrame with Z-Score results.
        out_base: Base output path.
    Returns:
        DataFrame with weekly price statistics, or None on error.
    """
    stock_prices = None
    weekly_stats = None
    try:
        quarters = pd.to_datetime(df["quarter_end"])
        start_date = quarters.min().strftime("%Y-%m-%d")
        from datetime import timedelta
        financial_end_date = quarters.max()
        extended_end_date = financial_end_date + timedelta(days=60)
        end_date = extended_end_date.strftime("%Y-%m-%d")
        weekly_stats = get_weekly_price_stats(ticker, start_date, end_date)
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
        print(f"[WARN] Could not fetch stock prices for overlay: {e}")
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
    is_em = getattr(profile, "is_emerging_market", "Unknown")
    maturity = getattr(profile, "maturity", None)
    maturity_map = {
        "early": "Early Stage",
        "growth": "Growth Stage",
        "mature": "Mature Company",
        "emerging": "Emerging Market",
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
        "Emerging Market": is_em,
        "Maturity": (
            maturity_map.get(str(maturity).lower(), "Mature Company")
            if maturity
            else ("Mature Company" if str(is_public).lower() == "true" else "Unknown")
        ),
        "Model": model,
        "SIC Code": sic_code or "N/A",
        "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
    }


def _generate_report_and_plot(df, model, out_base, context_info, ticker, stock_prices):
    """
    Generate the full Z-Score report and plot for a given analysis run.

    Args:
        df: DataFrame with Z-Score results.
        model: Z-Score model name.
        out_base: Base output path.
        context_info: Dictionary with context fields for reporting.
        ticker: Stock ticker symbol.
        stock_prices: DataFrame with weekly price statistics.
    Returns:
        None. Outputs are saved to disk.
    """
    try:
        # Explicitly sanitize the context_info before passing it to the report generator
        # This prevents DataFrame truthiness errors
        sanitized_context = {k: v for k, v in context_info.items()}
        
        if "weekly_prices" in sanitized_context and isinstance(sanitized_context["weekly_prices"], pd.DataFrame):
            sanitized_context["weekly_prices"] = sanitized_context["weekly_prices"].to_dict(orient="records")
            
        if "raw_quarters" in sanitized_context and isinstance(sanitized_context["raw_quarters"], pd.DataFrame):
            sanitized_context["raw_quarters"] = sanitized_context["raw_quarters"].to_dict(orient="records")
        
        # Generate the report with sanitized context
        report_zscore_full_report(df, model, out_base, print_to_console=True, context_info=sanitized_context)

        # Notify user of report location
        ticker_upper = str(ticker).upper() if ticker else ""
        if ticker_upper and out_base:
            from altman_zscore.utils.paths import get_output_dir
            import os
            if not out_base.startswith(f"{ticker_upper}/") and not out_base.startswith(f"{ticker_upper}\\"):
                out_base_path = os.path.join(ticker_upper, out_base)
            else:
                out_base_path = out_base
            report_path = get_output_dir(relative_path=f"{out_base_path}_zscore_full_report.md")
            if os.path.exists(report_path):
                print_info(f"Full Z-Score report (with LLM commentary) saved to {report_path}")
            else:
                print_warning(f"Expected report file {report_path} not found after generation.")
    except Exception as e:
        print_warning(f"Could not generate full Z-Score report: {e}")
        
    # Plot the Z-Score trend
    try:
        print_info("Generating Z-Score trend plot...")
        plot_zscore_trend(df, ticker, model, out_base, stock_prices=stock_prices)
    except ImportError:
        print_warning("matplotlib not installed, skipping plot.")
    except Exception as e:
        print_warning(f"Could not plot Z-Score trend: {e}")


def analyze_single_stock_zscore_trend(ticker: str, start_date: str = "2024-01-01", progress_callback=None) -> pd.DataFrame:
    """
    Analyze a single stock's Altman Z-Score trend with optional progress tracking.

    This function orchestrates the full pipeline for a single ticker, including input validation, data fetching, validation, computation, reporting, and output generation. Progress can be tracked via an optional callback.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date for analysis in YYYY-MM-DD format.
        progress_callback: Optional function to call with progress updates. Should accept (step_name: str, step_index: int, total_steps: int).
    Returns:
        DataFrame with Z-Score analysis results.
    """
    logger = logging.getLogger("altman_zscore.one_stock_analysis")
    out_base = os.path.join(get_output_dir(None, ticker=ticker), f"zscore_{ticker}")
    
    # Create progress tracker
    update_progress, total_steps = create_progress_tracker(progress_callback)
    
    # Step 1: Input Validation
    update_progress("Input Validation")
    check_company_status_and_handle(ticker)
    
    # Step 2: Fetch Company Profile 
    update_progress("Fetch Company Profile")
    profile, out_base = classify_and_prepare_output(ticker)
    model, sic_code = _select_zscore_model_from_profile(profile)
    
    # Step 3: Fetch Financials (Yahoo/SEC)
    update_progress("Fetch Financials (Yahoo/SEC)")
    fin_info, quarters = _fetch_and_validate_financials(ticker, model, start_date, out_base)
    raw_quarters = fin_info.get("quarters") if fin_info else None
    
    # Step 4: Fetch Market Data (Prices, Splits, Dividends)
    update_progress("Fetch Market Data (Prices, Splits, Dividends)")
    # This step happens within _fetch_and_save_weekly_prices later, but we track it here
    
    # Step 5: Fetch Analyst Recommendations
    update_progress("Fetch Analyst Recommendations")
    # This step happens within other data fetching functions, tracked here for progress
    
    # Step 6: Fetch Executive/Officer Data
    update_progress("Fetch Executive/Officer Data")
    # This step happens within profile classification, tracked here for progress
    
    # Step 7: Data Validation
    update_progress("Data Validation")
    # (Assume validation is performed here or in previous steps)

    # Step 8: Z-Score Computation
    update_progress("Z-Score Computation")
    df = _process_quarters_and_compute_zscores(quarters, ticker, model, raw_quarters=raw_quarters)

    # Step 9: Raw Data Output (CSV/JSON)
    update_progress("Raw Data Output (CSV/JSON)")
    _save_results_to_disk(df, out_base)
    for _, row in df.iterrows():
        if row.get("error"):
            print_warning(f"{row['quarter_end']}: {row['error']}")

    # Fetch weekly prices (part of Market Data step tracked earlier)
    stock_prices = _fetch_and_save_weekly_prices(ticker, df, out_base)

    # Step 10: LLM Prompt Construction
    update_progress("LLM Prompt Construction")
    context_info = _prepare_context_info(ticker, profile, model, sic_code)
    context_info["raw_quarters"] = raw_quarters if raw_quarters is not None else quarters
    context_info["weekly_prices"] = stock_prices

    # Step 11: LLM Report Generation
    update_progress("LLM Report Generation")
    # Split _generate_report_and_plot for granularity
    llm_report = _generate_llm_report(df, model, out_base, context_info, ticker, stock_prices)

    # Step 12: Chart Generation
    update_progress("Chart Generation")
    chart_path = _generate_chart(df, model, out_base, context_info, ticker, stock_prices)

    # Step 13: Final File Output
    update_progress("Final File Output")
    _finalize_outputs(df, model, out_base, context_info, ticker, stock_prices, llm_report, chart_path)

    return df

# Helper functions for split steps (implementations wrap the original logic)
def _generate_llm_report(df, model, out_base, context_info, ticker, stock_prices):
    """Generate the LLM-based analysis report."""
    try:
        # Explicitly sanitize the context_info before passing it to the report generator
        sanitized_context = {k: v for k, v in context_info.items()}
        
        if "weekly_prices" in sanitized_context and isinstance(sanitized_context["weekly_prices"], pd.DataFrame):
            sanitized_context["weekly_prices"] = sanitized_context["weekly_prices"].to_dict(orient="records")
            
        if "raw_quarters" in sanitized_context and isinstance(sanitized_context["raw_quarters"], pd.DataFrame):
            sanitized_context["raw_quarters"] = sanitized_context["raw_quarters"].to_dict(orient="records")
        
        # Generate just the report portion
        report = report_zscore_full_report(            
            df, 
            model, 
            out_base, 
            context_info=sanitized_context,
            print_to_console=True
        )
        return report
    except Exception as e:
        print_warning(f"Could not generate full Z-Score report: {e}")
        return None

def _generate_chart(df, model, out_base, context_info, ticker, stock_prices):
    """Generate the Z-Score trend plot chart."""
    try:
        print_info("Generating Z-Score trend plot...")
        chart_path = os.path.join(os.path.dirname(out_base), f"zscore_{ticker}_trend.png")
        plot_zscore_trend(
            df, 
            ticker, 
            model, 
            chart_path, 
            stock_prices=stock_prices
        )
        return chart_path
    except ImportError:
        print_warning("matplotlib not installed, skipping plot.")
        return None
    except Exception as e:
        print_warning(f"Could not plot Z-Score trend: {e}")
        return None

def _finalize_outputs(df, model, out_base, context_info, ticker, stock_prices, llm_report, chart_path):
    """Save all final outputs to disk."""
    try:
        # Save the LLM report if we have one
        if llm_report:
            report_path = f"{out_base}_zscore_full_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(llm_report)
            abs_report_path = os.path.abspath(report_path)
            print_info(f"Full Z-Score report (with LLM commentary) saved to {abs_report_path}")
        
        # Verify chart was generated
        if chart_path and os.path.exists(chart_path):
            print_info(f"Z-Score trend plot saved to {os.path.basename(chart_path)}")
        
        # Save any additional metadata or context info
        metadata = {
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "ticker": ticker,
            "model": str(model),
            "context": context_info
        }
        metadata_path = f"{out_base}_metadata.json"
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            print_warning(f"Could not save analysis metadata: {e}")
            
    except Exception as e:
        print_warning(f"Error in finalizing outputs: {e}")
        
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Run Altman Z-Score analysis for a single stock.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., MSFT)")
    parser.add_argument("--start_date", type=str, default="2024-01-01", help="Start date for analysis (YYYY-MM-DD)")
    args = parser.parse_args()
    analyze_single_stock_zscore_trend(args.ticker, args.start_date)
