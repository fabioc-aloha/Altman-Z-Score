# All imports should be at the top of the file, per Python best practices.

# Pydantic schemas for validating SEC and Yahoo data for Altman Z-Score analysis
from typing import Optional

from pydantic import BaseModel


class QuarterlyFinancials(BaseModel):
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
    valid: bool
    error: Optional[str] = None


# Add more schemas as needed for price data, etc.
