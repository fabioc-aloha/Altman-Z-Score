"""Configuration module for Altman Z-Score analysis."""
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import calendar
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    
    # Basic validation of ticker format
    for ticker in portfolio:
        if not isinstance(ticker, str) or not ticker or not ticker.isalpha():
            raise ValueError(f"Invalid ticker: {ticker}")
    
    return True

def get_quarter_dates(quarter: int, year: int) -> Tuple[str, str]:
    """Get the start and end dates for a given quarter.
    
    Args:
        quarter (int): Quarter number (1-4)
        year (int): Year
        
    Returns:
        Tuple[str, str]: Start and end dates in YYYY-MM-DD format
        
    Raises:
        ValueError: If quarter is not between 1 and 4
    """
    if quarter < 1 or quarter > 4:
        raise ValueError("Quarter must be between 1 and 4")
        
    end_month = quarter * 3
    start_month = end_month - 2  # First month of the quarter
    
    _, end_day = calendar.monthrange(year, end_month)
    
    return (
        f"{year}-{start_month:02d}-01",  # Start of quarter
        f"{year}-{end_month:02d}-{end_day:02d}"  # End of quarter
    )

def get_current_dates() -> Tuple[str, str, str]:
    """Get the dates for analysis based on current date.
    
    Returns:
        Tuple[str, str, str]: (price_start_date, price_end_date, period_end_date)
    """
    current_date = datetime.now()
    current_quarter = (current_date.month - 1) // 3 + 1

    # Set dates based on previous quarter
    if current_quarter == 1:
        # Use Q4 of previous year
        year = current_date.year - 1
        price_start, period_end = get_quarter_dates(4, year)
    else:
        # Use previous quarter of current year
        year = current_date.year
        price_start, period_end = get_quarter_dates(current_quarter - 1, year)
    
    price_end = period_end
    return price_start, price_end, period_end

# Top 20 generative-AI companies to analyze
PORTFOLIO: list[str] = [
    "MSFT",   # Microsoft Corporation
    "GOOGL",  # Alphabet Inc.
    "AMZN",   # Amazon.com, Inc.
    "META",   # Meta Platforms, Inc.
    "NVDA",   # NVIDIA Corporation
    "IBM",    # International Business Machines Corporation
    "ORCL",   # Oracle Corporation
    "CRM",    # Salesforce, Inc.
    "ADBE",   # Adobe Inc.
    "SNOW",   # Snowflake Inc.
    "PLTR",   # Palantir Technologies Inc.
    "AI",     # C3.ai, Inc.
    # "SPLK",   # Splunk Inc. - Acquired by Cisco in March 2024
    "DDOG",   # Datadog, Inc.
    "PATH",   # UiPath, Inc.
    "NOW",    # ServiceNow, Inc.
    "CRWD",   # CrowdStrike Holdings, Inc.
    "INTU",   # Intuit Inc.
    "UPST",   # Upstart Holdings, Inc.
    # "SOUN"    # SoundHound AI, Inc. - Removed (recent IPO, insufficient data)
]

# Z-score model parameters
ZSCORE_PARAMS = {
    'X1_WEIGHT': 1.2,  # Working Capital/Total Assets
    'X2_WEIGHT': 1.4,  # Retained Earnings/Total Assets
    'X3_WEIGHT': 3.3,  # EBIT/Total Assets
    'X4_WEIGHT': 0.6,  # Market Value of Equity/Total Liabilities
    'X5_WEIGHT': 1.0   # Sales/Total Assets
}

# Z-score interpretation thresholds
ZSCORE_THRESHOLDS = {
    'SAFE': 2.99,      # Above this is "Safe Zone"
    'GREY': 1.81       # Between this and SAFE is "Grey Zone", below is "Distress Zone"
}
