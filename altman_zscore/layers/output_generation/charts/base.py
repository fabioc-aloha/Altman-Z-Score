"""
Base Chart Component

Provides common functionality and utilities for all chart components.
"""

import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from ....common.logging_config import get_logger

logger = get_logger(__name__)


class ChartBase(ABC):
    """
    Abstract base class for all chart components.
    
    Provides common utilities and enforces a consistent interface
    for all chart components.
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def add_to_figure(self, fig: go.Figure, row: int, col: int, **kwargs) -> None:
        """
        Add this chart component to a plotly figure.
        
        Args:
            fig: The plotly figure to add to
            row: Row position in subplot grid (1-indexed)
            col: Column position in subplot grid (1-indexed)
            **kwargs: Additional arguments specific to the component
        """
        pass
    
    def get_risk_color(self, z_score: float) -> str:
        """Get color based on Z-Score risk level."""
        if z_score < 1.8:
            return "red"
        elif z_score < 2.99:            
            return "orange"
        else:
            return "green"
    
    def get_marker_colors(self, z_scores: List[float]) -> List[str]:
        """Get marker colors for multiple Z-Score values based on risk zones."""
        return [self.get_risk_color(score) for score in z_scores]
    
    def add_risk_zone_lines(self, fig: go.Figure, row: int, col: int) -> None:
        """Add standard Z-Score risk zone reference lines."""
        fig.add_hline(y=1.8, line_dash="dash", line_color="red", 
                     annotation_text="Distress Zone", row=row, col=col)
        fig.add_hline(y=2.99, line_dash="dash", line_color="orange", 
                     annotation_text="Gray Zone", row=row, col=col)
    
    def create_no_data_bar(self, chart_name: str) -> go.Bar:
        """Create a standardized 'No Data' placeholder chart."""
        return go.Bar(
            x=[f'No {chart_name} Data'],
            y=[0],
            marker_color='gray',
            name=chart_name,
            text=['No Data Available'],
            textposition='auto'
        )
    
    def get_subplot_ref(self, row: int, col: int) -> str:
        """
        Get the subplot reference for annotations.
        
        Args:
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            
        Returns:
            Subplot reference string
        """
        if row == 1 and col == 1:
            return ""
        else:
            # Calculate subplot number (row-major order)
            subplot_num = (row - 1) * 3 + col
            return str(subplot_num) if subplot_num > 1 else ""
    
    def calculate_indicator_domain(self, row: int, col: int, 
                                 total_rows: int = 5, total_cols: int = 3) -> Dict[str, List[float]]:
        """
        Calculate the domain position for an indicator chart in a subplot.
        
        Args:
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            total_rows: Total number of rows in the grid
            total_cols: Total number of columns in the grid
            
        Returns:
            Dict with x and y domain coordinates
        """
        # Calculate subplot dimensions with padding
        subplot_width = 1.0 / total_cols
        subplot_height = 1.0 / total_rows
        padding = 0.02  # Small padding between subplots
        
        # Calculate position (convert to 0-indexed)
        row_idx = row - 1
        col_idx = col - 1
        
        # Calculate domain bounds
        x_start = col_idx * subplot_width + padding
        x_end = (col_idx + 1) * subplot_width - padding
        y_start = (total_rows - row) * subplot_height + padding  # Flip y-axis
        y_end = (total_rows - row + 1) * subplot_height - padding
        
        return {
            'x': [x_start, x_end],
            'y': [y_start, y_end]
        }
    
    def add_no_data_annotation(self, fig: go.Figure, message: str, row: int, col: int) -> None:
        """Add annotation for missing data."""
        fig.add_annotation(
            text=message,
            x=0.5, y=0.5,
            xref=f"x{self.get_subplot_ref(row, col)}",
            yref=f"y{self.get_subplot_ref(row, col)}",
            showarrow=False,
            font=dict(size=14, color="gray")
        )
    
    def format_value(self, value: Any, decimal_places: int = 1) -> str:
        """Format a value for display, handling None and non-numeric values."""
        if value is None:
            return 'N/A'
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f'{value:.{decimal_places}f}'
        return str(value)
    
    def safe_get_numeric(self, obj: Any, attr: str, default: float = 0) -> float:
        """Safely get a numeric attribute from an object."""
        try:
            value = getattr(obj, attr, default)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            return default
        except (AttributeError, TypeError, ValueError):
            return default
