"""
Market Analysis Data Models

Data structures for technical analysis, valuation metrics, performance analysis,
and risk-return profiles to complement Z-Score fundamental analysis.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


@dataclass
class TechnicalIndicators:
    """Technical analysis indicators and metrics."""
    # Price trend indicators
    sma_20: Optional[float] = None          # 20-day simple moving average
    sma_50: Optional[float] = None          # 50-day simple moving average
    sma_200: Optional[float] = None         # 200-day simple moving average
    ema_12: Optional[float] = None          # 12-day exponential moving average
    ema_26: Optional[float] = None          # 26-day exponential moving average
    
    # Momentum indicators
    rsi: Optional[float] = None             # Relative Strength Index (14-day)
    macd: Optional[float] = None            # MACD line
    macd_signal: Optional[float] = None     # MACD signal line
    macd_histogram: Optional[float] = None  # MACD histogram
    
    # Volatility indicators
    bollinger_upper: Optional[float] = None # Bollinger Band upper
    bollinger_lower: Optional[float] = None # Bollinger Band lower
    atr: Optional[float] = None             # Average True Range
    
    # Volume indicators
    volume_sma: Optional[float] = None      # Volume moving average
    volume_ratio: Optional[float] = None    # Current volume vs average


@dataclass
class TechnicalAnalysis:
    """Complete technical analysis results."""
    ticker: str
    current_price: float
    analysis_date: datetime
    
    indicators: TechnicalIndicators
    
    # Trend analysis
    price_trend: str                        # "uptrend", "downtrend", "sideways"
    trend_strength: float                   # 0.0 to 1.0
    
    # Trading signals
    buy_signals: List[str]                  # List of bullish signals
    sell_signals: List[str]                 # List of bearish signals
    overall_signal: str                     # "buy", "sell", "hold"
    
    # Optional fields with defaults
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    
    # Volatility analysis
    volatility_30d: Optional[float] = None  # 30-day historical volatility
    volatility_rank: Optional[str] = None   # "low", "medium", "high"
    
    # Momentum analysis
    momentum_score: Optional[float] = None  # -1.0 to 1.0
    momentum_direction: Optional[str] = None # "bullish", "bearish", "neutral"


@dataclass
class ValuationMetrics:
    """Valuation ratios and comparative analysis."""
    ticker: str
    analysis_date: datetime
    
    # Core valuation ratios
    pe_ratio: Optional[float] = None        # Price-to-Earnings
    pb_ratio: Optional[float] = None        # Price-to-Book
    ps_ratio: Optional[float] = None        # Price-to-Sales
    peg_ratio: Optional[float] = None       # PEG ratio
    
    # Dividend metrics
    dividend_yield: Optional[float] = None  # Current dividend yield
    dividend_payout_ratio: Optional[float] = None
    dividend_growth_rate: Optional[float] = None
    
    # Market metrics
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    ev_ebitda: Optional[float] = None
    
    # Comparative analysis
    sector_pe_median: Optional[float] = None
    sector_pb_median: Optional[float] = None
    relative_valuation: Optional[str] = None # "undervalued", "fairly_valued", "overvalued"
    
    # Price targets and estimates
    analyst_price_target: Optional[float] = None
    upside_potential: Optional[float] = None


@dataclass 
class MarketPerformance:
    """Performance analysis vs benchmarks and sector."""
    ticker: str
    analysis_date: datetime
    
    # Returns analysis
    return_1d: Optional[float] = None       # 1-day return
    return_1w: Optional[float] = None       # 1-week return  
    return_1m: Optional[float] = None       # 1-month return
    return_3m: Optional[float] = None       # 3-month return
    return_6m: Optional[float] = None       # 6-month return
    return_1y: Optional[float] = None       # 1-year return
    
    # Benchmark comparison (vs S&P 500)
    benchmark_1m: Optional[float] = None    # Relative 1-month performance
    benchmark_3m: Optional[float] = None    # Relative 3-month performance
    benchmark_1y: Optional[float] = None    # Relative 1-year performance
    
    # Risk metrics
    beta: Optional[float] = None            # Beta vs market
    sharpe_ratio: Optional[float] = None    # Risk-adjusted return
    max_drawdown: Optional[float] = None    # Maximum drawdown
    
    # Sector analysis
    sector: Optional[str] = None
    sector_performance_1m: Optional[float] = None
    sector_performance_3m: Optional[float] = None
    sector_rank: Optional[int] = None       # Rank within sector
    
    # Correlation analysis
    market_correlation: Optional[float] = None


@dataclass
class RiskReturnProfile:
    """Combined fundamental and market risk assessment."""
    ticker: str
    analysis_date: datetime
    
    # Z-Score risk metrics
    z_score: float
    z_score_risk_category: str              # From Z-Score analysis
    fundamental_risk_score: float           # 0.0 to 1.0 (low to high risk)
    
    # Market risk metrics
    market_risk_score: float                # 0.0 to 1.0 (low to high risk)
    volatility_risk: float                  # Based on price volatility
    liquidity_risk: float                   # Based on volume and market cap
    
    # Combined risk assessment
    overall_risk_score: float               # Combined fundamental + market risk
    overall_risk_category: str              # "low", "medium", "high"
    
    # Investment recommendation
    risk_adjusted_score: float              # Risk-adjusted attractiveness
    investment_rating: str                  # "strong_buy", "buy", "hold", "sell", "strong_sell"
    confidence_level: float                 # 0.0 to 1.0
    
    # Key risks and opportunities
    key_risks: List[str]
    key_opportunities: List[str]
    
    # Optional fields with defaults
    # Return potential
    growth_potential: Optional[float] = None # Expected return potential
    dividend_income: Optional[float] = None  # Dividend yield contribution
    total_return_potential: Optional[float] = None
    
    # Correlation analysis
    zscore_price_correlation: Optional[float] = None


@dataclass
class ComprehensiveMarketAnalysis:
    """Complete market analysis combining all components."""
    ticker: str
    analysis_date: datetime
    
    # Executive summary
    investment_thesis: str
    key_strengths: List[str]
    key_concerns: List[str]
    target_rationale: str
    
    # Data quality
    data_quality_score: float               # 0.0 to 1.0
    analysis_completeness: float            # 0.0 to 1.0
    
    # Metadata
    generated_at: datetime
    generator_version: str
    
    # Optional analysis components (may fail individually)
    technical_analysis: Optional[TechnicalAnalysis] = None
    valuation_metrics: Optional[ValuationMetrics] = None
    market_performance: Optional[MarketPerformance] = None
    risk_return_profile: Optional[RiskReturnProfile] = None
    price_target: Optional[float] = None


# Utility classes for analysis parameters
@dataclass
class AnalysisParameters:
    """Parameters for market analysis configuration."""
    # Technical analysis periods
    short_ma_period: int = 20
    medium_ma_period: int = 50
    long_ma_period: int = 200
    rsi_period: int = 14
    
    # Volatility analysis
    volatility_window: int = 30
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    
    # Performance analysis
    benchmark_symbol: str = "SPY"
    sector_etf_map: Dict[str, str] = None
    
    # Risk analysis
    risk_free_rate: float = 0.045  # Current risk-free rate
    market_risk_premium: float = 0.06
    
    def __post_init__(self):
        if self.sector_etf_map is None:
            self.sector_etf_map = {
                "Technology": "XLK",
                "Healthcare": "XLV", 
                "Financials": "XLF",
                "Consumer Discretionary": "XLY",
                "Communication Services": "XLC",
                "Industrials": "XLI",
                "Consumer Staples": "XLP",
                "Energy": "XLE",
                "Utilities": "XLU",
                "Real Estate": "XLRE",
                "Materials": "XLB"
            }
