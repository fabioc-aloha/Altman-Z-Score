"""
Analysis Layer - Advanced Financial Analysis Capabilities

This layer provides sophisticated analysis capabilities beyond basic Z-Score calculation,
including risk-return analysis, portfolio optimization, and investment recommendations.

Strategic Components:
- Risk-Return Analysis Engine: Multi-dimensional risk assessment
- Portfolio Optimization: Modern portfolio theory implementation  
- Sector Benchmarking: Industry-specific comparisons
- Investment Recommendations: AI-powered decision support
- Real-time Monitoring: Continuous risk assessment
- Enhanced Financial Indicators: Advanced quality metrics and competitive positioning

Enterprise Features (v4.2.0):
- Advanced risk scoring algorithms
- Portfolio-level analysis and optimization
- Sector-specific benchmarks and peer analysis
- Investment recommendation engine with confidence scoring
- Real-time risk monitoring and alert capabilities
- Enhanced financial indicators for deeper insights
"""

from .risk_return_engine import (
    RiskReturnAnalyzer,
    RiskLevel,
    RecommendationAction,
    RiskMetrics,
    RecommendationResult,
    PortfolioRiskProfile,
    analyze_single_security,
    analyze_portfolio
)

# Import enhanced indicators for external use
from .enhanced_indicators import (
    EnhancedIndicatorsCalculator,
    EnhancedFinancialIndicators,
    CashFlowQualityMetrics,
    EarningsQualityMetrics,
    CapitalAllocationMetrics,
    CompetitivePositioningMetrics,
    format_enhanced_indicators_for_llm
)

__all__ = [
    # Main analyzer
    'RiskReturnAnalyzer',
    
    # Enums
    'RiskLevel',
    'RecommendationAction',
    
    # Data classes
    'RiskMetrics',
    'RecommendationResult', 
    'PortfolioRiskProfile',
    
    # Utility functions
    'analyze_single_security',
    'analyze_portfolio',
    
    # Enhanced indicators
    'EnhancedIndicatorsCalculator',
    'EnhancedFinancialIndicators',
    'CashFlowQualityMetrics',
    'EarningsQualityMetrics',
    'CapitalAllocationMetrics',
    'CompetitivePositioningMetrics',
    'format_enhanced_indicators_for_llm'
]
