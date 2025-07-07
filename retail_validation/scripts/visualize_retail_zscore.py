#!/usr/bin/env python3
"""
Retail Z-Score Visualization Script
===================================

Creates interactive Plotly visualizations of retail Z-Score calculations
to analyze model performance and identify parameter optimization opportunities.

Features:
- Interactive scatter plot with threshold zones
- Color-coded bankruptcy outcomes (green=survived, red=failed)
- Hover information with company details
- Statistical performance metrics
- Parameter optimization guidance

Usage:
    python retail_validation/scripts/visualize_retail_zscore.py [options]

Options:
    --output-dir DIR       Output directory for charts (default: retail_validation/results/)
    --data-file FILE       Specific validation results file to visualize
    --save-html           Save interactive HTML chart
    --show-chart          Display chart in browser
    --include-stats       Include statistical analysis
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import validation config
from retail_validation.config.validation_config import (
    COMPANY_CATEGORIES, BANKRUPTCY_DATES, DEFAULT_OUTPUT_DIR
)

# Z-Score thresholds for retail model
RETAIL_THRESHOLDS = {
    'safe': 2.99,
    'gray_upper': 2.99,
    'gray_lower': 1.81,
    'distress': 1.81
}

class RetailZScoreVisualizer:
    """
    Visualizes retail Z-Score calculations and bankruptcy outcomes.
    """
    
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        """Initialize the visualizer."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load company categories
        self.failed_companies = set(COMPANY_CATEGORIES['failed'])
        self.distressed_companies = set(COMPANY_CATEGORIES['distressed'])
        self.recovery_companies = set(COMPANY_CATEGORIES['recovery'])
        self.stable_companies = set(COMPANY_CATEGORIES['stable'])
        
    def load_validation_data(self, data_file: Optional[str] = None) -> pd.DataFrame:
        """
        Load validation results data.
        
        Args:
            data_file: Optional specific data file to load
            
        Returns:
            DataFrame with validation results
        """
        if data_file:
            data_path = Path(data_file)
        else:
            # Look for the most recent validation results
            results_dir = self.output_dir
            
            # Look for both CSV and JSON files
            csv_files = list(results_dir.glob("*validation_results*.csv"))
            json_files = []
            
            # Look for raw_results.json files in subdirectories
            for subdir in results_dir.glob("*/"):
                json_file = subdir / "raw_results.json"
                if json_file.exists():
                    json_files.append(json_file)
            
            # Prefer CSV files, but use JSON if available
            if csv_files:
                data_path = max(csv_files, key=lambda f: f.stat().st_mtime)
                file_type = 'csv'
            elif json_files:
                data_path = max(json_files, key=lambda f: f.stat().st_mtime)
                file_type = 'json'
            else:
                raise FileNotFoundError(f"No validation results found in {results_dir}")
        
        print(f"Loading data from: {data_path}")
        
        try:
            if data_path.suffix.lower() == '.json' or file_type == 'json':
                # Load JSON data and convert to DataFrame
                with open(data_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Extract company results
                companies_data = []
                
                # The JSON structure is {ticker: {data}, ticker: {data}, ...}
                for ticker, company_data in json_data.items():
                    if isinstance(company_data, dict):
                        # Skip companies with errors or missing retail_score
                        if 'error' in company_data or 'retail_score' not in company_data:
                            print(f"Skipping {ticker}: missing data or error")
                            continue
                            
                        companies_data.append({
                            'ticker': ticker,
                            'z_score': company_data.get('retail_score', 0),
                            'risk_category': company_data.get('retail_risk', 'Unknown'),
                            'model_used': 'retail',
                            'traditional_score': company_data.get('traditional_score', 0),
                            'traditional_risk': company_data.get('traditional_risk', 'Unknown'),
                            'category': company_data.get('category', 'other'),
                            'bankruptcy_date': company_data.get('bankruptcy_date'),
                            'company_name': company_data.get('metadata', {}).get('company_name', ticker)
                        })
                
                df = pd.DataFrame(companies_data)
                
            else:
                # Load CSV data
                df = pd.read_csv(data_path)
            
            print(f"Loaded {len(df)} companies from validation results")
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def categorize_companies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add bankruptcy outcome and category information to the dataframe.
        
        Args:
            df: DataFrame with company data
            
        Returns:
            DataFrame with added categorization columns
        """
        # Add bankruptcy outcome
        df['bankruptcy_outcome'] = df['ticker'].apply(
            lambda x: 'Failed' if x in self.failed_companies else 'Survived'
        )
        
        # Add company category
        def get_category(ticker):
            if ticker in self.failed_companies:
                return 'Failed'
            elif ticker in self.distressed_companies:
                return 'Distressed'
            elif ticker in self.recovery_companies:
                return 'Recovery'
            elif ticker in self.stable_companies:
                return 'Stable'
            else:
                return 'Other'
        
        df['category'] = df['ticker'].apply(get_category)
        
        # Add colors for plotting
        color_map = {
            'Failed': '#FF4444',      # Red
            'Distressed': '#FF8844',  # Orange
            'Recovery': '#44FF44',    # Green
            'Stable': '#4444FF',      # Blue
            'Other': '#888888'        # Gray
        }
        
        df['color'] = df['category'].map(color_map)
        
        # Debug: Check for any issues with the dataframe
        print(f"DataFrame shape after categorization: {df.shape}")
        print(f"Categories found: {df['category'].unique()}")
        print(f"Columns: {list(df.columns)}")
        
        return df
    
    def create_interactive_zscore_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create an interactive Z-Score plot with adjustable risk thresholds.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure object with interactive controls
        """
        # Sort by Z-Score for better visualization
        df_sorted = df.sort_values('z_score')
        
        # Create figure with secondary y-axis for controls
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.85, 0.15],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
            subplot_titles=["Retail Z-Score Analysis with Adjustable Risk Bands", "Threshold Controls"],
            vertical_spacing=0.1
        )
        
        # Add threshold zones as shapes (will be updated by JavaScript)
        # Safe zone (green background)
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(df_sorted)-0.5, 
            y0=RETAIL_THRESHOLDS['safe'], y1=df_sorted['z_score'].max() + 2,
            fillcolor="rgba(144, 238, 144, 0.3)",
            line=dict(width=0),
            layer="below",
            row=1, col=1
        )
        
        # Gray zone (yellow background)
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(df_sorted)-0.5, 
            y0=RETAIL_THRESHOLDS['gray_lower'], y1=RETAIL_THRESHOLDS['gray_upper'],
            fillcolor="rgba(255, 255, 0, 0.3)",
            line=dict(width=0),
            layer="below",
            row=1, col=1
        )
        
        # Distress zone (red background)
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=len(df_sorted)-0.5, 
            y0=df_sorted['z_score'].min() - 2, y1=RETAIL_THRESHOLDS['distress'],
            fillcolor="rgba(255, 182, 193, 0.3)",
            line=dict(width=0),
            layer="below",
            row=1, col=1
        )
        
        # Add moveable threshold lines
        fig.add_hline(
            y=RETAIL_THRESHOLDS['safe'], 
            line_dash="solid", 
            line_color="green", 
            line_width=3,
            annotation_text="Safe Threshold",
            annotation_position="right",
            row=1, col=1
        )
        
        fig.add_hline(
            y=RETAIL_THRESHOLDS['distress'], 
            line_dash="solid", 
            line_color="red", 
            line_width=3,
            annotation_text="Distress Threshold",
            annotation_position="right",
            row=1, col=1
        )
        
        # Plot companies by category with enhanced styling
        categories = df_sorted['category'].unique()
        x_positions = list(range(len(df_sorted)))
        
        for category in categories:
            category_data = df_sorted[df_sorted['category'] == category]
            category_indices = [i for i, ticker in enumerate(df_sorted['ticker']) if ticker in category_data['ticker'].values]
            
            # Determine marker properties based on bankruptcy outcome
            failed_companies = category_data[category_data['bankruptcy_date'].notna()]
            survived_companies = category_data[category_data['bankruptcy_date'].isna()]
            
            if len(failed_companies) > 0:
                failed_indices = [i for i, ticker in enumerate(df_sorted['ticker']) if ticker in failed_companies['ticker'].values]
                fig.add_trace(go.Scatter(
                    x=failed_indices,
                    y=failed_companies['z_score'],
                    mode='markers',
                    name=f'{category} - Failed ({len(failed_companies)})',
                    text=failed_companies['ticker'],
                    customdata=failed_companies[['company_name', 'bankruptcy_date', 'traditional_score']],
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Company: %{customdata[0]}<br>" +
                        "Retail Z-Score: %{y:.2f}<br>" +
                        "Traditional Z-Score: %{customdata[2]:.2f}<br>" +
                        "Bankruptcy Date: %{customdata[1]}<br>" +
                        "Category: " + category + "<br>" +
                        "<extra></extra>"
                    ),
                    marker=dict(
                        color='red',
                        size=14,
                        symbol='x',
                        line=dict(width=2, color='darkred')
                    )
                ), row=1, col=1)
            
            if len(survived_companies) > 0:
                survived_indices = [i for i, ticker in enumerate(df_sorted['ticker']) if ticker in survived_companies['ticker'].values]
                fig.add_trace(go.Scatter(
                    x=survived_indices,
                    y=survived_companies['z_score'],
                    mode='markers',
                    name=f'{category} - Survived ({len(survived_companies)})',
                    text=survived_companies['ticker'],
                    customdata=survived_companies[['company_name', 'traditional_score']],
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Company: %{customdata[0]}<br>" +
                        "Retail Z-Score: %{y:.2f}<br>" +
                        "Traditional Z-Score: %{customdata[1]:.2f}<br>" +
                        "Category: " + category + "<br>" +
                        "Status: Active<br>" +
                        "<extra></extra>"
                    ),
                    marker=dict(
                        color='green',
                        size=12,
                        symbol='circle',
                        line=dict(width=2, color='darkgreen')
                    )
                ), row=1, col=1)
        
        # Add risk zone indicators
        fig.add_annotation(
            x=len(df_sorted) * 0.02, 
            y=RETAIL_THRESHOLDS['safe'] + (df_sorted['z_score'].max() - RETAIL_THRESHOLDS['safe']) * 0.1,
            text="<b>SAFE ZONE</b><br>Low Bankruptcy Risk",
            showarrow=False,
            font=dict(color="darkgreen", size=12, family="Arial Bold"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="green",
            borderwidth=1,
            row=1, col=1
        )
        
        fig.add_annotation(
            x=len(df_sorted) * 0.02, 
            y=(RETAIL_THRESHOLDS['safe'] + RETAIL_THRESHOLDS['distress']) / 2,
            text="<b>GRAY ZONE</b><br>Moderate Risk",
            showarrow=False,
            font=dict(color="darkorange", size=12, family="Arial Bold"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="orange",
            borderwidth=1,
            row=1, col=1
        )
        
        fig.add_annotation(
            x=len(df_sorted) * 0.02, 
            y=RETAIL_THRESHOLDS['distress'] - (RETAIL_THRESHOLDS['distress'] - df_sorted['z_score'].min()) * 0.1,
            text="<b>DISTRESS ZONE</b><br>High Bankruptcy Risk",
            showarrow=False,
            font=dict(color="darkred", size=12, family="Arial Bold"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="red",
            borderwidth=1,
            row=1, col=1
        )
        
        # Add threshold sliders in the bottom subplot
        z_min, z_max = df_sorted['z_score'].min() - 1, df_sorted['z_score'].max() + 1
        
        # Create slider traces (invisible points for slider positioning)
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 0],
            mode='markers',
            marker=dict(size=0, opacity=0),
            showlegend=False,
            hoverinfo='skip'
        ), row=2, col=1)
        
        # Update layout with enhanced styling
        fig.update_layout(
            title={
                'text': "Interactive Retail Z-Score Model Analysis<br><sub>Drag threshold lines or use controls to adjust risk bands</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial Bold'}
            },
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.3)",
                borderwidth=1,
                font=dict(size=10)
            ),
            width=1400,
            height=900,
            template="plotly_white",
            
            # Add range sliders for threshold adjustment
            updatemenus=[
                {
                    "buttons": [
                        {
                            "label": "Reset Thresholds",
                            "method": "restyle",
                            "args": [{"shapes": self._get_default_shapes(len(df_sorted), df_sorted['z_score'].min(), df_sorted['z_score'].max())}]
                        },
                        {
                            "label": "Conservative",
                            "method": "restyle", 
                            "args": [{"shapes": self._get_conservative_shapes(len(df_sorted), df_sorted['z_score'].min(), df_sorted['z_score'].max())}]
                        },
                        {
                            "label": "Aggressive",
                            "method": "restyle",
                            "args": [{"shapes": self._get_aggressive_shapes(len(df_sorted), df_sorted['z_score'].min(), df_sorted['z_score'].max())}]
                        }
                    ],
                    "direction": "down",
                    "showactive": True,
                    "x": 0.1,
                    "xanchor": "left",
                    "y": 1.02,
                    "yanchor": "top"
                }
            ],
            
            # Add sliders for threshold adjustment
            sliders=[
                {
                    "active": int((RETAIL_THRESHOLDS['safe'] - z_min) / (z_max - z_min) * 100),
                    "currentvalue": {"prefix": "Safe Threshold: "},
                    "pad": {"t": 50},
                    "steps": [
                        {
                            "args": [{"shapes[0].y1": val, "shapes[0].y0": val}],
                            "label": f"{val:.1f}",
                            "method": "relayout",
                            "value": val
                        }
                        for val in np.arange(z_min, z_max, 0.1)
                    ],
                    "x": 0.1,
                    "xanchor": "left",
                    "y": 0.0,
                    "yanchor": "top"
                },
                {
                    "active": int((RETAIL_THRESHOLDS['distress'] - z_min) / (z_max - z_min) * 100),
                    "currentvalue": {"prefix": "Distress Threshold: "},
                    "pad": {"t": 20},
                    "steps": [
                        {
                            "args": [{"shapes[2].y1": val, "shapes[2].y0": val}],
                            "label": f"{val:.1f}",
                            "method": "relayout",
                            "value": val
                        }
                        for val in np.arange(z_min, z_max, 0.1)
                    ],
                    "x": 0.1,
                    "xanchor": "left",
                    "y": -0.05,
                    "yanchor": "top"
                }
            ]
        )
        
        # Update x and y axes
        fig.update_xaxes(
            title="Company Index (sorted by Z-Score)",
            tickangle=45,
            row=1, col=1
        )
        
        fig.update_yaxes(
            title="Z-Score",
            row=1, col=1
        )
        
        # Hide axes for the control panel
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=1)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=1)
        
        return fig
    
    def _get_default_shapes(self, n_companies: int, z_min: float, z_max: float) -> List[Dict]:
        """Get default threshold shapes."""
        return [
            # Safe zone
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": RETAIL_THRESHOLDS['safe'], "y1": z_max + 2,
                "fillcolor": "rgba(144, 238, 144, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            # Gray zone  
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": RETAIL_THRESHOLDS['gray_lower'], "y1": RETAIL_THRESHOLDS['gray_upper'],
                "fillcolor": "rgba(255, 255, 0, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            # Distress zone
            {
                "type": "rect", 
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": z_min - 2, "y1": RETAIL_THRESHOLDS['distress'],
                "fillcolor": "rgba(255, 182, 193, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            }
        ]
    
    def _get_conservative_shapes(self, n_companies: int, z_min: float, z_max: float) -> List[Dict]:
        """Get conservative threshold shapes (higher thresholds)."""
        conservative_safe = RETAIL_THRESHOLDS['safe'] + 0.5
        conservative_distress = RETAIL_THRESHOLDS['distress'] + 0.3
        
        return [
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": conservative_safe, "y1": z_max + 2,
                "fillcolor": "rgba(144, 238, 144, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": conservative_distress, "y1": conservative_safe,
                "fillcolor": "rgba(255, 255, 0, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": z_min - 2, "y1": conservative_distress,
                "fillcolor": "rgba(255, 182, 193, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            }
        ]
    
    def _get_aggressive_shapes(self, n_companies: int, z_min: float, z_max: float) -> List[Dict]:
        """Get aggressive threshold shapes (lower thresholds)."""
        aggressive_safe = RETAIL_THRESHOLDS['safe'] - 0.5
        aggressive_distress = RETAIL_THRESHOLDS['distress'] - 0.3
        
        return [
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": max(aggressive_safe, 0), "y1": z_max + 2,
                "fillcolor": "rgba(144, 238, 144, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": max(aggressive_distress, z_min - 2), "y1": max(aggressive_safe, 0),
                "fillcolor": "rgba(255, 255, 0, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            },
            {
                "type": "rect",
                "x0": -0.5, "x1": n_companies-0.5,
                "y0": z_min - 2, "y1": max(aggressive_distress, z_min - 2),
                "fillcolor": "rgba(255, 182, 193, 0.3)",
                "line": {"width": 0},
                "layer": "below"
            }
        ]
        """
        Create the main Z-Score scatter plot with threshold zones.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure object
        """
        # Create the figure
        fig = go.Figure()
        
        # Add threshold zones as shapes
        # Safe zone (green background)
        fig.add_shape(
            type="rect",
            x0=-1, x1=len(df), y0=RETAIL_THRESHOLDS['safe'], y1=10,
            fillcolor="rgba(144, 238, 144, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        # Gray zone (yellow background)
        fig.add_shape(
            type="rect",
            x0=-1, x1=len(df), 
            y0=RETAIL_THRESHOLDS['gray_lower'], y1=RETAIL_THRESHOLDS['gray_upper'],
            fillcolor="rgba(255, 255, 0, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        # Distress zone (red background)
        fig.add_shape(
            type="rect",
            x0=-1, x1=len(df), y0=-5, y1=RETAIL_THRESHOLDS['distress'],
            fillcolor="rgba(255, 182, 193, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        # Add threshold lines
        fig.add_hline(y=RETAIL_THRESHOLDS['safe'], line_dash="dash", 
                     line_color="green", annotation_text="Safe Zone (Z > 2.99)")
        fig.add_hline(y=RETAIL_THRESHOLDS['distress'], line_dash="dash", 
                     line_color="red", annotation_text="Distress Zone (Z < 1.81)")
        
        # Plot companies by category
        categories = df['category'].unique()
        
        for category in categories:
            category_data = df[df['category'] == category]
            
            # Determine marker symbol and size
            if category == 'Failed':
                marker_symbol = 'x'
                marker_size = 12
            else:
                marker_symbol = 'circle'
                marker_size = 10
            
            fig.add_trace(go.Scatter(
                x=list(range(len(category_data))),
                y=category_data['z_score'],
                mode='markers',
                name=f'{category} ({len(category_data)})',
                text=category_data['ticker'],
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Z-Score: %{y:.2f}<br>" +
                    "Category: " + category + "<br>" +
                    "Risk Zone: %{customdata}<br>" +
                    "<extra></extra>"
                ),
                customdata=category_data['risk_category'] if 'risk_category' in category_data.columns else ['Unknown'] * len(category_data),
                marker=dict(
                    color=category_data['color'].iloc[0],
                    size=marker_size,
                    symbol=marker_symbol,
                    line=dict(width=2, color='white')
                )
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': "Retail Z-Score Model Performance Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title="Company Index",
            yaxis_title="Z-Score",
            hovermode='closest',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1
            ),
            width=1200,
            height=800,
            template="plotly_white"
        )
        
        # Add annotations for zones
        fig.add_annotation(
            x=len(df) * 0.95, y=RETAIL_THRESHOLDS['safe'] + 0.5,
            text="SAFE ZONE", showarrow=False,
            font=dict(color="green", size=14, family="Arial Black"),
            bgcolor="rgba(255, 255, 255, 0.7)"
        )
        
        fig.add_annotation(
            x=len(df) * 0.95, y=(RETAIL_THRESHOLDS['safe'] + RETAIL_THRESHOLDS['distress']) / 2,
            text="GRAY ZONE", showarrow=False,
            font=dict(color="orange", size=14, family="Arial Black"),
            bgcolor="rgba(255, 255, 255, 0.7)"
        )
        
        fig.add_annotation(
            x=len(df) * 0.95, y=RETAIL_THRESHOLDS['distress'] - 0.5,
            text="DISTRESS ZONE", showarrow=False,
            font=dict(color="red", size=14, family="Arial Black"),
            bgcolor="rgba(255, 255, 255, 0.7)"
        )
        
        return fig
    
    def create_distribution_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a distribution plot showing Z-Score distributions by outcome.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Failed companies distribution
        failed_data = df[df['bankruptcy_outcome'] == 'Failed']['z_score']
        survived_data = df[df['bankruptcy_outcome'] == 'Survived']['z_score']
        
        fig.add_trace(go.Histogram(
            x=failed_data,
            name=f'Failed Companies ({len(failed_data)})',
            opacity=0.7,
            marker_color='red',
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=survived_data,
            name=f'Survived Companies ({len(survived_data)})',
            opacity=0.7,
            marker_color='green',
            nbinsx=20
        ))
        
        # Add threshold lines
        fig.add_vline(x=RETAIL_THRESHOLDS['safe'], line_dash="dash", 
                     line_color="green", annotation_text="Safe Threshold")
        fig.add_vline(x=RETAIL_THRESHOLDS['distress'], line_dash="dash", 
                     line_color="red", annotation_text="Distress Threshold")
        
        fig.update_layout(
            title="Z-Score Distribution by Bankruptcy Outcome",
            xaxis_title="Z-Score",
            yaxis_title="Count",
            barmode='overlay',
            template="plotly_white"
        )
        
        return fig
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate model performance metrics.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Dictionary with performance metrics
        """
        # Create prediction based on thresholds
        def predict_bankruptcy(z_score):
            if z_score < RETAIL_THRESHOLDS['distress']:
                return 'Failed'
            elif z_score < RETAIL_THRESHOLDS['safe']:
                return 'Gray'
            else:
                return 'Safe'
        
        df['prediction'] = df['z_score'].apply(predict_bankruptcy)
        
        # Calculate metrics
        failed_companies = df[df['bankruptcy_outcome'] == 'Failed']
        survived_companies = df[df['bankruptcy_outcome'] == 'Survived']
        
        # Sensitivity (True Positive Rate) - How many failed companies were correctly identified
        correctly_identified_failed = len(failed_companies[failed_companies['prediction'] == 'Failed'])
        sensitivity = correctly_identified_failed / len(failed_companies) if len(failed_companies) > 0 else 0
        
        # Specificity (True Negative Rate) - How many survived companies were correctly identified as safe
        correctly_identified_safe = len(survived_companies[survived_companies['prediction'] == 'Safe'])
        specificity = correctly_identified_safe / len(survived_companies) if len(survived_companies) > 0 else 0
        
        # Accuracy
        correct_predictions = correctly_identified_failed + correctly_identified_safe
        accuracy = correct_predictions / len(df) if len(df) > 0 else 0
        
        # False positive rate - Survived companies incorrectly flagged as failed
        false_positives = len(survived_companies[survived_companies['prediction'] == 'Failed'])
        false_positive_rate = false_positives / len(survived_companies) if len(survived_companies) > 0 else 0
        
        return {
            'total_companies': len(df),
            'failed_companies': len(failed_companies),
            'survived_companies': len(survived_companies),
            'sensitivity': sensitivity,
            'specificity': specificity,
            'accuracy': accuracy,
            'false_positive_rate': false_positive_rate,
            'correctly_identified_failed': correctly_identified_failed,
            'correctly_identified_safe': correctly_identified_safe,
            'mean_zscore_failed': failed_companies['z_score'].mean() if len(failed_companies) > 0 else 0,
            'mean_zscore_survived': survived_companies['z_score'].mean() if len(survived_companies) > 0 else 0,
            'zscore_separation': abs(survived_companies['z_score'].mean() - failed_companies['z_score'].mean()) if len(failed_companies) > 0 and len(survived_companies) > 0 else 0
        }
    
    def create_performance_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a comprehensive performance dashboard.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure object with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Z-Score Scatter Plot', 'Distribution by Outcome', 
                           'Performance Metrics', 'Zone Analysis'),
            specs=[[{"type": "scatter"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Add scatter plot
        categories = df['category'].unique()
        for category in categories:
            category_data = df[df['category'] == category]
            fig.add_trace(
                go.Scatter(
                    x=category_data.index,
                    y=category_data['z_score'],
                    mode='markers',
                    name=category,
                    marker=dict(color=category_data['color'].iloc[0]),
                    text=category_data['ticker'],
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Add distribution histograms
        failed_data = df[df['bankruptcy_outcome'] == 'Failed']['z_score']
        survived_data = df[df['bankruptcy_outcome'] == 'Survived']['z_score']
        
        fig.add_trace(
            go.Histogram(x=failed_data, name='Failed', marker_color='red', opacity=0.7, showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(x=survived_data, name='Survived', marker_color='green', opacity=0.7, showlegend=False),
            row=1, col=2
        )
        
        # Calculate and add performance metrics
        metrics = self.calculate_performance_metrics(df)
        
        fig.add_trace(
            go.Bar(
                x=['Accuracy', 'Sensitivity', 'Specificity'],
                y=[metrics['accuracy'], metrics['sensitivity'], metrics['specificity']],
                marker_color=['blue', 'red', 'green'],
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Add zone analysis pie chart
        zone_counts = df['prediction'].value_counts() if 'prediction' in df.columns else pd.Series([0, 0, 0], index=['Safe', 'Gray', 'Failed'])
        
        fig.add_trace(
            go.Pie(
                labels=['Safe Zone', 'Gray Zone', 'Distress Zone'],
                values=[zone_counts.get('Safe', 0), zone_counts.get('Gray', 0), zone_counts.get('Failed', 0)],
                marker_colors=['green', 'orange', 'red'],
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Retail Z-Score Model Performance Dashboard",
            showlegend=True,
            height=800,
            template="plotly_white"
        )
        
        return fig
    
    def generate_optimization_report(self, df: pd.DataFrame) -> str:
        """
        Generate a text report with optimization recommendations.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            String with optimization recommendations
        """
        metrics = self.calculate_performance_metrics(df)
        
        report = f"""
RETAIL Z-SCORE MODEL OPTIMIZATION REPORT
=======================================

CURRENT PERFORMANCE METRICS:
- Total Companies Analyzed: {metrics['total_companies']}
- Failed Companies: {metrics['failed_companies']}
- Survived Companies: {metrics['survived_companies']}

PREDICTION ACCURACY:
- Overall Accuracy: {metrics['accuracy']:.2%}
- Sensitivity (Failed Detection): {metrics['sensitivity']:.2%}
- Specificity (Safe Detection): {metrics['specificity']:.2%}
- False Positive Rate: {metrics['false_positive_rate']:.2%}

SCORE DISTRIBUTION:
- Mean Z-Score (Failed): {metrics['mean_zscore_failed']:.2f}
- Mean Z-Score (Survived): {metrics['mean_zscore_survived']:.2f}
- Score Separation: {metrics['zscore_separation']:.2f}

OPTIMIZATION RECOMMENDATIONS:

1. THRESHOLD ADJUSTMENT:
   - Current Distress Threshold: {RETAIL_THRESHOLDS['distress']:.2f}
   - Current Safe Threshold: {RETAIL_THRESHOLDS['safe']:.2f}
   - Recommendation: {'Increase distress threshold' if metrics['sensitivity'] < 0.8 else 'Consider lowering distress threshold'}

2. COEFFICIENT OPTIMIZATION:
   - Current Formula: Z = 1.2·X₁ + 1.4·X₂ + 3.3·X₃ + 0.6·X₄ + 1.0·X₅ + 0.5·X₆
   - Focus Area: {'Inventory component (X₆)' if metrics['zscore_separation'] < 1.0 else 'Working capital component (X₁)'}

3. MODEL PERFORMANCE:
   - Status: {'Needs improvement' if metrics['accuracy'] < 0.75 else 'Good performance' if metrics['accuracy'] < 0.85 else 'Excellent performance'}
   - Priority: {'Increase sensitivity' if metrics['sensitivity'] < 0.8 else 'Maintain current performance'}

4. NEXT STEPS:
   - Run parameter sensitivity analysis
   - Test alternative coefficient combinations
   - Validate on additional retail companies
   - Consider sector-specific sub-models

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def visualize_retail_zscores(self, 
                                data_file: Optional[str] = None,
                                save_html: bool = True,
                                show_chart: bool = True,
                                include_stats: bool = True) -> Dict:
        """
        Main method to create all visualizations.
        
        Args:
            data_file: Optional data file path
            save_html: Whether to save HTML files
            show_chart: Whether to display charts
            include_stats: Whether to include statistical analysis
            
        Returns:
            Dictionary with paths to generated files
        """
        print("Starting retail Z-Score visualization...")
        
        # Load data
        df = self.load_validation_data(data_file)
        
        # Add categorization
        df = self.categorize_companies(df)
        
        # Create enhanced visualizations
        try:
            print("Creating interactive plot...")
            interactive_fig = self.create_interactive_zscore_plot(df)
            print("Interactive plot created successfully")
            
            print("Creating coefficient adjustment plot...")
            coefficient_fig = self.create_coefficient_adjustment_plot(df)
            print("Coefficient plot created successfully")
            
            print("Creating comprehensive dashboard...")
            comprehensive_fig = self.create_comprehensive_dashboard(df)
            print("Comprehensive dashboard created successfully")
            
            print("Creating distribution plot...")
            distribution_fig = self.create_distribution_plot(df)
            print("Distribution plot created successfully")
            
        except Exception as e:
            print(f"Error creating plots: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        generated_files = {}
        
        # Save HTML files
        if save_html:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            interactive_path = self.output_dir / f"retail_zscore_interactive_{timestamp}.html"
            coefficient_path = self.output_dir / f"retail_zscore_coefficients_{timestamp}.html"
            comprehensive_path = self.output_dir / f"retail_zscore_comprehensive_{timestamp}.html"
            distribution_path = self.output_dir / f"retail_zscore_distribution_{timestamp}.html"
            
            # Save with enhanced HTML templates
            self._save_enhanced_html(interactive_fig, str(interactive_path), 
                                   "Interactive Retail Z-Score Analysis", 
                                   "Adjust risk thresholds and analyze model performance")
            
            self._save_enhanced_html(coefficient_fig, str(coefficient_path),
                                   "Coefficient Adjustment Tool",
                                   "Optimize model coefficients for better performance")
            
            self._save_enhanced_html(comprehensive_fig, str(comprehensive_path),
                                   "Comprehensive Analysis Dashboard", 
                                   "Complete overview of model performance and metrics")
            
            distribution_fig.write_html(str(distribution_path))
            
            generated_files['interactive'] = str(interactive_path)
            generated_files['coefficients'] = str(coefficient_path)
            generated_files['comprehensive'] = str(comprehensive_path)
            generated_files['distribution'] = str(distribution_path)
            
            print(f"Saved enhanced visualizations to {self.output_dir}")
        
        # Generate optimization report
        if include_stats:
            report = self.generate_optimization_report(df)
            report_path = self.output_dir / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            generated_files['report'] = str(report_path)
            print(f"Saved optimization report to {report_path}")
        
        # Display charts
        if show_chart:
            interactive_fig.show()
        
        return generated_files
    
    def _save_enhanced_html(self, fig: go.Figure, filepath: str, title: str, description: str):
        """Save figure with enhanced HTML template."""
        try:
            # Generate the chart HTML
            chart_html = fig.to_html(include_plotlyjs=True, div_id="chart", config={'responsive': True})
            
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.9;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        .instructions {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    
    <div class="instructions">
        <strong>Instructions:</strong>
        <ul>
            <li>Hover over data points for detailed information</li>
            <li>Use the toolbar to zoom, pan, and download the chart</li>
            <li>Interactive controls allow real-time threshold adjustments</li>
            <li>Green dots = Active companies, Red X = Bankrupt companies</li>
        </ul>
    </div>
    
    <div class="chart-container">
        {chart_html}
    </div>
    
    <div class="footer">
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Retail Z-Score Model Analysis
    </div>
</body>
</html>"""
        
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_template)
                
        except Exception as e:
            print(f"Error saving HTML file {filepath}: {e}")
            import traceback
            traceback.print_exc()
            raise


    def create_coefficient_adjustment_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create an interactive plot for adjusting model coefficients.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure with coefficient sliders
        """
        # Current coefficients
        current_coeffs = {
            'X1': 1.2,  # Working Capital Ratio
            'X2': 1.4,  # Retained Earnings Ratio  
            'X3': 3.3,  # EBIT Ratio
            'X4': 0.6,  # Market Equity Ratio
            'X5': 1.0,  # Asset Turnover
            'X6': 0.5   # Inventory Adjustment
        }
        
        fig = go.Figure()
        
        # Add coefficient bars
        components = list(current_coeffs.keys())
        values = list(current_coeffs.values())
        
        fig.add_trace(go.Bar(
            x=components,
            y=values,
            name='Current Coefficients',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
            text=[f'{v:.1f}' for v in values],
            textposition='auto'
        ))
        
        # Add component descriptions
        descriptions = [
            'Working Capital<br>(excl. inventory)',
            'Retained Earnings<br>Stability',
            'EBIT<br>Profitability', 
            'Market Equity<br>Leverage',
            'Asset Turnover<br>Efficiency',
            'Inventory Turnover<br>Retail-specific'
        ]
        
        fig.update_layout(
            title={
                'text': 'Retail Z-Score Model Coefficient Adjustment<br><sub>Z = 1.2·X₁ + 1.4·X₂ + 3.3·X₃ + 0.6·X₄ + 1.0·X₅ + 0.5·X₆</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title='Model Components',
            yaxis_title='Coefficient Value',
            template='plotly_white',
            height=600,
            
            # Add sliders for each coefficient
            sliders=[
                {
                    "active": int(coeff * 10),
                    "currentvalue": {"prefix": f"{comp} Coefficient: "},
                    "pad": {"t": 50 + i * 60},
                    "steps": [
                        {
                            "args": [{"y": [values[:j] + [val] + values[j+1:] for j in range(len(values)) if j == i][0]}],
                            "label": f"{val:.1f}",
                            "method": "restyle",
                            "value": val
                        }
                        for val in np.arange(0, 5, 0.1)
                    ],
                    "x": 0.1,
                    "xanchor": "left", 
                    "y": 1.0 - i * 0.08,
                    "yanchor": "top"
                }
                for i, (comp, coeff) in enumerate(current_coeffs.items())
            ]
        )
        
        # Add annotations for component descriptions
        for i, (comp, desc) in enumerate(zip(components, descriptions)):
            fig.add_annotation(
                x=i,
                y=values[i] + 0.1,
                text=desc,
                showarrow=False,
                font=dict(size=10),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="gray",
                borderwidth=1
            )
        
        return fig
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a comprehensive dashboard with all analysis tools.
        
        Args:
            df: DataFrame with Z-Score data
            
        Returns:
            Plotly figure with multiple interactive panels
        """
        # Create subplots for comprehensive dashboard
        fig = make_subplots(
            rows=3, cols=2,
            row_heights=[0.5, 0.25, 0.25],
            column_widths=[0.7, 0.3],
            specs=[
                [{"colspan": 2}, None],  # Main chart spans both columns
                [{"type": "bar"}, {"type": "pie"}],  # Performance metrics and zone distribution
                [{"type": "histogram"}, {"type": "scatter"}]  # Distribution and correlation
            ],
            subplot_titles=[
                'Interactive Z-Score Analysis with Risk Bands',
                'Performance Metrics', 
                'Zone Distribution',
                'Score Distribution by Outcome',
                'Retail vs Traditional Model Comparison'
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.05
        )
        
        # Main interactive plot (row 1, spanning both columns)
        df_sorted = df.sort_values('z_score')
        
        # Add companies by bankruptcy outcome
        failed_companies = df_sorted[df_sorted['bankruptcy_date'].notna()]
        survived_companies = df_sorted[df_sorted['bankruptcy_date'].isna()]
        
        if len(failed_companies) > 0:
            failed_indices = [i for i, ticker in enumerate(df_sorted['ticker']) if ticker in failed_companies['ticker'].values]
            fig.add_trace(go.Scatter(
                x=failed_indices,
                y=failed_companies['z_score'],
                mode='markers',
                name=f'Failed Companies ({len(failed_companies)})',
                marker=dict(color='red', size=14, symbol='x'),
                text=failed_companies['ticker'],
                hovertemplate="<b>%{text}</b><br>Z-Score: %{y:.2f}<br>Status: Bankrupt<extra></extra>"
            ), row=1, col=1)
            
        if len(survived_companies) > 0:
            survived_indices = [i for i, ticker in enumerate(df_sorted['ticker']) if ticker in survived_companies['ticker'].values]
            fig.add_trace(go.Scatter(
                x=survived_indices,
                y=survived_companies['z_score'],
                mode='markers',
                name=f'Active Companies ({len(survived_companies)})', 
                marker=dict(color='green', size=12, symbol='circle'),
                text=survived_companies['ticker'],
                hovertemplate="<b>%{text}</b><br>Z-Score: %{y:.2f}<br>Status: Active<extra></extra>"
            ), row=1, col=1)
        
        # Add risk zones
        self._add_risk_zones_to_subplot(fig, len(df_sorted), df_sorted['z_score'].min(), df_sorted['z_score'].max(), row=1, col=1)
        
        # Performance metrics (row 2, col 1)
        metrics = self.calculate_performance_metrics(df)
        fig.add_trace(go.Bar(
            x=['Accuracy', 'Sensitivity', 'Specificity'],
            y=[metrics['accuracy'], metrics['sensitivity'], metrics['specificity']],
            marker_color=['blue', 'red', 'green'],
            name='Performance',
            showlegend=False,
            text=[f"{v:.1%}" for v in [metrics['accuracy'], metrics['sensitivity'], metrics['specificity']]],
            textposition='auto'
        ), row=2, col=1)
        
        # Zone distribution (row 2, col 2)
        zone_counts = self._calculate_zone_distribution(df)
        fig.add_trace(go.Pie(
            labels=['Safe Zone', 'Gray Zone', 'Distress Zone'],
            values=[zone_counts.get('Safe', 0), zone_counts.get('Gray', 0), zone_counts.get('Distress', 0)],
            marker_colors=['green', 'orange', 'red'],
            name='Zone Distribution',
            showlegend=False
        ), row=2, col=2)
        
        # Distribution by outcome (row 3, col 1)
        if len(failed_companies) > 0:
            fig.add_trace(go.Histogram(
                x=failed_companies['z_score'],
                name='Failed',
                marker_color='red',
                opacity=0.7,
                showlegend=False
            ), row=3, col=1)
            
        fig.add_trace(go.Histogram(
            x=survived_companies['z_score'],
            name='Survived', 
            marker_color='green',
            opacity=0.7,
            showlegend=False
        ), row=3, col=1)
        
        # Retail vs Traditional comparison (row 3, col 2)
        if 'traditional_score' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['traditional_score'],
                y=df['z_score'],
                mode='markers',
                name='Retail vs Traditional',
                marker=dict(
                    color=df['z_score'],
                    colorscale='RdYlGn',
                    size=8,
                    showscale=False
                ),
                text=df['ticker'],
                hovertemplate="<b>%{text}</b><br>Traditional: %{x:.2f}<br>Retail: %{y:.2f}<extra></extra>",
                showlegend=False
            ), row=3, col=2)
            
            # Add diagonal line for reference
            min_score = min(df['traditional_score'].min(), df['z_score'].min())
            max_score = max(df['traditional_score'].max(), df['z_score'].max())
            fig.add_trace(go.Scatter(
                x=[min_score, max_score],
                y=[min_score, max_score],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Equal Score Line',
                showlegend=False
            ), row=3, col=2)
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Comprehensive Retail Z-Score Analysis Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=1200,
            template='plotly_white',
            showlegend=True
        )
        
        return fig
    
    def _add_risk_zones_to_subplot(self, fig, n_companies: int, z_min: float, z_max: float, row: int, col: int):
        """Add risk zone shapes to a subplot."""
        # Safe zone
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=n_companies-0.5,
            y0=RETAIL_THRESHOLDS['safe'], y1=z_max + 2,
            fillcolor="rgba(144, 238, 144, 0.2)",
            line=dict(width=0),
            layer="below",
            row=row, col=col
        )
        
        # Gray zone
        fig.add_shape(
            type="rect", 
            x0=-0.5, x1=n_companies-0.5,
            y0=RETAIL_THRESHOLDS['gray_lower'], y1=RETAIL_THRESHOLDS['gray_upper'],
            fillcolor="rgba(255, 255, 0, 0.2)",
            line=dict(width=0),
            layer="below",
            row=row, col=col
        )
        
        # Distress zone
        fig.add_shape(
            type="rect",
            x0=-0.5, x1=n_companies-0.5, 
            y0=z_min - 2, y1=RETAIL_THRESHOLDS['distress'],
            fillcolor="rgba(255, 182, 193, 0.2)",
            line=dict(width=0),
            layer="below",
            row=row, col=col
        )
        
        # Threshold lines
        fig.add_hline(y=RETAIL_THRESHOLDS['safe'], line_dash="dash", line_color="green", row=row, col=col)
        fig.add_hline(y=RETAIL_THRESHOLDS['distress'], line_dash="dash", line_color="red", row=row, col=col)
    
    def _calculate_zone_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of companies across risk zones."""
        def get_zone(z_score):
            if z_score >= RETAIL_THRESHOLDS['safe']:
                return 'Safe'
            elif z_score >= RETAIL_THRESHOLDS['distress']:
                return 'Gray'
            else:
                return 'Distress'
        
        zones = df['z_score'].apply(get_zone)
        return zones.value_counts().to_dict()
    

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Visualize retail Z-Score model performance')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, 
                       help='Output directory for charts')
    parser.add_argument('--data-file', help='Specific validation results file to visualize')
    parser.add_argument('--save-html', action='store_true', default=True,
                       help='Save interactive HTML charts')
    parser.add_argument('--show-chart', action='store_true', default=False,
                       help='Display chart in browser')
    parser.add_argument('--include-stats', action='store_true', default=True,
                       help='Include statistical analysis')
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = RetailZScoreVisualizer(args.output_dir)
    
    # Generate visualizations
    try:
        generated_files = visualizer.visualize_retail_zscores(
            data_file=args.data_file,
            save_html=args.save_html,
            show_chart=args.show_chart,
            include_stats=args.include_stats
        )
        
        print("\nVisualization complete!")
        print("Generated files:")
        for file_type, path in generated_files.items():
            print(f"  {file_type}: {path}")
            
    except Exception as e:
        print(f"Error creating visualizations: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
