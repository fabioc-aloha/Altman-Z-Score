"""
model_validators.py
-----------------
Validation schemas for different Z-Score models.
Currently limited to U.S.-based companies only.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class BaseFinancialData(BaseModel):
    """Base financial data fields common to all models."""
    total_assets: float = Field(..., gt=0)
    total_liabilities: float = Field(..., gt=0)
    retained_earnings: float
    ebit: float

    class Config:
        extra = 'allow'


class ManufacturingData(BaseFinancialData):
    """Validation schema for manufacturing companies (original and private models)."""
    working_capital: float
    sales: float = Field(..., gt=0)


class PublicManufacturingData(ManufacturingData):
    """Additional validation for public manufacturing companies."""
    market_value_equity: float = Field(..., gt=0)


class FinancialInstitutionData(BaseFinancialData):
    """Validation schema for financial institutions."""
    total_equity: float = Field(..., gt=0)
    intangible_assets: Optional[float] = Field(0, ge=0)


def validate_financial_data(model_type: str, data: Dict) -> Dict:
    """
    Validate financial data based on the model type.
    Currently limited to U.S.-based companies only.
    
    Args:
        model_type: Type of Z-Score model
        data: Financial data to validate
    
    Returns:
        Dict: Validated data
    
    Raises:
        ValueError: If validation fails
    """
    try:
        if model_type == 'original':
            return PublicManufacturingData(**data).dict()
        elif model_type == 'private':
            return ManufacturingData(**data).dict()
        elif model_type == 'financial':
            return FinancialInstitutionData(**data).dict()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    except Exception as e:
        raise ValueError(f"Validation failed for {model_type} model: {str(e)}")
