"""
Data models for the Altman Z-Score package.

This module contains data classes and types used throughout the Z-Score
analysis pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union


@dataclass
class FilteredSecData:
    """
    Data class for filtered SEC EDGAR data.
    """
    quarters: List[Dict]
    metadata: Dict
    start_date: str
    total_quarters_available: int
    filtered_quarters_count: int
    company_profile: Dict = field(default_factory=dict)


@dataclass
class FilteredYahooData:
    """
    Data class for filtered Yahoo Finance data.
    """
    market_data: Dict
    price_history: List[Dict]
    start_date: str
    end_date: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class MergedFinancialData:
    """
    Data class for merged financial data from FMP and Yahoo sources.
    
    Strategic Focus: FMP provides pre-calculated ratios, Yahoo provides market data.
    No complex field mapping required.
    """
    ticker: str
    timestamp: str
    
    # Z-Score ratios (pre-calculated by FMP)
    working_capital_ratio: Optional[float] = None
    retained_earnings_ratio: Optional[float] = None
    ebit_ratio: Optional[float] = None
    asset_turnover: Optional[float] = None
    
    # Market data (from Yahoo Finance)
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None
      # Additional ratios for context
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    inventory_ratio: Optional[float] = None  # For company classification
    
    # Data quality metrics
    data_quality_score: Optional[float] = None
    
    # Raw data for debugging/validation
    raw_fmp_data: Optional[Dict[str, Any]] = None
    raw_yahoo_data: Optional[Dict[str, Any]] = None
    
    # Legacy compatibility (deprecated)
    quarters: Optional[List[Dict]] = None
    company_profile: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class CanonicalQuarter:
    """
    Data class for a canonical quarter with standardized fields.
    """
    period_end: str
    total_assets: float
    current_assets: float
    current_liabilities: float
    total_liabilities: float
    retained_earnings: float
    ebit: float
    sales: float
    market_value_equity: Optional[float] = None
    book_value_equity: Optional[float] = None
    inventory: Optional[float] = None
    intangible_assets: Optional[float] = None
    working_capital: Optional[float] = None  # Can be calculated
    raw_data: Dict = field(default_factory=dict)  # Original data for reference

    def __post_init__(self):
        """Calculate any derived fields if not explicitly provided."""
        if self.working_capital is None:
            self.working_capital = self.current_assets - self.current_liabilities
        
        if self.book_value_equity is None and self.total_assets is not None and self.total_liabilities is not None:
            self.book_value_equity = self.total_assets - self.total_liabilities


@dataclass
class CompanyProfile:
    """
    Data class for company profile information.
    """
    ticker: str
    name: str
    sic: Optional[str] = None
    sic_description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    cik: Optional[str] = None
    is_financial: bool = False
    is_retail: bool = False
    is_manufacturing: bool = False
    is_service: bool = False
    is_us_company: bool = True
    is_adr: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class ZScoreModelConfig:
    """
    Data class for Z-Score model configuration.
    """
    model_key: str  # "original", "private", "emerging", "financial", "retail"
    model_type: str  # Human-readable name
    model_coefficients: Dict[str, float]
    model_thresholds: Dict[str, float]
    use_market_value: bool
    appropriateness_warnings: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class ZScoreComponent:
    """
    Data class for an individual Z-Score component calculation.
    """
    name: str  # X1, X2, etc.
    value: float
    numerator: float
    denominator: float
    coefficient: float
    weighted_value: float
    is_valid: bool = True
    warnings: List[str] = field(default_factory=list)


@dataclass
class ZScoreResult:
    """
    Data class for Z-Score calculation results for a quarter.
    """
    quarter_end: str
    zscore: Optional[float]
    components: Dict[str, ZScoreComponent]
    valid: bool
    model_key: str
    zone: str  # "safe", "grey", "distress"
    diagnostics: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class MarketData:
    """
    Data class for market-related data.
    """
    market_value_equity: Dict[str, float]  # Keyed by date
    price_history: List[Dict]
    price_statistics: Dict = field(default_factory=dict)
    recommendations: Optional[Dict] = None
    institutional_holders: Optional[Dict] = None
    major_holders: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class AnalysisContext:
    """
    Data class for overall analysis context.
    """
    ticker: str
    start_date: str
    end_date: str
    model_config: ZScoreModelConfig
    company_profile: CompanyProfile
    quarters_analyzed: int
    analysis_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    version: str = "4.0.0"
    metadata: Dict = field(default_factory=dict)


@dataclass
class OutputManifest:
    """
    Data class for tracking generated output files.
    """
    csv_path: Optional[str] = None
    json_path: Optional[str] = None
    chart_path: Optional[str] = None
    report_path: Optional[str] = None
    metadata_path: Optional[str] = None
    additional_files: Dict[str, str] = field(default_factory=dict)  # name: path


@dataclass
class ValidationResult:
    """
    Data class for validation results.
    """
    valid: bool
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """
    Data class for data quality reports.
    """
    passes_threshold: bool
    total_quarters: int
    usable_quarters: int
    missing_fields: Dict[str, List[str]] = field(default_factory=dict)  # quarter -> field list
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class OutlierReport:
    """
    Data class for outlier detection results.
    """
    has_outliers: bool
    outliers: Dict[str, List[Dict]] = field(default_factory=dict)  # component -> list of outliers
    warnings: List[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """
    Comprehensive data quality assessment report.
    """
    ticker: str
    is_complete: bool
    missing_fields: List[str]
    warnings: List[str]
    quality_score: float  # 0.0 to 1.0
    recommendation: str
    timestamp: Optional[str] = None
    
    # Detailed quality metrics
    total_checks: Optional[int] = None
    passed_checks: Optional[int] = None
    failed_checks: Optional[int] = None
    warning_checks: Optional[int] = None


# This file will be expanded during refactoring with additional data models
