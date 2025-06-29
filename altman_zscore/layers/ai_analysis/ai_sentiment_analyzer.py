"""
AI Sentiment Analyzer - Multi-source market sentiment integration

This module integrates market sentiment analysis from multiple sources
to provide comprehensive sentiment-aware investment insights.

Key Features:
- Multi-source sentiment aggregation
- News and social media analysis simulation
- Analyst sentiment tracking
- Sentiment-fundamental divergence detection
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import AIAnalysisError
from ...models.data_models import MergedFinancialData
from ..data_fetch.llm_client import LLMClient

logger = get_logger(__name__)


class SentimentSource(Enum):
    """Sources of sentiment data."""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    ANALYST_REPORTS = "analyst_reports"
    EARNINGS_CALLS = "earnings_calls"
    SEC_FILINGS = "sec_filings"


@dataclass
class SentimentMetric:
    """Individual sentiment metric from a source."""
    source: SentimentSource
    sentiment_score: float  # -1.0 (very negative) to +1.0 (very positive)
    confidence: float  # 0.0 to 1.0
    sample_size: int
    time_window: str
    key_themes: List[str]


@dataclass
class SentimentAnalysisResult:
    """Results of comprehensive sentiment analysis."""
    ticker: str
    overall_sentiment_score: float  # Weighted average of all sources
    sentiment_trend: str  # 'improving', 'declining', 'stable'
    sentiment_metrics: List[SentimentMetric]
    fundamental_sentiment_divergence: Optional[str]  # Divergence analysis
    investment_implication: str
    confidence: float
    analysis_timestamp: datetime


class AISentimentAnalyzer:
    """
    AI-powered market sentiment analysis and integration.
    
    Simulates multi-source sentiment analysis to demonstrate
    integration capabilities with actual sentiment data sources.
    """
    
    def __init__(self):
        """Initialize the AI sentiment analyzer."""
        self.llm_client = LLMClient()
        logger.info("AI Sentiment Analyzer initialized")
    
    async def analyze_sentiment(self, financial_data: MergedFinancialData) -> SentimentAnalysisResult:
        """
        Perform comprehensive sentiment analysis for a company.
        
        Args:
            financial_data: Target company's financial data
            
        Returns:
            SentimentAnalysisResult: Complete sentiment analysis results
            
        Raises:
            AIAnalysisError: If sentiment analysis fails
        """
        try:
            logger.info(f"Starting AI sentiment analysis for {financial_data.ticker}")
            
            # Step 1: Gather sentiment metrics from multiple sources
            sentiment_metrics = await self._gather_sentiment_metrics(financial_data.ticker)
            
            # Step 2: Calculate overall sentiment score
            overall_sentiment = self._calculate_overall_sentiment(sentiment_metrics)
            
            # Step 3: Analyze sentiment trend
            sentiment_trend = await self._analyze_sentiment_trend(financial_data.ticker, sentiment_metrics)
            
            # Step 4: Detect fundamental-sentiment divergence
            divergence_analysis = await self._analyze_fundamental_sentiment_divergence(
                financial_data, overall_sentiment
            )
            
            # Step 5: Generate investment implications
            investment_implication = await self._generate_sentiment_investment_implication(
                financial_data.ticker, overall_sentiment, sentiment_trend, divergence_analysis
            )
            
            result = SentimentAnalysisResult(
                ticker=financial_data.ticker,
                overall_sentiment_score=overall_sentiment,
                sentiment_trend=sentiment_trend,
                sentiment_metrics=sentiment_metrics,
                fundamental_sentiment_divergence=divergence_analysis,
                investment_implication=investment_implication,
                confidence=0.72,  # Moderate-high confidence for simulated analysis
                analysis_timestamp=datetime.now()
            )
            
            logger.info(f"Sentiment analysis complete for {financial_data.ticker}: "
                       f"overall sentiment {result.overall_sentiment_score:.2f}, "
                       f"trend: {result.sentiment_trend}")
            
            return result
            
        except Exception as e:
            error_msg = f"Sentiment analysis failed for {financial_data.ticker}: {str(e)}"
            logger.error(error_msg)
            raise AIAnalysisError(error_msg) from e
    
    async def _gather_sentiment_metrics(self, ticker: str) -> List[SentimentMetric]:
        """
        Gather sentiment metrics from multiple sources (simulated).
        
        Args:
            ticker: Target company ticker
            
        Returns:
            List of sentiment metrics from different sources
        """
        # In a real implementation, this would:
        # 1. Fetch news articles from financial news APIs
        # 2. Analyze social media mentions (Twitter, Reddit, etc.)
        # 3. Process analyst reports and ratings changes
        # 4. Analyze earnings call transcripts
        # 5. Process SEC filing sentiment
        
        # Simulated sentiment metrics for demonstration
        import random
        random.seed(hash(ticker))  # Consistent "random" values for demo
        
        metrics = []
        
        # News sentiment
        news_sentiment = SentimentMetric(
            source=SentimentSource.NEWS,
            sentiment_score=random.uniform(-0.3, 0.7),
            confidence=0.8,
            sample_size=45,
            time_window="30 days",
            key_themes=["earnings", "market_conditions", "competition"]
        )
        metrics.append(news_sentiment)
        
        # Social media sentiment
        social_sentiment = SentimentMetric(
            source=SentimentSource.SOCIAL_MEDIA,
            sentiment_score=random.uniform(-0.5, 0.5),
            confidence=0.6,
            sample_size=1200,
            time_window="7 days",
            key_themes=["product_reviews", "brand_perception", "customer_service"]
        )
        metrics.append(social_sentiment)
        
        # Analyst sentiment
        analyst_sentiment = SentimentMetric(
            source=SentimentSource.ANALYST_REPORTS,
            sentiment_score=random.uniform(-0.2, 0.8),
            confidence=0.9,
            sample_size=12,
            time_window="90 days",
            key_themes=["growth_prospects", "valuation", "competitive_position"]
        )
        metrics.append(analyst_sentiment)
        
        return metrics
    
    def _calculate_overall_sentiment(self, sentiment_metrics: List[SentimentMetric]) -> float:
        """
        Calculate weighted overall sentiment score.
        
        Args:
            sentiment_metrics: List of sentiment metrics
            
        Returns:
            Overall sentiment score (-1.0 to +1.0)
        """
        if not sentiment_metrics:
            return 0.0
        
        # Weight by confidence and sample size
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric in sentiment_metrics:
            # Weight combines confidence and normalized sample size
            weight = metric.confidence * min(1.0, metric.sample_size / 100.0)
            weighted_sum += metric.sentiment_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _analyze_sentiment_trend(self, ticker: str, 
                                     sentiment_metrics: List[SentimentMetric]) -> str:
        """
        Analyze sentiment trend over time (simulated).
        
        Args:
            ticker: Target company ticker
            sentiment_metrics: Current sentiment metrics
            
        Returns:
            Sentiment trend description
        """
        # In a real implementation, this would compare current sentiment
        # with historical sentiment to determine trend direction
        
        # Simulate trend analysis
        import random
        random.seed(hash(ticker + "trend"))
        
        trends = ["improving", "declining", "stable"]
        weights = [0.3, 0.3, 0.4]  # Slight bias toward stability
        
        return random.choices(trends, weights=weights)[0]
    
    async def _analyze_fundamental_sentiment_divergence(self, 
                                                      financial_data: MergedFinancialData,
                                                      sentiment_score: float) -> Optional[str]:
        """
        Analyze divergence between fundamental strength and market sentiment.
        
        Args:
            financial_data: Company's financial data
            sentiment_score: Overall sentiment score
            
        Returns:
            Divergence analysis or None if no significant divergence
        """
        # Simulate fundamental strength assessment
        # In reality, this would use actual Z-score and financial metrics
        import random
        random.seed(hash(financial_data.ticker + "divergence"))
        
        # Simulated fundamental strength (-1 to +1)
        fundamental_strength = random.uniform(-0.5, 0.8)
        
        # Check for significant divergence (>0.5 point difference)
        divergence = abs(sentiment_score - fundamental_strength)
        
        if divergence > 0.5:
            if sentiment_score > fundamental_strength:
                return f"Market sentiment ({sentiment_score:.2f}) appears overly optimistic relative to fundamental strength ({fundamental_strength:.2f}). Potential overvaluation risk."
            else:
                return f"Market sentiment ({sentiment_score:.2f}) appears overly pessimistic relative to fundamental strength ({fundamental_strength:.2f}). Potential value opportunity."
        
        return None  # No significant divergence
    
    async def _generate_sentiment_investment_implication(self, 
                                                       ticker: str,
                                                       sentiment_score: float,
                                                       sentiment_trend: str,
                                                       divergence_analysis: Optional[str]) -> str:
        """
        Generate LLM-powered investment implications from sentiment analysis.
        
        Args:
            ticker: Target company ticker
            sentiment_score: Overall sentiment score
            sentiment_trend: Sentiment trend direction
            divergence_analysis: Fundamental-sentiment divergence analysis
            
        Returns:
            Investment implication narrative
        """
        sentiment_desc = self._describe_sentiment_score(sentiment_score)
        
        # Load prompt template from file
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "prompt_sentiment_analysis.md"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found: {prompt_path}")
            # Fallback to a simple prompt
            prompt_template = """As a market sentiment analyst, provide investment strategy for {ticker} based on sentiment analysis:
            
Sentiment Analysis:
- Overall Sentiment: {sentiment_description} (score: {sentiment_score}/5.0)
- Sentiment Trend: {sentiment_trend}
- Divergence: {divergence_analysis}

Provide investment recommendations and risk management guidance."""

        # Format the prompt with actual data
        prompt = prompt_template.format(
            ticker=ticker,
            sentiment_description=sentiment_desc,
            sentiment_score=f"{sentiment_score:.2f}",
            sentiment_trend=sentiment_trend,
            divergence_analysis=divergence_analysis if divergence_analysis else 'No significant divergence detected'
        )
        
        try:
            # Format prompt as messages for chat completion
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                ticker,
                messages,
                "sentiment_implication"
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate sentiment investment implication for {ticker}: {str(e)}")
            # Fallback to rule-based implication
            return self._generate_fallback_sentiment_implication(sentiment_score, sentiment_trend, divergence_analysis)
    
    def _describe_sentiment_score(self, score: float) -> str:
        """Convert sentiment score to descriptive text."""
        if score > 0.6:
            return "Very Positive"
        elif score > 0.2:
            return "Positive"
        elif score > -0.2:
            return "Neutral"
        elif score > -0.6:
            return "Negative"
        else:
            return "Very Negative"
    
    def _generate_fallback_sentiment_implication(self, 
                                               sentiment_score: float,
                                               sentiment_trend: str,
                                               divergence_analysis: Optional[str]) -> str:
        """Generate rule-based sentiment implication as fallback."""
        sentiment_desc = self._describe_sentiment_score(sentiment_score)
        
        base_implication = f"Market sentiment is {sentiment_desc.lower()} and {sentiment_trend}. "
        
        if sentiment_score > 0.4:
            base_implication += "Strong positive sentiment may indicate momentum but also potential overvaluation risk."
        elif sentiment_score < -0.4:
            base_implication += "Negative sentiment may present contrarian investment opportunities if fundamentals remain strong."
        else:
            base_implication += "Neutral sentiment suggests balanced market expectations."
        
        if divergence_analysis:
            base_implication += f" {divergence_analysis}"
        
        return base_implication
