"""
Main Pipeline - Complete end-to-end Z-Score analysis pipeline

This module provides the main entry point for complete ticker analysis,
integrating all layers from data fetching through final report generation.

Key Features:
- Complete pipeline orchestration
- Error handling and recovery
- Progress tracking and logging
- Batch processing capabilities
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from altman_zscore.common.config import get_config
from .common.logging_config import get_logger
from .common.exceptions import PipelineError
from .layers.data_fetch.data_merger import DataMerger
from .layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from .layers.output_generation.csv_json_generator import CSVJSONGenerator
from .layers.output_generation.chart_generator import ChartGenerator
from .layers.output_generation.report_generator import ReportGenerator
from .layers.output_generation.file_manager import FileManager

logger = get_logger(__name__)


class AltmanZScorePipeline:
    """Complete Altman Z-Score analysis pipeline."""
    
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
        self.csv_json_generator = CSVJSONGenerator(output_base_path)
        self.chart_generator = ChartGenerator(output_base_path)
        self.report_generator = ReportGenerator(output_base_path)
        self.file_manager = FileManager(output_base_path)
    
    async def analyze_ticker(
        self, 
        ticker: str,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_ai_insights: bool = False,
        start_date: str = None
    ) -> Dict[str, str]:
        """
        Complete analysis for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            generate_charts: Whether to generate visualization charts
            generate_reports: Whether to generate comprehensive reports
            include_ai_insights: Whether to include AI-powered analysis
            start_date: Start date for historical data in YYYY-MM-DD format (default: fetch all available)
            
        Returns:
            Dict[str, str]: Paths to generated output files
        """
        try:
            logger.info(f"Starting complete analysis for {ticker}")
            
            # Step 1: Merge financial data
            logger.info(f"Step 1: Merging financial data for {ticker}")
            merged = await self.data_merger.merge_financial_data(ticker, start_date=start_date)
            if not isinstance(merged, list):
                merged = [merged]
            
            # Step 2: Calculate Z-Score for each period
            logger.info(f"Step 2: Calculating Z-Score for {ticker} ({len(merged)} periods)")
            zscore_results = []
            for data in merged:
                result = self.zscore_calculator.calculate_zscore(data)
                zscore_results.append(result)
            
            # Use the most recent result for dashboard/report
            latest_result = zscore_results[0]
            
            # Step 3a: CSV/JSON report for all results
            logger.info(f"Step 3a: Generating CSV/JSON data for {ticker}")
            csv_path = self.csv_json_generator.generate_csv_report(zscore_results)
            json_path = self.csv_json_generator.generate_json_report(zscore_results)
            output_files = {'csv': csv_path, 'json': json_path}
            
            # Step 3b: Chart using latest result
            if generate_charts:
                logger.info(f"Step 3b: Generating charts for {ticker}")
                chart_path = self.chart_generator.generate_zscore_dashboard(latest_result)
                output_files['chart'] = chart_path
            
            # Step 3c: Reports
            if generate_reports:
                logger.info(f"Step 3c: Generating reports for {ticker}")
                ai_insights = None
                if include_ai_insights:
                    ai_insights = await self._generate_ai_insights(latest_result)
                report_path = self.report_generator.generate_comprehensive_report(latest_result, ai_insights)
                summary_path = self.report_generator.generate_summary_report(latest_result)
                output_files['report'] = report_path
                output_files['summary'] = summary_path
            
            logger.info(f"Analysis complete for {ticker}. Generated {len(output_files)} files.")
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
    
    async def _generate_ai_insights(self, zscore_result) -> Optional[str]:
        """
        Generate AI-powered insights (placeholder for future AI integration).
        
        Args:
            zscore_result: Z-Score calculation result
            
        Returns:
            Optional[str]: AI-generated insights
        """
        # TODO: Integrate with AI analysis layer when available
        logger.info("AI insights generation requested but not yet implemented")
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
                'output_generators': 'Ready',
                'file_manager': 'Ready'
            },
            'storage': self.file_manager.get_storage_summary(),
            'version': '3.9.0'
        }


# Convenience function for single ticker analysis
async def analyze_single_ticker(ticker: str, **kwargs) -> Dict[str, str]:
    """
    Convenience function to analyze a single ticker.
    
    Args:
        ticker: Stock ticker symbol
        **kwargs: Additional arguments
        
    Returns:
        Dict[str, str]: Generated output file paths
    """
    pipeline = AltmanZScorePipeline()
    return await pipeline.analyze_ticker(ticker, **kwargs)


# Convenience function for batch analysis
async def analyze_multiple_tickers(tickers: List[str], **kwargs) -> Dict[str, Dict[str, str]]:
    """
    Convenience function to analyze multiple tickers.
    
    Args:
        tickers: List of ticker symbols
        **kwargs: Additional arguments
        
    Returns:
        Dict[str, Dict[str, str]]: Results for each ticker
    """
    pipeline = AltmanZScorePipeline()
    return await pipeline.batch_analyze(tickers, **kwargs)
