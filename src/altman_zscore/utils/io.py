"""
I/O utilities for Altman Z-Score analysis.
Centralizes DataFrame-to-file logic and output file naming for DRY compliance.
"""

import os
import pandas as pd
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

def get_output_file_path(ticker: str, basename: str, ext: str = "csv", subdir: Optional[str] = None) -> str:
    """
    Construct a consistent output file path for a given ticker, basename, and extension.
    Optionally place in a subdirectory under the ticker's output folder.
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
    """
    Save a DataFrame to CSV or JSON with pretty formatting and error handling.
    If fmt is None, inferred from file extension.
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
