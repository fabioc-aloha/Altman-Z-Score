"""
AI Analysis Layer - Comprehensive AI-enhanced financial analysis

This layer provides four key AI enhancements to the Altman Z-Score pipeline:
1. Data Quality & Anomaly Detection - AI-powered data validation
2. Intelligent Peer Comparison - Smart peer identification and benchmarking  
3. Market Sentiment Integration - Multi-source sentiment synthesis
4. Risk Factor Identification - Comprehensive risk analysis

Key Features:
- AI-powered data quality assessment and anomaly detection
- Literature-informed financial analysis using academic research
- Comprehensive investment narratives with AI insights
- Risk-adjusted recommendations based on multiple AI components
- Professional-grade analysis suitable for institutional decision-making

Current Implementation Status:
- ✅ Data Quality Analysis (Phase 1) - Fully implemented
- 🔄 Peer Analysis (Phase 2) - Planned implementation
- 🔄 Sentiment Analysis (Phase 3) - Planned implementation  
- 🔄 Risk Analysis (Phase 4) - Planned implementation
"""

from .ai_data_quality_checker import AIDataQualityChecker, DataQualityMetrics
from .ai_orchestrator import AIAnalysisOrchestrator, ComprehensiveAIAnalysis

# Legacy component (existing)
from .ai_insights_generator import AIInsightsGenerator

__all__ = [
    'AIDataQualityChecker',
    'DataQualityMetrics', 
    'AIAnalysisOrchestrator',
    'ComprehensiveAIAnalysis',
    'AIInsightsGenerator'  # Legacy component
]
