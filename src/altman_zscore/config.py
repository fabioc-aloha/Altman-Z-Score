"""Configuration module for Altman Z-Score analysis."""
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
import calendar
import os
import json
import logging
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import sys

# Add the project root to Python path to support direct imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import configuration from portfolio.py
from portfolio import (
    PORTFOLIO,
    PERIOD_END,
    PRICE_START,
    PRICE_END,
)

def validate_analysis_period(
    period_end: str = PERIOD_END,
    price_start: str = PRICE_START,
    price_end: str = PRICE_END
) -> None:
    """Validate analysis period dates."""
    try:
        start = datetime.strptime(price_start, "%Y-%m-%d")
        end = datetime.strptime(period_end, "%Y-%m-%d")
        price_end_date = datetime.strptime(price_end, "%Y-%m-%d")
        
        if start > end:
            raise ValueError("PRICE_START cannot be after PERIOD_END")
            
        if price_end_date > end:
            raise ValueError("PRICE_END cannot be after PERIOD_END")
        
        # Quarter validation
        month = end.month 
        day = end.day
        if month not in [3, 6, 9, 12] or day not in [31, 30]:
            raise ValueError(
                "PERIOD_END must be the last day of a quarter "
                "(March 31, June 30, September 30, or December 31)"
            )
        
        # Date range validation
        days_diff = (price_end_date - start).days
        if days_diff < 60 or days_diff > 100:
            logger.warning(
                f"Price comparison period is {days_diff} days. "
                "Recommended period is 90 days (one quarter)."
            )
        
        # Future date warning
        today = datetime.now()
        if end > today:
            logger.warning(f"Analysis period end date {period_end} is in the future")
            
    except ValueError as e:
        if "unconverted data remains" in str(e) or "does not match format" in str(e):
            raise ValueError(f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}")
        raise

# Validate dates with enhanced checks
validate_analysis_period()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# API request configuration
MAX_BATCH_SIZE = 5  # Maximum number of concurrent requests
FALLBACK_DELAY = 1  # Delay in seconds before trying fallback methods
MAX_RETRIES = 3  # Maximum number of retry attempts

def get_quarter_dates(quarter: int, year: int) -> Tuple[str, str]:
    """Get start and end dates for a specific quarter."""
    if quarter not in range(1, 5):
        raise ValueError("Quarter must be between 1 and 4")
        
    month = (quarter - 1) * 3 + 1
    quarter_start = datetime(year, month, 1)
    last_month = quarter * 3
    _, last_day = calendar.monthrange(year, last_month)
    quarter_end = datetime(year, last_month, last_day)
    
    return quarter_start.strftime("%Y-%m-%d"), quarter_end.strftime("%Y-%m-%d")

def get_current_dates() -> Tuple[str, str, str]:
    """Get default dates for analysis."""
    today = datetime.now()
    month = (today.month - 1) // 3 * 3 + 3  # Round to last complete quarter
    year = today.year
    
    if month == 12:
        _, last_day = calendar.monthrange(year, 12)
        quarter_end = datetime(year, 12, last_day)
    else:
        month += 1  # First month of next quarter
        _, last_day = calendar.monthrange(year, month - 1)
        quarter_end = datetime(year, month - 1, last_day)
    
    price_start = quarter_end - timedelta(days=90)
    price_end = quarter_end
    
    return (
        price_start.strftime("%Y-%m-%d"),
        price_end.strftime("%Y-%m-%d"),
        quarter_end.strftime("%Y-%m-%d")
    )

class ZScoreModel(Enum):
    """Available Z-score models."""
    ORIGINAL = "original"  # Public manufacturing companies
    PRIVATE = "private"    # Private manufacturing companies
    SERVICE = "service"    # Non-manufacturing/service companies
    EM = "emerging"       # Emerging markets

# Z-score model parameters
ZSCORE_MODELS = {
    ZScoreModel.ORIGINAL: {
        "X1": 1.2,  # Working capital/Total assets
        "X2": 1.4,  # Retained earnings/Total assets
        "X3": 3.3,  # EBIT/Total assets
        "X4": 0.6,  # Market value of equity/Total liabilities
        "X5": 0.999,  # Sales/Total assets
        "thresholds": {
            "safe": 2.99,
            "grey": 1.81,
            "distress": 1.81
        }
    },
    ZScoreModel.PRIVATE: {
        "X1": 0.717,  # Working capital/Total assets
        "X2": 0.847,  # Retained earnings/Total assets
        "X3": 3.107,  # EBIT/Total assets
        "X4": 0.420,  # Book value of equity/Total liabilities
        "X5": 0.998,  # Sales/Total assets
        "thresholds": {
            "safe": 2.9,
            "grey": 1.23,
            "distress": 1.23
        }
    },
    ZScoreModel.SERVICE: {
        "X1": 6.56,   # Working capital/Total assets
        "X2": 3.26,   # Retained earnings/Total assets
        "X3": 6.72,   # EBIT/Total assets
        "X4": 1.05,   # Book value of equity/Total liabilities
        "X5": 0,      # Sales/Total assets (not used)
        "thresholds": {
            "safe": 2.6,
            "grey": 1.1,
            "distress": 1.1
        }
    },
    ZScoreModel.EM: {
        "X1": 3.25,   # Working capital/Total assets
        "X2": 6.25,   # Retained earnings/Total assets
        "X3": 3.25,   # EBIT/Total assets
        "X4": 1.05,   # Book value of equity/Total liabilities
        "X5": 0,      # Sales/Total assets (not used)
        "thresholds": {
            "safe": 2.99,
            "grey": 1.81,
            "distress": 1.81
        }
    }
}

# Default model
DEFAULT_ZSCORE_MODEL = ZScoreModel.ORIGINAL

@dataclass
class ExcludedTicker:
    """Information about an excluded ticker."""
    ticker: str
    exclusion_date: datetime
    reason: str
    cik: Optional[str] = None
    last_attempt: Optional[datetime] = None
    retry_count: int = 0

@dataclass
class PortfolioHealth:
    """Portfolio health metrics."""
    total_tickers: int
    excluded_count: int
    active_count: int
    cik_success_rate: float
    data_quality_score: float
    last_update: datetime

class PortfolioConfig:
    """Manages portfolio configuration including exclusions."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize portfolio configuration.
        
        Args:
            config_dir: Directory for configuration files.
        """
        self.config_dir = Path(config_dir or Path.cwd())
        self.excluded_file = self.config_dir / "excluded_tickers.json"
        self.portfolio_file = self.config_dir / "portfolio_config.json"
        self.excluded_tickers: Dict[str, ExcludedTicker] = {}
        self.load_config()
        
    def load_config(self):
        """Load configuration from files."""
        if self.excluded_file.exists():
            try:
                with open(self.excluded_file) as f:
                    excluded_data = json.load(f)
                    self.excluded_tickers = {
                        ticker: ExcludedTicker(
                            ticker=ticker,
                            exclusion_date=datetime.fromisoformat(data["exclusion_date"]),
                            reason=data["reason"],
                            cik=data.get("cik"),
                            last_attempt=datetime.fromisoformat(data["last_attempt"]) 
                                if data.get("last_attempt") else None,
                            retry_count=data.get("retry_count", 0)
                        )
                        for ticker, data in excluded_data.items()
                    }
            except Exception as e:
                logger.error(f"Error loading excluded tickers: {e}")
                self.excluded_tickers = {}
    
    def save_config(self):
        """Save configuration to files."""
        excluded_data = {
            ticker: {
                "exclusion_date": exc.exclusion_date.isoformat(),
                "reason": exc.reason,
                "cik": exc.cik,
                "last_attempt": exc.last_attempt.isoformat() if exc.last_attempt else None,
                "retry_count": exc.retry_count
            }
            for ticker, exc in self.excluded_tickers.items()
        }
        
        with open(self.excluded_file, "w") as f:
            json.dump(excluded_data, f, indent=4)
            
    def exclude_ticker(self, ticker: str, reason: str, cik: Optional[str] = None):
        """
        Add a ticker to the excluded list.
        
        Args:
            ticker: Stock ticker symbol
            reason: Reason for exclusion
            cik: Optional CIK number if known
        """
        self.excluded_tickers[ticker] = ExcludedTicker(
            ticker=ticker,
            exclusion_date=datetime.now(),
            reason=reason,
            cik=cik
        )
        self.save_config()
        
    def get_portfolio_health(self) -> PortfolioHealth:
        """Get portfolio health metrics."""
        total = len(PORTFOLIO)
        excluded = len(self.excluded_tickers)
        active = total - excluded
        
        # Calculate CIK success rate
        cik_success = sum(1 for t in self.excluded_tickers.values() 
                         if t.reason != "CIK lookup failed")
        cik_rate = (total - (excluded - cik_success)) / total if total > 0 else 0
        
        # Simple data quality score for now
        quality_score = active / total if total > 0 else 0
        
        return PortfolioHealth(
            total_tickers=total,
            excluded_count=excluded,
            active_count=active,
            cik_success_rate=cik_rate,
            data_quality_score=quality_score,
            last_update=datetime.now()
        )
        
    def get_active_portfolio(self) -> List[str]:
        """Get list of active (non-excluded) tickers."""
        return [ticker for ticker in PORTFOLIO 
                if ticker not in self.excluded_tickers]

def validate_portfolio(portfolio: list[str]) -> bool:
    """
    Validate the portfolio configuration.
    
    Args:
        portfolio (list[str]): List of stock tickers
        
    Returns:
        bool: True if portfolio is valid
        
    Raises:
        ValueError: If portfolio configuration is invalid
    """
    if not portfolio:
        raise ValueError("PORTFOLIO must not be empty")
    
    # Check that we have at least some active tickers
    active_tickers = portfolio_config.get_active_portfolio()
    if not active_tickers:
        raise ValueError("No active tickers in portfolio")
    
    # Basic validation of ticker format
    for ticker in portfolio:
        if not isinstance(ticker, str) or not ticker or not ticker.isalpha():
            logger.warning(f"Invalid ticker format: {ticker}")
            portfolio_config.exclude_ticker(
                ticker=ticker,
                reason="Invalid ticker format"
            )
    
    return True

# Initialize portfolio configuration
portfolio_config = PortfolioConfig()


