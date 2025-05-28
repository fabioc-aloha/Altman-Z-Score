"""
Path utilities for Altman Z-Score analysis.

- All outputs for a given ticker are written to ./output/<TICKER>/.
- If a ticker is not available or does not exist, a marker file TICKER_NOT_AVAILABLE.txt is written in the ticker's output folder.
- The marker file is created by the pipeline when classification fails or the ticker is invalid, and no other output files are produced for that ticker.
"""
import os

def get_output_dir(relative_path=None, ticker=None):
    """
    Return the absolute path to the output directory or file for a given ticker.

    If ticker is provided, the base directory is ./output/<TICKER>/ (created if needed).
    If relative_path is provided, it is appended to the base directory. If it looks like a file, its parent directory is created.
    If neither is provided, returns the absolute path to ./output/ (created if needed).
    """
    output_dir = os.path.abspath('./output')
    os.makedirs(output_dir, exist_ok=True)

    if ticker:
        ticker_dir = os.path.join(output_dir, ticker.upper())
        os.makedirs(ticker_dir, exist_ok=True)
        base_dir = ticker_dir
    else:
        base_dir = output_dir

    if relative_path:
        full_path = os.path.join(base_dir, relative_path)
        # If the relative_path looks like a file, create its parent directory
        dirpath = os.path.dirname(full_path) if '.' in os.path.basename(full_path) else full_path
        os.makedirs(dirpath, exist_ok=True)
        return full_path
    else:
        return base_dir

def write_ticker_not_available(ticker, reason=None):
    """
    Write a marker file named TICKER_NOT_AVAILABLE.txt in the output/<TICKER>/ folder.
    The file indicates that the ticker is not available or does not exist, and is used to signal downstream tools or users.
    If a reason is provided, it is included in the file content for additional context.
    Returns the path to the marker file.
    """
    ticker_dir = get_output_dir(ticker=ticker)
    marker_path = os.path.join(ticker_dir, "TICKER_NOT_AVAILABLE.txt")
    message = f"Ticker '{ticker}' is not available or does not exist."
    if reason:
        message += f"\nReason: {reason}"
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(message + "\n")
    return marker_path
