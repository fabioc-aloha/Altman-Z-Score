"""
Main Pipeline - Complete end-to-end investment analysis pipeline

This module provides the main entry point for complete ticker analysis,
integrating all layers from data fetching through comprehensive investment
analysis and final report generation.

Key Features:
- Complete pipeline orchestration with market analysis
- Z-Score calculation with market intelligence
- Error handling and recovery
- Progress tracking and logging
- Batch processing capabilities
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from .common.logging_config import get_logger
from .common.exceptions import PipelineError
from .layers.data_fetch.data_merger import DataMerger
from .layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from .layers.market_analysis.market_analysis_orchestrator import MarketAnalysisOrchestrator
from .layers.output_generation.csv_json_generator import CSVJSONGenerator
from .layers.output_generation.chart_generator import ChartGenerator
from .layers.output_generation.report_generator import ReportGenerator
from .layers.output_generation.file_manager import FileManager
from .layers.ai_insights.ai_insights_generator import AIInsightsGenerator

logger = get_logger(__name__)


class AltmanZScorePipeline:
    """Complete Altman Z-Score investment analysis pipeline."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize the pipeline.
        
        Args:
            output_base_path: Base directory for output files
        """
        self.output_base_path = output_base_path
        
        # Initialize components
        self.data_merger = DataMerger()
        self.zscore_calculator = ZScoreCalculator()
        self.market_analyzer = MarketAnalysisOrchestrator()
        self.csv_json_generator = CSVJSONGenerator(output_base_path)
        self.chart_generator = ChartGenerator(output_base_path)
        self.report_generator = ReportGenerator(output_base_path)
        self.file_manager = FileManager(output_base_path)
        self.ai_insights_generator = AIInsightsGenerator(output_base_path)
    
    async def analyze_ticker(
        self, 
        ticker: str,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_ai_insights: bool = False,
        include_market_analysis: bool = True,
        forced_model: str = None,
        quarters: int = 4,
        enhanced_analysis: bool = False,
        batch_size: int = 10
    ) -> Dict[str, str]:
        """
        Complete analysis for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            generate_charts: Whether to generate visualization charts
            generate_reports: Whether to generate comprehensive reports
            include_ai_insights: Whether to include AI-powered analysis
            include_market_analysis: Whether to include market analysis
            forced_model: Optional model to force (overrides automatic selection)
            quarters: Number of quarters for historical analysis (enhanced accounts: 8-20)
            enhanced_analysis: Enable enhanced features for upgraded FMP accounts
            batch_size: Batch size for concurrent processing (enhanced accounts: 20-50)
            
        Returns:
            Dict[str, str]: Paths to generated output files
        """
        try:
            logger.info(f"Starting complete investment analysis for {ticker}")
            
            # Enhanced analysis mode handling
            if enhanced_analysis:
                logger.info(f"Enhanced analysis mode enabled: {quarters} quarters, batch size {batch_size}")
                # Set enhanced mode environment variables for downstream components
                import os
                os.environ['FMP_ENHANCED_MODE'] = '1'
                os.environ['ANALYSIS_QUARTERS'] = str(quarters)
                os.environ['BATCH_SIZE'] = str(batch_size)
            
            # Validate quarters parameter for enhanced vs regular accounts
            if quarters > 4 and not enhanced_analysis:
                logger.warning(f"Quarters={quarters} requested but enhanced_analysis=False. Using 4 quarters for free account compatibility.")
                quarters = 4
            elif enhanced_analysis and quarters < 8:
                logger.info(f"Enhanced analysis enabled but quarters={quarters}. Consider using 8+ quarters for better trend analysis.")
            
            # Step 1: Merge financial data
            logger.info(f"Step 1: Merging financial data for {ticker}")
            # Pass enhanced parameters to data merger
            merged = await self.data_merger.merge_financial_data(
                ticker, 
                start_date=None,
                quarters=quarters if enhanced_analysis else 4
            )
            if not isinstance(merged, list):
                merged = [merged]
            
            # Step 2: Calculate Z-Score for each period
            logger.info(f"Step 2: Calculating Z-Score for {ticker} ({len(merged)} periods)")
            zscore_results = []
            for data in merged:
                result = self.zscore_calculator.calculate_zscore(data, forced_model=forced_model)
                zscore_results.append(result)
            
            # Use the most recent result for dashboard/report
            latest_result = zscore_results[0]            # Step 3: Market Analysis (NEW)
            market_analysis = None
            if include_market_analysis:
                logger.info(f"Step 3: Conducting market analysis for {ticker}")
                try:
                    # Note: analyze_ticker method is not async, but we'll call it directly
                    market_analysis = self.market_analyzer.analyze_ticker(
                        ticker, 
                        zscore_results[0].z_score, 
                        zscore_results[0].risk_category
                    )
                    if market_analysis.risk_return_profile:
                        logger.info(f"Market analysis complete for {ticker}: {market_analysis.risk_return_profile.investment_rating} ({market_analysis.risk_return_profile.confidence_level:.1%} confidence)")
                    else:
                        logger.info(f"Market analysis complete for {ticker} (no risk-return profile generated)")
                except Exception as e:
                    logger.warning(f"Market analysis failed for {ticker}: {str(e)}. Continuing with Z-Score only.")
                    market_analysis = None
            
            # Step 4a: CSV/JSON report for all results (enhanced with market analysis)
            logger.info(f"Step 4a: Generating CSV/JSON data for {ticker}")
            csv_path = self.csv_json_generator.generate_csv_report(zscore_results, market_analysis)
            json_path = self.csv_json_generator.generate_json_report(zscore_results, market_analysis)
            output_files = {'csv': csv_path, 'json': json_path}
              # Step 4b: Chart using all results for multi-quarter trend analysis (enhanced with market analysis)
            if generate_charts:
                logger.info(f"Step 4b: Generating enhanced charts for {ticker} ({len(zscore_results)} periods)")
                try:
                    chart_path = self.chart_generator.generate_zscore_dashboard(zscore_results, market_analysis)
                    output_files['chart'] = chart_path
                except Exception as e:
                    logger.warning(f"Chart generation failed for {ticker}: {str(e)}. Continuing with other outputs.")
            
            # Step 4c: Reports (enhanced with market analysis)
            if generate_reports:
                logger.info(f"Step 4c: Generating enhanced reports for {ticker}")
                ai_insights = None
                if include_ai_insights:
                    ai_insights = await self._generate_ai_insights(latest_result, market_analysis)
                report_path = self.report_generator.generate_comprehensive_report(latest_result, ai_insights, market_analysis)
                summary_path = self.report_generator.generate_summary_report(latest_result, market_analysis)
                output_files['report'] = report_path
                output_files['summary'] = summary_path
            
            logger.info(f"Complete investment analysis finished for {ticker}. Generated {len(output_files)} files.")
            return output_files
            
        except Exception as e:
            error_msg = f"Pipeline failed for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise PipelineError(error_msg) from e
    
    async def batch_analyze(
        self, 
        tickers: List[str],
        **kwargs
    ) -> Dict[str, Dict[str, str]]:
        """
        Analyze multiple tickers in batch.
        
        Args:
            tickers: List of ticker symbols
            **kwargs: Additional arguments passed to analyze_ticker
            
        Returns:
            Dict[str, Dict[str, str]]: Results for each ticker
        """
        results = {}
        
        logger.info(f"Starting batch analysis for {len(tickers)} tickers")
        
        for i, ticker in enumerate(tickers, 1):
            try:
                logger.info(f"Processing ticker {i}/{len(tickers)}: {ticker}")
                results[ticker] = await self.analyze_ticker(ticker, **kwargs)
                
            except Exception as e:
                logger.error(f"Failed to process {ticker}: {str(e)}")
                results[ticker] = {'error': str(e)}
        
        logger.info(f"Batch analysis complete. Processed {len(results)} tickers.")
        return results
    
    async def _generate_ai_insights(self, zscore_result, market_analysis=None) -> Optional[str]:
        """
        Generate AI-powered insights combining Z-Score and market analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Market analysis result (optional)
            
        Returns:
            Optional[str]: AI-generated comprehensive insights        """
        try:
            logger.info(f"Generating AI-powered insights for {zscore_result.ticker}")
            
            # Generate comprehensive AI insights combining all analysis
            insights = await self.ai_insights_generator.generate_investment_narrative(
                zscore_result, market_analysis
            )
            
            if insights:
                logger.info(f"AI insights generated for {zscore_result.ticker}: {len(insights)} characters")
                return insights
            else:
                logger.warning(f"No AI insights generated for {zscore_result.ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate AI insights for {zscore_result.ticker}: {str(e)}")
            return None
    
    def get_pipeline_status(self) -> Dict[str, any]:
        """
        Get current pipeline status and health.
        
        Returns:
            Dict: Pipeline status information
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'data_merger': 'Ready',
                'zscore_calculator': 'Ready', 
                'market_analyzer': 'Ready',
                'output_generators': 'Ready',
                'file_manager': 'Ready'
            },
            'storage': self.file_manager.get_storage_summary(),
            'version': '4.0.0'
        }
