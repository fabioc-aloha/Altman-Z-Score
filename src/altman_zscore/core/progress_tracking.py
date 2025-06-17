"""
Progress tracking functionality for Altman Z-Score analysis.

This module provides pipeline step definitions and a progress tracker factory for use in the main analysis pipeline. 
The progress tracker supports optional callback-based progress reporting for UI or CLI feedback.
"""


# Pipeline step definitions
PIPELINE_STEPS = [
    "Input Validation",
    # Data Fetching sub-steps
    "Fetch Company Profile",
    "Fetch Financials (SEC)",
    "Fetch Market Data (Prices, Splits, Dividends)",
    "Fetch Analyst Recommendations",
    "Fetch Executive/Officer Data",
    # End Data Fetching
    "Data Validation",
    "Data Processing",
    "Z-Score Computation",
    "Raw Data Output (CSV/JSON)",
    "LLM Prompt Construction",
    "LLM Report Generation",
    "Chart Generation",
    "Final File Output"
]

class ProgressTracker:
    """Tracks progress through the analysis pipeline."""
    
    def __init__(self, callback=None):
        """Initialize progress tracker.
        
        Args:
            callback: Optional callback function for progress updates
        """
        self.current_step = 0
        self.total_steps = len(PIPELINE_STEPS)
        self.callback = callback
        self.model_name = None  # Added to store the model name
        
    def update(self, step_name: str):
        """Update progress to the next step.
        
        Args:
            step_name: Name of the current step
        """
        if step_name in PIPELINE_STEPS:
            self.current_step = PIPELINE_STEPS.index(step_name)
        if self.callback:
            self.callback(self.current_step, self.total_steps, self.model_name)

def create_progress_tracker(callback=None):
    """Create a new progress tracker or update function.
    
    Args:
        callback: Optional callback for progress updates
        
    Returns:
        If callback provided, returns (update_fn, total_steps).
        Else, returns ProgressTracker instance.
    """
    return ProgressTracker(callback)
