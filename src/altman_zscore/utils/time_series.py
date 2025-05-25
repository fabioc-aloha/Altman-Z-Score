"""Time series analysis utilities for financial data."""
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import numpy as np
import pandas as pd
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class TrendMetrics:
    """Container for trend analysis metrics."""
    slope: float
    r_squared: float
    mean: float
    std_dev: float
    z_score: float
    periods: int

@dataclass
class SeasonalityMetrics:
    """Container for seasonality metrics."""
    seasonal_factors: Dict[str, float]
    strength: float  # 0-1 score indicating seasonality strength
    period_length: int

@dataclass
class AnomalyScore:
    """Container for anomaly detection scores."""
    score: float  # How anomalous the value is (higher = more anomalous)
    threshold: float  # Current threshold for anomaly detection
    is_anomaly: bool  # Whether the score exceeds the threshold
    contributing_factors: List[str]  # What factors contributed to the anomaly

class TimeSeriesAnalyzer:
    """Analyzer for financial time series data."""
    
    def __init__(self, seasonality_periods: int = 4):
        """Initialize time series analyzer.
        
        Args:
            seasonality_periods: Number of periods for seasonality analysis (default=4 for quarterly)
        """
        self.seasonality_periods = seasonality_periods
        
    def calculate_trend(
        self,
        values: List[Union[float, Decimal]],
        dates: List[datetime]
    ) -> TrendMetrics:
        """Calculate trend metrics for a time series.
        
        Args:
            values: List of numeric values (float or Decimal)
            dates: List of corresponding dates
            
        Returns:
            TrendMetrics object containing trend analysis
            
        Raises:
            ValueError: If length of values and dates don't match or if fewer than 2 points
        """
        if len(values) != len(dates):
            raise ValueError("Length of values and dates must match")
        
        if len(values) < 2:
            raise ValueError("Need at least 2 points for trend analysis")
            
        # Convert dates to numeric values (days since first date)
        first_date = min(dates)
        x = np.array([(d - first_date).days for d in dates], dtype=np.float64)
        
        # Convert values to numpy array, handling both float and Decimal
        y = np.array([float(v) if isinstance(v, Decimal) else float(v) for v in values], dtype=np.float64)
        
        # Calculate linear regression
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept
        
        # Calculate R-squared
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        # Calculate z-score of latest value
        mean = float(np.mean(y))
        std_dev = float(np.std(y))
        latest_z_score = float((y[-1] - mean) / std_dev if std_dev > 0 else 0.0)
        
        return TrendMetrics(
            slope=float(slope),
            r_squared=float(r_squared),
            mean=mean,
            std_dev=std_dev,
            z_score=float(latest_z_score),
            periods=len(values)
        )
        
    def detect_seasonality(
        self,
        values: List[Union[float, Decimal]],
        dates: List[datetime]
    ) -> SeasonalityMetrics:
        """Detect seasonality in time series data.
        
        Args:
            values: List of numeric values
            dates: List of corresponding dates
            
        Returns:
            SeasonalityMetrics object containing seasonal analysis
        """
        if len(values) != len(dates):
            raise ValueError("Length of values and dates must match")
            
        # Convert values to numpy array
        y = np.array([float(v) if isinstance(v, Decimal) else float(v) for v in values])
        
        # Initialize seasonal factors
        seasonal_factors: Dict[str, float] = {}
        quarters = pd.Series([pd.Timestamp(d).quarter for d in dates])
        
        # Calculate seasonal factors by quarter
        for quarter in range(1, 5):
            quarter_values = y[quarters == quarter]
            if len(quarter_values) > 0:
                seasonal_factors[f"Q{quarter}"] = float(np.mean(quarter_values))
        
        # Normalize seasonal factors
        if seasonal_factors:
            mean_factor = np.mean(list(seasonal_factors.values()))
            if mean_factor != 0:
                seasonal_factors = {k: float(v/mean_factor) for k, v in seasonal_factors.items()}
            
        # Calculate seasonality strength
        if len(seasonal_factors) > 1:  # Need at least 2 quarters for seasonality
            factor_values = np.array([float(v) for v in seasonal_factors.values()])
            variance_factors = np.var(factor_values)
            seasonality_strength = float(np.clip(variance_factors, 0, 1))
        else:
            seasonality_strength = 0.0
            
        return SeasonalityMetrics(
            seasonal_factors=seasonal_factors,
            strength=seasonality_strength,
            period_length=self.seasonality_periods
        )
        
    def detect_anomalies(
        self,
        values: List[Union[float, Decimal]],
        dates: List[datetime],
        z_threshold: float = 3.0
    ) -> List[AnomalyScore]:
        """Detect anomalies in time series data.
        
        Args:
            values: List of numeric values
            dates: List of corresponding dates
            z_threshold: Z-score threshold for anomaly detection
            
        Returns:
            List of AnomalyScore objects for each point
        """
        if len(values) != len(dates):
            raise ValueError("Length of values and dates must match")
            
        # Convert values to numpy array
        y = np.array([float(v) if isinstance(v, Decimal) else float(v) for v in values])
        
        scores: List[AnomalyScore] = []
        
        # Calculate rolling statistics
        window = 4  # Use quarterly window
        for i in range(len(y)):
            # Get local window
            start_idx = max(0, i - window)
            window_values = y[start_idx:i+1]
            
            if len(window_values) < 2:
                continue
                
            # Calculate local statistics
            local_mean = float(np.mean(window_values))
            local_std = float(np.std(window_values))
            
            if local_std == 0:
                continue
                
            # Calculate z-score
            z_score = float((y[i] - local_mean) / local_std)
            
            # Determine contributing factors
            factors = []
            if abs(z_score) > z_threshold:
                if z_score > 0:
                    factors.append("Unusually high value")
                else:
                    factors.append("Unusually low value")
                    
                # Check for rapid change
                if i > 0:
                    change = float((y[i] - y[i-1]) / y[i-1] if y[i-1] != 0 else 0)
                    if abs(change) > 0.5:  # 50% change threshold
                        factors.append("Rapid change from previous period")
            
            scores.append(AnomalyScore(
                score=float(abs(z_score)),
                threshold=float(z_threshold),
                is_anomaly=abs(z_score) > z_threshold,
                contributing_factors=factors
            ))
            
        return scores
