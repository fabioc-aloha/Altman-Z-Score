"""
Base schema definitions for API response validation.

Defines base response types, error handling, validation error, and data quality metrics for use across API schemas.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseStatus(Enum):
    """Enumeration of API response status values."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  # For batch responses where some items succeeded


@dataclass
class BaseResponse:
    """Base class for all API responses.

    Attributes:
        status (ResponseStatus): The response status.
        timestamp (datetime): The time the response was generated.
    """

    status: ResponseStatus
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseResponse":
        """Create a BaseResponse object from a dictionary.

        Args:
            data (dict): Dictionary containing response data.

        Returns:
            BaseResponse: Instantiated response object.
        """
        return cls(
            status=ResponseStatus[data.get("status", "ERROR").upper()],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
        )


@dataclass
class ErrorResponse(BaseResponse):
    """Error response with details for failed API calls.

    Attributes:
        error_code (str): Error code identifier.
        error_message (str): Human-readable error message.
        retry_after (float, optional): Seconds to wait before retrying.
        errors (list, optional): List of error details.
        warnings (list, optional): List of warning messages.
    """

    error_code: str
    error_message: str
    retry_after: Optional[float] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorResponse":
        """Create an ErrorResponse object from a dictionary.

        Args:
            data (dict): Dictionary containing error response data.

        Returns:
            ErrorResponse: Instantiated error response object.
        """
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
    """Details of a validation error for a specific field.

    Attributes:
        field (str): Name of the field with the error.
        message (str): Description of the validation error.
        value (Any): The value that failed validation.
        code (str): Error code or type.
    """

    field: str
    message: str
    value: Any
    code: str


@dataclass
class DataQualityMetrics:
    """Metrics for assessing data quality in API responses.

    Attributes:
        completeness (float): Percentage of required fields present (0-1).
        accuracy (float): Estimated accuracy based on validation rules (0-1).
        timeliness (float): Recency of the data (0-1).
        consistency (float): Internal consistency score (0-1).
    """

    completeness: float  # Percentage of required fields present
    accuracy: float  # Estimated accuracy based on validation rules
    timeliness: float  # How recent the data is (0-1)
    consistency: float  # Internal consistency score (0-1)
