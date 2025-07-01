"""
CSV/JSON Generator - Export Z-Score results to structured data formats

This module generates CSV and JSON outputs from Z-Score calculation results,
providing structured data for external analysis, reporting, and integration.

Key Features:
- CSV export with comprehensive financial metrics
- JSON export with nested data structures
- Batch processing for multiple tickers
- Customizable output formatting and field selection
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..zscore_calculation import ZScoreCalculationResult
from ..._version import __version__

logger = get_logger(__name__)


class CSVJSONGenerator:
    """Generator for CSV and JSON output formats."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize CSV/JSON generator.
        
        Args:
            output_base_path: Base directory for output files
        """        
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_csv_report(self, zscore_results, market_analysis=None, ai_analysis=None):
        """
        Generate CSV report from one or more Z-Score calculation results.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results
            ai_analysis: Optional AI comprehensive analysis results
            
        Returns:
            str: Path to generated CSV file
        """
        # Support single result or list of results
        results = zscore_results if isinstance(zscore_results, list) else [zscore_results]
        try:
            # Use first result's ticker for directory
            ticker = results[0].ticker
            ticker_dir = self.output_base_path / ticker
            ticker_dir.mkdir(exist_ok=True)
            
            csv_path = ticker_dir / f"{ticker}_zscore_report.csv"
            
            # Prepare CSV data for all results (enhanced with market analysis and AI analysis)
            csv_data = []
            for res in results:
                csv_data.extend(self._prepare_csv_data(res, market_analysis, ai_analysis))
            
            # Write CSV file
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Determine all fieldnames across all rows
                all_keys = set()
                for row in csv_data:
                    all_keys.update(row.keys())
                # Preserve order from first row, then append any new keys
                fieldnames = list(csv_data[0].keys())
                for key in sorted(all_keys):
                    if key not in fieldnames:
                        fieldnames.append(key)
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            logger.info(f"Enhanced CSV report generated: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            error_msg = f"Failed to generate CSV report for {zscore_results}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def generate_json_report(self, zscore_results, market_analysis=None, ai_analysis=None) -> str:
        """
        Generate JSON report from Z-Score calculation result.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results
            ai_analysis: Optional AI comprehensive analysis results
            
        Returns:
            str: Path to generated JSON file
        """
        # Support single result or list of results
        results = zscore_results if isinstance(zscore_results, list) else [zscore_results]
        try:
            ticker = results[0].ticker
            ticker_dir = self.output_base_path / ticker
            ticker_dir.mkdir(exist_ok=True)
            
            json_path = ticker_dir / f"{ticker}_zscore_data.json"
            
            # Prepare JSON data for all results
            json_data = [self._prepare_json_data(res, market_analysis, ai_analysis) for res in results]
            
            # Write JSON file
            with open(json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, default=str)
            
            logger.info(f"JSON report generated: {json_path}")
            return str(json_path)
            
        except Exception as e:
            error_msg = f"Failed to generate JSON report for {zscore_results}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _prepare_csv_data(self, zscore_result: ZScoreCalculationResult, market_analysis=None, ai_analysis=None) -> List[Dict[str, Any]]:
        """Prepare data for CSV export."""
        csv_row = {
            'ticker': zscore_result.ticker,
            'z_score': zscore_result.z_score,
            'model_used': zscore_result.model_used,
            'risk_category': zscore_result.risk_category,
            'calculation_date': zscore_result.calculation_timestamp,
            'data_quality_score': zscore_result.data_quality_score,
            'warnings_count': len(zscore_result.warnings),
            'warnings': '; '.join(zscore_result.warnings),
            **zscore_result.component_values
        }
        
        # Add AI analysis data if available
        if ai_analysis:
            # Add LLM final commentary (core AI output)
            csv_row.update({
                'ai_llm_commentary_available': bool(getattr(ai_analysis, 'llm_final_commentary', None)),
                'ai_llm_commentary_length': len(getattr(ai_analysis, 'llm_final_commentary', '') or ''),
                'ai_overall_confidence': getattr(ai_analysis, 'overall_ai_confidence', None),
                'ai_recommendations_count': len(getattr(ai_analysis, 'ai_recommendations', []) or [])
            })
            
            if hasattr(ai_analysis, 'data_quality') and ai_analysis.data_quality:
                csv_row.update({
                    'ai_overall_quality_score': ai_analysis.data_quality.overall_quality_score,
                    'ai_reliability_rating': ai_analysis.data_quality.reliability_rating,
                    'ai_anomalies_count': len(ai_analysis.data_quality.anomalies_detected)
                })
            if hasattr(ai_analysis, 'sentiment_analysis') and ai_analysis.sentiment_analysis:
                csv_row.update({
                    'ai_sentiment_score': getattr(ai_analysis.sentiment_analysis, 'overall_sentiment_score', None),
                    'ai_sentiment_trend': getattr(ai_analysis.sentiment_analysis, 'sentiment_trend', None)
                })
            if hasattr(ai_analysis, 'risk_analysis') and ai_analysis.risk_analysis:
                csv_row.update({
                    'ai_risk_score': getattr(ai_analysis.risk_analysis, 'overall_risk_score', None),
                    'ai_risk_level': getattr(ai_analysis.risk_analysis, 'risk_level', None)
                })
        
        return [csv_row]
    
    def _prepare_json_data(self, zscore_result: ZScoreCalculationResult, market_analysis=None, ai_analysis=None) -> Dict[str, Any]:
        """Prepare data for JSON export."""
        json_data = {
            'ticker': zscore_result.ticker,
            'analysis_summary': {
                'z_score': zscore_result.z_score,
                'risk_category': zscore_result.risk_category,
                'model_used': zscore_result.model_used,
                'calculation_date': zscore_result.calculation_timestamp,
                'data_quality_score': zscore_result.data_quality_score
            },
            'component_values': zscore_result.component_values,
            'warnings': zscore_result.warnings,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': __version__
            }
        }
        
        # Add AI analysis data if available
        if ai_analysis:
            json_data['ai_analysis'] = {
                'llm_final_commentary': getattr(ai_analysis, 'llm_final_commentary', None),
                'overall_confidence': getattr(ai_analysis, 'overall_ai_confidence', None),
                'ai_recommendations': getattr(ai_analysis, 'ai_recommendations', []),
                'analysis_timestamp': getattr(ai_analysis, 'analysis_timestamp', None)
            }
            
            if hasattr(ai_analysis, 'data_quality') and ai_analysis.data_quality:
                json_data['ai_analysis']['data_quality'] = {
                    'overall_score': ai_analysis.data_quality.overall_quality_score,
                    'reliability_rating': ai_analysis.data_quality.reliability_rating,
                    'anomalies_detected': len(ai_analysis.data_quality.anomalies_detected),
                    'recommendation': getattr(ai_analysis.data_quality, 'recommendation', None)
                }
            if hasattr(ai_analysis, 'sentiment_analysis') and ai_analysis.sentiment_analysis:
                json_data['ai_analysis']['sentiment'] = {
                    'overall_score': getattr(ai_analysis.sentiment_analysis, 'overall_sentiment_score', None),
                    'trend': getattr(ai_analysis.sentiment_analysis, 'sentiment_trend', None),
                    'confidence': getattr(ai_analysis.sentiment_analysis, 'confidence', None)
                }
            if hasattr(ai_analysis, 'risk_analysis') and ai_analysis.risk_analysis:
                json_data['ai_analysis']['risk'] = {
                    'overall_score': getattr(ai_analysis.risk_analysis, 'overall_risk_score', None),
                    'risk_level': getattr(ai_analysis.risk_analysis, 'risk_level', None),
                    'key_factors': getattr(ai_analysis.risk_analysis, 'key_risk_factors', [])
                }
        
        return json_data
