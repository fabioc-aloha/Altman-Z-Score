"""Base schema definitions for API response validation."""
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """Base model for all API responses."""
    timestamp: datetime = Field(..., description="Response timestamp")
    status_code: int = Field(..., description="HTTP status code")
    raw_response: Dict[str, Any] = Field(..., description="Original response data")

    class Config:
        arbitrary_types_allowed = True

class DataQualityMetrics(BaseModel):
    """Metrics indicating data quality."""
    completeness: float = Field(..., ge=0, le=1)
    accuracy: float = Field(..., ge=0, le=1)
    timeliness: float = Field(..., ge=0, le=1)
    consistency: float = Field(..., ge=0, le=1)

class ValidationError(BaseModel):
    """Model for validation error details."""
    field: str
    message: str
    value: Any
    code: str
