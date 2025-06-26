"""
Custom exceptions for the Altman Z-Score package.

This module contains custom exception classes for specific error conditions
encountered throughout the Z-Score analysis pipeline.
"""

class ZScoreError(Exception):
    """Base exception class for all Z-Score related errors."""
    pass


class AltmanZScoreError(ZScoreError):
    """Generic exception for Altman Z-Score pipeline errors."""
    pass


class DataFetchError(ZScoreError):
    """Exception raised for errors in data fetching layer."""
    
    def __init__(self, message: str, source: str = None, status_code: int = None):
        self.source = source
        self.status_code = status_code
        super().__init__(message)


class APIRateLimitError(DataFetchError):
    """Exception raised for API rate limit errors (HTTP 401, 429)."""
    
    def __init__(self, message: str, source: str = None, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, source=source, status_code=429)


class FieldMappingError(ZScoreError):
    """Exception raised for field mapping errors."""
    pass


class InsufficientDataError(ZScoreError):
    """Exception raised when there is insufficient data for analysis."""
    
    def __init__(self, message: str, min_required: int = None, available: int = None):
        self.min_required = min_required
        self.available = available
        super().__init__(message)


class ModelSelectionError(ZScoreError):
    """Exception raised for model selection errors."""
    pass


class SectorExclusionError(ModelSelectionError):
    """Exception raised when a company's sector is excluded from Z-Score analysis."""
    
    def __init__(self, message: str, sic_code: str = None, sector: str = None):
        self.sic_code = sic_code
        self.sector = sector
        super().__init__(message)


class CalculationError(ZScoreError):
    """Exception raised for Z-Score calculation errors."""
    pass


class ValidationError(ZScoreError):
    """Exception raised for validation errors."""
    pass


class ComponentValidationError(ValidationError):
    """Exception raised when a Z-Score component validation fails."""
    
    def __init__(self, message: str, component: str = None, value: float = None):
        self.component = component
        self.value = value
        super().__init__(message)


class NonUSCompanyError(ZScoreError):
    """Exception raised when attempting to analyze a non-U.S. company."""
    
    def __init__(self, message: str, ticker: str = None, country: str = None):
        self.ticker = ticker
        self.country = country
        super().__init__(message)


class CacheError(ZScoreError):
    """Exception raised for cache-related errors."""
    pass


class OutputGenerationError(ZScoreError):
    """Exception raised for output generation errors."""
    pass


class AIAnalysisError(ZScoreError):
    """Exception raised for AI analysis and narrative generation errors."""
    
    def __init__(self, message: str, source: str = None, response_details: dict = None):
        self.source = source
        self.response_details = response_details or {}
        super().__init__(message)


class PipelineError(ZScoreError):
    """Exception raised for pipeline orchestration errors."""
    pass


class ConfigurationError(ZScoreError):
    """Exception raised for configuration errors."""
    pass


class UnsupportedFeatureError(ZScoreError):
    """Exception raised when attempting to use an unsupported feature."""
    pass


class AnalysisError(ZScoreError):
    """Exception raised for analysis engine errors."""
    pass


class ValidationError(ZScoreError):
    """Exception raised for data validation errors."""
    pass


# This file will be expanded during refactoring with additional exceptions
