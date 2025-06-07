"""
Progress tracking functionality for Altman Z-Score analysis.

This module provides pipeline step definitions and a progress tracker factory for use in the main analysis pipeline. The progress tracker supports optional callback-based progress reporting for UI or CLI feedback.
"""

import logging
import time

# Pipeline step definitions
PIPELINE_STEPS = [
    "Input Validation",
    # Data Fetching sub-steps
    "Fetch Company Profile",
    "Fetch Financials (Yahoo/SEC)",
    "Fetch Market Data (Prices, Splits, Dividends)",
    "Fetch Analyst Recommendations",
    "Fetch Executive/Officer Data",
    # End Data Fetching
    "Data Validation",
    "Z-Score Computation",
    "Raw Data Output (CSV/JSON)",
    "LLM Prompt Construction",
    "LLM Report Generation",
    "Chart Generation",
    "Final File Output"
]

def create_progress_tracker(progress_callback=None):
    """
    Create a progress tracker with callback functionality.

    Args:
        progress_callback: Optional callback function for progress updates. Should accept (step_name, current_step, total_steps).
    Returns:
        Tuple of (update_progress function, total_steps).
    """
    total_steps = len(PIPELINE_STEPS)
    current_step = 0
    
    def update_progress(step_name):
        nonlocal current_step
        if progress_callback:
            progress_callback(step_name, current_step, total_steps)
            # Add small delay to make progress visible
            time.sleep(0.1)
        current_step += 1
    
    return update_progress, total_steps
