"""
I/O utilities for Altman Z-Score analysis.

Centralizes DataFrame-to-file logic and output file naming for DRY compliance.
Provides functions for constructing output file paths and saving DataFrames to disk.
"""

import os
import pandas as pd
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

def get_output_file_path(ticker: str, basename: str, ext: str = "csv", subdir: Optional[str] = None) -> str:
    """Construct a consistent output file path for a given ticker, basename, and extension.

    Args:
        ticker (str): Stock ticker symbol.
        basename (str): Base name for the file (without extension).
        ext (str, optional): File extension (default 'csv').
        subdir (str, optional): Subdirectory under the ticker's output folder.

    Returns:
        str: Full output file path.
    """
    from .paths import get_output_dir
    base = get_output_dir(ticker=ticker)
    if subdir:
        base = os.path.join(base, subdir)
        os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{basename}.{ext}")

def save_dataframe(
    df: pd.DataFrame,
    path: str,
    fmt: Optional[str] = None,
    orient: Literal["split", "records", "index", "columns", "values", "table"] = "records",
    indent: int = 2
) -> None:
    """Save a DataFrame to CSV or JSON with pretty formatting and error handling.

    Args:
        df (pd.DataFrame): DataFrame to save.
        path (str): Output file path.
        fmt (str, optional): File format ('csv' or 'json'). If None, inferred from file extension.
        orient (str, optional): JSON orientation (if saving as JSON).
        indent (int, optional): Indentation for JSON output.

    Raises:
        ValueError: If the file format is unsupported.
        RuntimeError: If saving fails due to I/O or other errors.
    """
    fmt = fmt or os.path.splitext(path)[1][1:].lower()
    try:
        if fmt == "csv":
            df.to_csv(path, index=False)
        elif fmt == "json":
            # Only pass indent if pandas version supports it (>=1.0.0)
            import pandas as pd
            import inspect
            to_json_sig = inspect.signature(pd.DataFrame.to_json)
            if "indent" in to_json_sig.parameters:
                df.to_json(path, orient=orient, indent=indent)
            else:
                df.to_json(path, orient=orient)
        else:
            logger.error(f"Unsupported file format: {fmt}")
            raise ValueError(f"Unsupported file format: {fmt}")
    except Exception as e:
        logger.error(f"Could not save DataFrame to {path}: {e}")
        raise RuntimeError(f"Could not save DataFrame to {path}: {e}")
