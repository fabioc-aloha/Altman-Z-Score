"""
AI Data Quality Checker - AI-powered financial data quality and anomaly detection

This module implements AI-enhanced data quality checking to identify anomalies,
inconsistencies, and quality issues in financial data that could affect 
Z-Score accuracy and investment analysis reliability.

Key Features:
- LLM-powered anomaly detection using financial domain knowledge
- Industry-specific data validation patterns
- Quality scoring with confidence metrics
- Automated flagging of suspicious data points
- Integration with academic literature on financial data quality
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError, ValidationError
from ...models.data_models import MergedFinancialData, DataQualityReport
from ..data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


@dataclass
class AnomalyDetection:
    """Data structure for anomaly detection results."""
    field_name: str
    anomaly_type: str  # 'outlier', 'inconsistency', 'missing_critical', 'calculation_error'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_action: str
    confidence: float


@dataclass
class DataQualityMetrics:
    """Comprehensive data quality assessment metrics."""
    overall_quality_score: float  # 0-100
    completeness_score: float    # 0-100
    consistency_score: float     # 0-100
    accuracy_score: float        # 0-100
    anomalies_detected: List[AnomalyDetection]
    reliability_rating: str      # 'excellent', 'good', 'fair', 'poor', 'unreliable'
    recommendation: str


class AIDataQualityChecker:
    """AI-powered data quality and anomaly detection for financial data."""
    
    def __init__(self):
        """Initialize the AI data quality checker."""
        self.llm_client = LLMClient()
        logger.info("AI Data Quality Checker initialized")
    
    async def analyze_data_quality(self, financial_data: MergedFinancialData) -> DataQualityMetrics:
        """
        Perform comprehensive AI-powered data quality analysis.
        
        Args:
            financial_data: Merged financial data to analyze
            
        Returns:
            DataQualityMetrics: Comprehensive quality assessment
            
        Raises:
            AIAnalysisError: If AI analysis fails
        """
        try:
            logger.info(f"Starting AI data quality analysis for {financial_data.ticker}")
            
            # Extract key financial metrics for analysis
            financial_summary = self._extract_financial_summary(financial_data)
            
            # Perform AI-powered anomaly detection
            anomalies = await self._detect_anomalies(financial_summary)
            
            # Calculate quality scores
            quality_scores = await self._calculate_quality_scores(financial_summary, anomalies)
            
            # Generate overall assessment
            overall_assessment = await self._generate_overall_assessment(
                financial_summary, anomalies, quality_scores
            )
            
            # Compile results
            quality_metrics = DataQualityMetrics(
                overall_quality_score=overall_assessment['overall_score'],
                completeness_score=quality_scores['completeness'],
                consistency_score=quality_scores['consistency'],
                accuracy_score=quality_scores['accuracy'],
                anomalies_detected=anomalies,
                reliability_rating=overall_assessment['reliability_rating'],
                recommendation=overall_assessment['recommendation']
            )
            
            logger.info(f"Data quality analysis complete for {financial_data.ticker}: "
                       f"{quality_metrics.overall_quality_score:.1f}/100 "
                       f"({quality_metrics.reliability_rating})")
            
            return quality_metrics
            
        except Exception as e:
            error_msg = f"AI data quality analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    def _extract_financial_summary(self, financial_data: MergedFinancialData) -> Dict[str, Any]:
        """
        Extract key financial metrics for AI analysis.
        
        Args:
            financial_data: Merged financial data
            
        Returns:
            Dict containing extracted financial summary
        """
        return {
            'ticker': financial_data.ticker,
            'report_date': financial_data.timestamp,  # Use timestamp instead of report_date
            'company_name': getattr(financial_data, 'company_name', 'Unknown'),
            'sector': getattr(financial_data, 'sector', 'Unknown'),
            'industry': getattr(financial_data, 'industry', 'Unknown'),
            
            # Core Z-Score components - use ratios from MergedFinancialData
            'working_capital_ratio': financial_data.working_capital_ratio,
            'retained_earnings_ratio': financial_data.retained_earnings_ratio,
            'ebit_ratio': financial_data.ebit_ratio,
            'asset_turnover': financial_data.asset_turnover,
            'market_cap': financial_data.market_cap,
            
            # Additional financial metrics
            'current_ratio': financial_data.current_ratio,
            'debt_to_equity': financial_data.debt_to_equity,
            'shares_outstanding': financial_data.shares_outstanding,
            'current_price': financial_data.current_price,
            
            # Data completeness flags - check for ratio availability
            'has_working_capital': financial_data.working_capital_ratio is not None,
            'has_retained_earnings': financial_data.retained_earnings_ratio is not None,
            'has_ebit': financial_data.ebit_ratio is not None,
            'has_market_data': financial_data.market_cap is not None,
        }
    
    async def _detect_anomalies(self, financial_summary: Dict[str, Any]) -> List[AnomalyDetection]:
        """
        Use LLM to detect financial data anomalies.
        
        Args:
            financial_summary: Extracted financial metrics
            
        Returns:
            List of detected anomalies
        """
        prompt = self._build_anomaly_detection_prompt(financial_summary)
        
        for attempt in range(3):  # Retry logic
            try:
                response = self.llm_client.chat_completion(
                    ticker=financial_summary['ticker'],
                    messages=[{"role": "user", "content": prompt}],
                    interaction_type="anomaly_detection",
                    temperature=0.1,  # Low temperature for consistent analysis
                    max_tokens=2000,
                    force_json=True  # Force JSON response format
                )
                
                # Log the raw response for debugging
                logger.debug(f"Raw anomaly detection response for {financial_summary['ticker']}: {response}")
                
                # Try to extract JSON from response if it's wrapped in text
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                # Parse JSON response
                anomaly_data = json.loads(response_clean)
                anomalies = []
                
                for anomaly_info in anomaly_data.get('anomalies', []):
                    anomalies.append(AnomalyDetection(
                        field_name=anomaly_info['field_name'],
                        anomaly_type=anomaly_info['anomaly_type'],
                        severity=anomaly_info['severity'],
                        description=anomaly_info['description'],
                        suggested_action=anomaly_info['suggested_action'],
                        confidence=anomaly_info['confidence']
                    ))
                
                logger.info(f"Detected {len(anomalies)} anomalies for {financial_summary['ticker']}")
                return anomalies
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for anomaly detection: {str(e)}")
                logger.debug(f"Failed response: {response[:200]}...")
                if attempt == 2:
                    logger.error(f"All anomaly detection attempts failed for {financial_summary['ticker']}")
                    return []  # Return empty list if all attempts fail
        
        return []
    
    async def _calculate_quality_scores(self, financial_summary: Dict[str, Any], 
                                      anomalies: List[AnomalyDetection]) -> Dict[str, float]:
        """
        Calculate quality scores using AI analysis.
        
        Args:
            financial_summary: Financial metrics summary
            anomalies: Detected anomalies
            
        Returns:
            Dict with quality scores
        """
        prompt = self._build_quality_scoring_prompt(financial_summary, anomalies)
        
        for attempt in range(3):
            try:
                response = self.llm_client.chat_completion(
                    ticker=financial_summary['ticker'],
                    messages=[{"role": "user", "content": prompt}],
                    interaction_type="quality_scoring",
                    temperature=0.1,
                    max_tokens=1000,
                    force_json=True  # Force JSON response format
                )
                
                # Log and clean response
                logger.debug(f"Raw quality scoring response for {financial_summary['ticker']}: {response}")
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                scores_data = json.loads(response_clean)
                return {
                    'completeness': scores_data['completeness_score'],
                    'consistency': scores_data['consistency_score'],
                    'accuracy': scores_data['accuracy_score']
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for quality scoring: {str(e)}")
                logger.debug(f"Failed response: {response[:200]}...")
                if attempt == 2:
                    # Return conservative default scores
                    return {'completeness': 70.0, 'consistency': 70.0, 'accuracy': 70.0}
        
        return {'completeness': 70.0, 'consistency': 70.0, 'accuracy': 70.0}
    
    async def _generate_overall_assessment(self, financial_summary: Dict[str, Any],
                                         anomalies: List[AnomalyDetection],
                                         quality_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate overall data quality assessment.
        
        Args:
            financial_summary: Financial metrics summary
            anomalies: Detected anomalies
            quality_scores: Calculated quality scores
            
        Returns:
            Dict with overall assessment
        """
        prompt = self._build_overall_assessment_prompt(financial_summary, anomalies, quality_scores)
        
        for attempt in range(3):
            try:
                response = self.llm_client.chat_completion(
                    ticker=financial_summary['ticker'],
                    messages=[{"role": "user", "content": prompt}],
                    interaction_type="overall_assessment",
                    temperature=0.2,
                    max_tokens=1500,
                    force_json=True  # Force JSON response format
                )
                
                # Log and clean response
                logger.debug(f"Raw overall assessment response for {financial_summary['ticker']}: {response}")
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                assessment_data = json.loads(response_clean)
                return {
                    'overall_score': assessment_data['overall_score'],
                    'reliability_rating': assessment_data['reliability_rating'],
                    'recommendation': assessment_data['recommendation']
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for overall assessment: {str(e)}")
                logger.debug(f"Failed response: {response[:200]}...")
                if attempt == 2:
                    # Return conservative default assessment
                    avg_score = sum(quality_scores.values()) / len(quality_scores)
                    return {
                        'overall_score': avg_score,
                        'reliability_rating': 'fair' if avg_score >= 60 else 'poor',
                        'recommendation': 'Proceed with caution due to data quality analysis limitations.'
                    }
        
        # Fallback assessment
        avg_score = sum(quality_scores.values()) / len(quality_scores)
        return {
            'overall_score': avg_score,
            'reliability_rating': 'fair' if avg_score >= 60 else 'poor',
            'recommendation': 'Proceed with caution due to data quality analysis limitations.'
        }
    
    def _build_anomaly_detection_prompt(self, financial_summary: Dict[str, Any]) -> str:
        """Build prompt for anomaly detection."""
        
        def format_value(value, is_ratio=False):
            if value is None:
                return 'Missing'
            if is_ratio:
                return f"{value:.4f}"
            else:
                return f"${value:,.0f}"
        
        return f"""You are a financial data quality expert analyzing company financial data for anomalies and inconsistencies. 

Company: {financial_summary['ticker']} ({financial_summary['company_name']})
Sector: {financial_summary['sector']} | Industry: {financial_summary['industry']}
Report Date: {financial_summary['report_date']}

Financial Data (Z-Score Ratios):
- Working Capital Ratio: {format_value(financial_summary['working_capital_ratio'], True)}
- Retained Earnings Ratio: {format_value(financial_summary['retained_earnings_ratio'], True)}
- EBIT Ratio: {format_value(financial_summary['ebit_ratio'], True)}
- Asset Turnover: {format_value(financial_summary['asset_turnover'], True)}
- Market Cap: {format_value(financial_summary['market_cap'])}
- Current Ratio: {format_value(financial_summary['current_ratio'], True)}
- Debt-to-Equity: {format_value(financial_summary['debt_to_equity'], True)}

Data Completeness:
- Has Working Capital Ratio: {financial_summary['has_working_capital']}
- Has Retained Earnings Ratio: {financial_summary['has_retained_earnings']}
- Has EBIT Ratio: {financial_summary['has_ebit']}
- Has Market Data: {financial_summary['has_market_data']}

Analyze this financial data for anomalies considering:

1. **Data Completeness**: Missing critical fields for Z-Score calculation
2. **Ratio Reasonableness**: Unusual ratios vs. industry norms
3. **Internal Consistency**: Relationships between financial metrics
4. **Industry Context**: Typical patterns for this sector/industry
5. **Magnitude Checks**: Unreasonable values (negative where positive expected, etc.)

Academic Context:
- Altman (1968) identified optimal Z-Score discriminatory ratios
- Financial statement quality research emphasizes consistency checks
- Industry-specific patterns from empirical finance literature

Return your analysis as JSON:
{{
  "anomalies": [
    {{
      "field_name": "field_with_anomaly",
      "anomaly_type": "outlier|inconsistency|missing_critical|calculation_error",
      "severity": "low|medium|high|critical",
      "description": "Clear description of the anomaly",
      "suggested_action": "Recommended action to address",
      "confidence": 0.85
    }}
  ]
}}

If no significant anomalies detected, return: {{"anomalies": []}}"""

    def _build_quality_scoring_prompt(self, financial_summary: Dict[str, Any], 
                                    anomalies: List[AnomalyDetection]) -> str:
        """Build prompt for quality scoring."""
        anomaly_summary = f"Detected {len(anomalies)} anomalies: " + \
                         ", ".join([f"{a.field_name} ({a.severity})" for a in anomalies[:5]])
        
        return f"""You are a financial data quality expert scoring data reliability for investment analysis.

Company: {financial_summary['ticker']} - {financial_summary['sector']} sector
Anomalies: {anomaly_summary}

Data Availability:
- Core Z-Score Fields: {sum([financial_summary['has_working_capital'], financial_summary['has_retained_earnings'], financial_summary['has_ebit']])}/3 available
- Market Data: {'Available' if financial_summary['has_market_data'] else 'Missing'}
- Additional Ratios: {sum([1 for x in [financial_summary['current_ratio'], financial_summary['debt_to_equity']] if x is not None])}/2 available

Score the data quality (0-100) for:

1. **Completeness** (0-100): Availability of required data fields
2. **Consistency** (0-100): Internal logical consistency and ratio relationships  
3. **Accuracy** (0-100): Likelihood data represents true financial position

Consider:
- Critical fields for Z-Score calculation (working capital, retained earnings, EBIT, assets)
- Severity and number of detected anomalies
- Industry-typical data patterns
- Market data integration quality

Return as JSON:
{{
  "completeness_score": 85,
  "consistency_score": 78,
  "accuracy_score": 82
}}"""

    def _build_overall_assessment_prompt(self, financial_summary: Dict[str, Any],
                                       anomalies: List[AnomalyDetection],
                                       quality_scores: Dict[str, float]) -> str:
        """Build prompt for overall assessment."""
        critical_anomalies = len([a for a in anomalies if a.severity in ['high', 'critical']])
        
        return f"""You are a financial analyst providing an overall data quality assessment for investment decision-making.

Company: {financial_summary['ticker']} ({financial_summary['company_name']})
Quality Scores: Completeness {quality_scores['completeness']:.1f}, Consistency {quality_scores['consistency']:.1f}, Accuracy {quality_scores['accuracy']:.1f}
Anomalies: {len(anomalies)} total, {critical_anomalies} critical/high severity

Provide overall assessment considering:
- Suitability for Z-Score calculation and investment analysis
- Risk of incorrect conclusions from data issues
- Confidence level for decision-making
- Academic standards for financial analysis quality

Return as JSON:
{{
  "overall_score": 78.5,
  "reliability_rating": "excellent|good|fair|poor|unreliable",
  "recommendation": "Clear recommendation for using this data in investment analysis"
}}

Rating Guidelines:
- excellent (90-100): Institutional-quality data, high confidence
- good (75-89): Suitable for investment analysis with minor caveats
- fair (60-74): Usable but requires additional verification
- poor (40-59): Significant limitations, use with extreme caution
- unreliable (<40): Not suitable for investment decisions"""
