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
    
    def generate_csv_report(self, zscore_results, market_analysis=None):
        """
        Generate CSV report from one or more Z-Score calculation results.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results
            
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
            
            # Prepare CSV data for all results (enhanced with market analysis)
            csv_data = []
            for res in results:
                csv_data.extend(self._prepare_csv_data(res, market_analysis))
            
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
    
    def generate_json_report(self, zscore_results, market_analysis=None) -> str:
        """
        Generate JSON report from Z-Score calculation result.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results
            
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
            json_data = [self._prepare_json_data(res, market_analysis) for res in results]
            
            # Write JSON file
            with open(json_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, default=str)
            
            logger.info(f"JSON report generated: {json_path}")
            return str(json_path)
            
        except Exception as e:
            error_msg = f"Failed to generate JSON report for {zscore_results}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _prepare_csv_data(self, zscore_result: ZScoreCalculationResult, market_analysis=None) -> List[Dict[str, Any]]:
        """Prepare data for CSV export."""
        return [{
            'ticker': zscore_result.ticker,
            'z_score': zscore_result.z_score,            'model_used': zscore_result.model_used,
            'risk_category': zscore_result.risk_category,
            'calculation_date': zscore_result.calculation_timestamp,
            'data_quality_score': zscore_result.data_quality_score,
            'warnings_count': len(zscore_result.warnings),
            'warnings': '; '.join(zscore_result.warnings),
            **zscore_result.component_values
        }]
    
    def _prepare_json_data(self, zscore_result: ZScoreCalculationResult, market_analysis=None) -> Dict[str, Any]:
        """Prepare data for JSON export."""
        return {
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
                'generator_version': '3.8.0-dev'
            }
        }
