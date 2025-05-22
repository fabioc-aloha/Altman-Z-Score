"""API response schema package."""
from .base import (
    BaseResponse,
    ResponseStatus,
    ErrorResponse,
    ValidationError,
    DataQualityMetrics
)
from .edgar import (
    FilingInfo,
    CompanyInfo,
    XBRLData,
    EDGARResponse,
    CompanyResponse,
    FilingResponse,
    SearchResponse
)
from .yahoo import (
    MarketQuote,
    HistoricalPrice,
    CompanyProfile,
    YahooResponse,
    QuoteResponse,
    HistoryResponse,
    ProfileResponse
)
from .validation import ResponseValidator

__all__ = [
    # Base schemas
    'BaseResponse',
    'ResponseStatus',
    'ErrorResponse',
    'ValidationError',
    'DataQualityMetrics',
    # SEC EDGAR schemas
    'FilingInfo',
    'CompanyInfo',
    'XBRLData',
    'EDGARResponse',
    'CompanyResponse',
    'FilingResponse',
    'SearchResponse',
    # Yahoo Finance schemas
    'MarketQuote',
    'HistoricalPrice',
    'CompanyProfile',
    'YahooResponse',
    'QuoteResponse',
    'HistoryResponse',
    'ProfileResponse',
    # Validation
    'ResponseValidator',
]
