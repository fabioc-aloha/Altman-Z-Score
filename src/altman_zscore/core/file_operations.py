"""
Filesystem operations for Altman Z-Score analysis.

This module provides helpers for constructing output file paths and saving results, metadata, and analysis outputs to disk. All functions are designed for robust error handling and modular use in the analysis pipeline.
"""

import json
import os
import logging
from typing import Dict, Any

from altman_zscore.utils.paths import get_output_dir
from altman_zscore.utils.io import save_dataframe
from altman_zscore.plotting.plotting_terminal import print_info, print_error

def get_zscore_path(ticker: str, ext: str = None) -> str:
    """
    Return the path for Z-Score output files in the ticker's output directory.

    Args:
        ticker: Stock ticker symbol.
        ext: Optional file extension (e.g., 'csv', 'json').

    Returns:
        Path to the Z-Score output file as a string.
    """
    base = get_output_dir(None, ticker=ticker)
    return f"{os.path.join(base, f'zscore_{ticker}')}{ext if ext else ''}"

def save_results_to_disk(df, out_base: str, error: bool = False) -> None:
    """
    Save results DataFrame to CSV and JSON using the DRY utility function.

    Args:
        df: DataFrame to save.
        out_base: Output file base path (without extension).
        error: If True, append '_error' to filenames.

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

def save_metadata_to_disk(metadata: Dict[str, Any], out_base: str) -> None:
    """
    Save analysis metadata to disk as a JSON file.

    Args:
        metadata: Dictionary of metadata to save.
        out_base: Output file base path (without extension).

    Returns:
        None. File is saved to disk.
    """
    try:
        metadata_path = f"{out_base}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        print_info(f"Metadata saved to: {metadata_path}")
    except Exception as e:
        print_error(f"Could not save metadata: {e}")
