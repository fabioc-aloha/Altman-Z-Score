"""
Report generation and output handling for Altman Z-Score analysis.

This module provides functions to generate LLM-based reports, create Z-Score trend charts, and finalize output files for a given analysis run. All functions are designed for robust error handling and modular use in the main pipeline.
"""

import json
import logging
import os
from datetime import datetime
import pandas as pd

from altman_zscore.plotting.plotting_main import plot_zscore_trend
from .reporting import report_zscore_full_report
from altman_zscore.plotting.plotting_terminal import print_info, print_warning

def generate_llm_report(df, model, out_base, context_info, ticker, stock_prices):
    """
    Generate the LLM-based analysis report for a given stock and context.
    
    Args:
        df: DataFrame with Z-Score and financial data.
        model: Z-Score model name.
        out_base: Output file base path (without extension).
        context_info: Dictionary of context fields for the report.
        ticker: Stock ticker symbol.
        stock_prices: DataFrame of stock price data (optional).
        
    Returns:
        Markdown string with the full report, or None on error.
    """
    try:
        # Explicitly sanitize the context_info before passing to report generator
        sanitized_context = {k: v for k, v in context_info.items()}
        
        if "weekly_prices" in sanitized_context and isinstance(sanitized_context["weekly_prices"], pd.DataFrame):
            sanitized_context["weekly_prices"] = sanitized_context["weekly_prices"].to_dict(orient="records")
            
        if "raw_quarters" in sanitized_context and isinstance(sanitized_context["raw_quarters"], pd.DataFrame):
            sanitized_context["raw_quarters"] = sanitized_context["raw_quarters"].toDict(orient="records")
        
        # Generate just the report portion
        report = report_zscore_full_report(
            df, 
            model, 
            out_base, 
            print_to_console=True, 
            context_info=sanitized_context,
            save_to_disk=False  # Will save in finalize_outputs
        )
        return report
    except Exception as e:
        print_warning(f"Could not generate full Z-Score report: {e}")
        return None

def generate_chart(df, model, out_base, ticker, stock_prices):
    """
    Generate the Z-Score trend plot chart and save to disk.
    
    Args:
        df: DataFrame with Z-Score and financial data.
        model: Z-Score model name.
        out_base: Output file base path (without extension).
        ticker: Stock ticker symbol.
        stock_prices: DataFrame of stock price data (optional).
        
    Returns:
        Path to the saved chart image, or None on error.
    """
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

def finalize_outputs(df, model, out_base, context_info, ticker, stock_prices, llm_report, chart_path):
    """
    Save all final outputs (report, chart, metadata) to disk for a given analysis run.
    
    Args:
        df: DataFrame with Z-Score and financial data.
        model: Z-Score model name.
        out_base: Output file base path (without extension).
        context_info: Dictionary of context fields for the report.
        ticker: Stock ticker symbol.
        stock_prices: DataFrame of stock price data (optional).
        llm_report: Markdown string with the full report (optional).
        chart_path: Path to the saved chart image (optional).
        
    Returns:
        None. Outputs are saved to disk.
    """
    try:
        # Save the LLM report if we have one
        if llm_report:
            report_path = f"{out_base}_zscore_full_report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(llm_report)
            print_info(f"Full Z-Score report saved to {os.path.basename(report_path)}")
        
        # Verify chart was generated
        if chart_path and os.path.exists(chart_path):
            print_info(f"Z-Score trend plot saved to {os.path.basename(chart_path)}")
        
        # Save analysis metadata and context info
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
