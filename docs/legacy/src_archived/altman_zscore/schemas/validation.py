"""
Pydantic schemas for validating SEC and Yahoo data for Altman Z-Score analysis.

Defines schemas for quarterly financials and validation results used in the data validation pipeline.
"""

from typing import Optional

from pydantic import BaseModel


class QuarterlyFinancials(BaseModel):
    """Schema for quarterly financial statement data.

    Attributes:
        period_end (str): Period end date (YYYY-MM-DD).
        total_assets (float): Total assets for the period.
        current_assets (float): Current assets for the period.
        current_liabilities (float): Current liabilities for the period.
        retained_earnings (float): Retained earnings for the period.
        ebit (float): Earnings before interest and taxes.
        sales (float): Sales revenue for the period.
        market_value_equity (float, optional): Market value of equity (for Z-Score MVE).
        industry (str, optional): Industry classification.
        maturity (str, optional): Company maturity/stage.
    """

    period_end: str  # YYYY-MM-DD
    total_assets: float
    current_assets: float
    current_liabilities: float
    retained_earnings: float
    ebit: float
    sales: float
    market_value_equity: Optional[float] = None  # For Z-Score MVE
    industry: Optional[str] = None
    maturity: Optional[str] = None


class QuarterlyValidationResult(BaseModel):
    """Schema for the result of validating a single quarter's data.

    Attributes:
        valid (bool): Whether the data is valid.
        error (str, optional): Error message if validation failed.
    """

    valid: bool
    error: Optional[str] = None


# Add more schemas as needed for price data, etc.
