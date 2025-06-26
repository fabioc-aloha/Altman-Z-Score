"""Enhanced validation messages and guidance for Altman Z-Score model validation errors.

This module provides detailed error messages and troubleshooting guidance for model validation failures,
helping users understand and fix data issues.
"""

from typing import Dict, Optional
from decimal import Decimal

# Validation thresholds and ranges
VALIDATION_RANGES = {
    "working_capital_to_assets": (-1.0, 1.0),
    "retained_earnings_to_assets": (-2.0, 1.0),
    "ebit_to_assets": (-1.0, 1.0),
    "equity_to_liabilities": (0.0, 10.0),
    "sales_to_assets": (0.0, 5.0),
    "liquid_assets_to_total_assets": (0.0, 1.0),
    "loan_loss_reserves_to_loans": (0.0, 0.2),
    "operating_expenses_to_income": (0.0, 2.0),
    "equity_to_total_debt": (0.0, 1.0),
    "core_revenue_to_assets": (0.0, 0.5)
}

TROUBLESHOOTING_GUIDANCE = {
    "working_capital_to_assets": """
    Working Capital to Total Assets ratio outside normal range.
    Common causes:
    - Negative working capital (current liabilities > current assets)
    - Missing or incorrect current assets/liabilities data
    - Recent major asset purchase or debt repayment
    
    Troubleshooting steps:
    1. Verify current assets and liabilities from financial statements
    2. Check for any significant one-time events affecting working capital
    3. Consider seasonal variations in working capital
    4. For early-stage companies, confirm capital structure
    """,
    
    "retained_earnings_to_assets": """
    Retained Earnings to Total Assets ratio outside normal range.
    Common causes:
    - Accumulated losses in early-stage companies
    - Recent dividends or stock buybacks
    - Merger/acquisition effects
    
    Troubleshooting steps:
    1. Check company age and stage (startups often have negative retained earnings)
    2. Review recent capital allocation decisions
    3. Verify retained earnings calculation includes all adjustments
    4. For loss-making companies, consider using Z' model
    """,
    
    "ebit_to_assets": """
    EBIT to Total Assets ratio outside normal range.
    Common causes:
    - Operating losses
    - Significant non-operating income/expenses
    - Recent large asset purchases
    
    Troubleshooting steps:
    1. Verify EBIT calculation includes all operating items
    2. Check for one-time charges or gains
    3. Review asset base changes
    4. For pre-revenue companies, consider alternative metrics
    """,
    
    "equity_to_liabilities": """
    Market Value of Equity to Book Value of Liabilities ratio outside normal range.
    Common causes:
    - Market volatility affecting equity value
    - Complex debt structures
    - Recent capital raises or debt issuance
    
    Troubleshooting steps:
    1. Verify market capitalization data
    2. Check all debt obligations are included
    3. Consider off-balance sheet liabilities
    4. For private companies, use book value of equity
    """,
    
    "sales_to_assets": """
    Sales to Total Assets ratio outside normal range.
    Common causes:
    - Asset-heavy business model
    - Recent major capital investments
    - Seasonal business fluctuations
    
    Troubleshooting steps:
    1. Compare ratio to industry averages
    2. Check for recent asset acquisitions
    3. Consider revenue recognition policies
    4. For service companies, evaluate asset utilization
    """,
    
    # Financial institution specific metrics
    "liquid_assets_to_total_assets": """
    Liquid Assets to Total Assets ratio outside normal range.
    Common causes:
    - Misclassification of liquid assets
    - Recent major investments
    - Regulatory requirement changes
    
    Troubleshooting steps:
    1. Verify liquid asset classification
    2. Check compliance with regulatory requirements
    3. Review investment portfolio changes
    4. Consider timing of major transactions
    """,
    
    "loan_loss_reserves_to_loans": """
    Loan Loss Reserves to Loans ratio outside normal range.
    Common causes:
    - Changes in credit risk assessment
    - Economic cycle effects
    - Regulatory requirement changes
    
    Troubleshooting steps:
    1. Review loan portfolio quality
    2. Check recent provision methodology changes
    3. Compare to peer institutions
    4. Consider macroeconomic factors
    """
}

def get_validation_message(metric: str, value: Decimal) -> str:
    """
    Generate a detailed validation message for a metric value outside normal range.
    
    Args:
        metric: The name of the financial metric
        value: The actual value of the metric
    
    Returns:
        A detailed message explaining the issue and providing troubleshooting guidance
    """
    if metric not in VALIDATION_RANGES:
        return f"Unknown metric: {metric}"
        
    min_val, max_val = VALIDATION_RANGES[metric]
    guidance = TROUBLESHOOTING_GUIDANCE.get(metric, "No specific guidance available.")
    
    message = f"""
    Validation Error for {metric}:
    - Actual value: {value}
    - Expected range: [{min_val}, {max_val}]
    
    {guidance}
    """
    
    return message

def validate_metric(metric: str, value: Decimal) -> Optional[str]:
    """
    Validate a single metric value and return an error message if invalid.
    
    Args:
        metric: The name of the financial metric
        value: The value to validate
    
    Returns:
        None if valid, or an error message if invalid
    """
    if metric not in VALIDATION_RANGES:
        return f"Unknown metric: {metric}"
        
    min_val, max_val = VALIDATION_RANGES[metric]
    if not (min_val <= float(value) <= max_val):
        return get_validation_message(metric, value)
    
    return None

def validate_financial_data(data: Dict[str, Decimal]) -> Dict[str, str]:
    """
    Validate all financial metrics in the data and return validation messages.
    
    Args:
        data: Dictionary of financial metrics and their values
    
    Returns:
        Dictionary of validation error messages for invalid metrics
    """
    validation_messages = {}
    
    for metric, value in data.items():
        message = validate_metric(metric, value)
        if message:
            validation_messages[metric] = message
            
    return validation_messages
