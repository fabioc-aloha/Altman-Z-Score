"""Base schema definitions for API response validation."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseStatus(Enum):
    """API response status."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  # For batch responses where some items succeeded


@dataclass
class BaseResponse:
    """Base class for all API responses."""

    status: ResponseStatus
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseResponse":
        """Create response object from dictionary."""
        return cls(
            status=ResponseStatus[data.get("status", "ERROR").upper()],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
        )


@dataclass
class ErrorResponse(BaseResponse):
    """Error response with details."""

    error_code: str
    error_message: str
    retry_after: Optional[float] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorResponse":
        """Create error response from dictionary."""
        base = super().from_dict(data)
        return cls(
            status=base.status,
            timestamp=base.timestamp,
            error_code=data["error_code"],
            error_message=data["error_message"],
            retry_after=data.get("retry_after"),
            errors=data.get("errors"),
            warnings=data.get("warnings"),
        )


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    message: str
    value: Any
    code: str


@dataclass
class DataQualityMetrics:
    """Metrics for assessing data quality."""

    completeness: float  # Percentage of required fields present
    accuracy: float  # Estimated accuracy based on validation rules
    timeliness: float  # How recent the data is (0-1)
    consistency: float  # Internal consistency score (0-1)
