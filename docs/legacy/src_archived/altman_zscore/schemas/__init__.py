"""API response schema package."""

from .base import BaseResponse, DataQualityMetrics, ErrorResponse, ResponseStatus, ValidationError
from .edgar import CompanyInfo, CompanyResponse, EDGARResponse, FilingInfo, FilingResponse, SearchResponse, XBRLData
from .yahoo import (
    CompanyProfile,
    HistoricalPrice,
    HistoryResponse,
    MarketQuote,
    ProfileResponse,
    QuoteResponse,
    YahooResponse,
)

__all__ = [
    # Base schemas
    "BaseResponse",
    "ResponseStatus",
    "ErrorResponse",
    "ValidationError",
    "DataQualityMetrics",
    # SEC EDGAR schemas
    "FilingInfo",
    "CompanyInfo",
    "XBRLData",
    "EDGARResponse",
    "CompanyResponse",
    "FilingResponse",
    "SearchResponse",
    # Yahoo Finance schemas
    "MarketQuote",
    "HistoricalPrice",
    "CompanyProfile",
    "YahooResponse",
    "QuoteResponse",
    "HistoryResponse",
    "ProfileResponse",
]
