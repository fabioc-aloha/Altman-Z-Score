from pydantic import BaseModel, Field
from typing import Optional

class QuarterlyFinancials(BaseModel):
    period_end: str  # YYYY-MM-DD
    total_assets: float
    current_assets: float
    current_liabilities: float
    retained_earnings: float
    ebit: float
    sales: float
    market_value_equity: Optional[float] = None  # For Z-Score MVE

class QuarterlyValidationResult(BaseModel):
    valid: bool
    error: Optional[str] = None

# Add more schemas as needed for price data, etc.