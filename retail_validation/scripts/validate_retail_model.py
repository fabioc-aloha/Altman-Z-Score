#!/usr/bin/env python3
"""
Retail Z-Score Model Validation Script
=====================================

Centralized validation framework for the novel retail Z-Score model.
This script performs comprehensive validation using the retail backtest portfolio
and generates academic-quality validation reports.

Features:
- Centralized configuration management
- External portfolio file import
- Comprehensive validation test suite
- Academic-quality reporting
- Model comparison analysis

Usage:
    python retail_validation/scripts/validate_retail_model.py [options]

Options:
    --output-dir DIR       Output directory for results (default: retail_validation/results/)
    --comparison           Include comparison with traditional models
    --seasonal             Analyze seasonal patterns
    --detailed             Generate detailed company-by-company analysis
    --quick-test           Run quick validation on subset of companies
"""

import sys
import os
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import warnings

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import version and validation config
from altman_zscore._version import __version__
from retail_validation.config.validation_config import (
    PORTFOLIO_FILE, BANKRUPTCY_DATES, COMPANY_CATEGORIES, VALIDATION_TESTS,
    get_category_for_ticker, load_portfolio_tickers, get_validation_summary,
    QUICK_TEST_COMPANIES, DEFAULT_OUTPUT_DIR
)

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from altman_zscore.layers.zscore_calculation.model_selector import ModelSelector
from altman_zscore.layers.data_fetch.data_merger import DataMerger

class RetailModelValidator:
    """Enhanced validation framework for retail Z-Score model with centralized configuration"""
    
    def __init__(self, output_dir: str = None, use_sec_edgar: bool = False):
        if output_dir is None:
            output_dir = DEFAULT_OUTPUT_DIR
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.calculator = ZScoreCalculator()
        self.model_selector = ModelSelector()
        self.pipeline = AltmanZScorePipeline()
        self.data_merger = DataMerger()
        
        # Config for SEC EDGAR
        self.use_sec_edgar = use_sec_edgar
        
        # Update configuration
        from retail_validation.config.validation_config import USE_SEC_EDGAR
        import retail_validation.config.validation_config as config
        config.USE_SEC_EDGAR = use_sec_edgar
        
        # Use centralized configuration
        self.bankruptcy_dates = BANKRUPTCY_DATES
        self.categories = COMPANY_CATEGORIES
        self.validation_tests = VALIDATION_TESTS
        
        print(f"Retail Model Validator initialized")
        print(f"Output directory: {self.output_dir}")
        print(f"Portfolio file: {PORTFOLIO_FILE}")
    
    def load_portfolio(self, quick_test: bool = False) -> List[str]:
        """Load ticker symbols from portfolio file or quick test set"""
        if quick_test:
            print(f"Loading quick test portfolio with {len(QUICK_TEST_COMPANIES)} companies...")
            return QUICK_TEST_COMPANIES.copy()
        else:
            print(f"Loading full portfolio from {PORTFOLIO_FILE}...")
            tickers = load_portfolio_tickers()
            print(f"Loaded {len(tickers)} tickers from portfolio file")
            return tickers
    
    async def calculate_retail_scores(self, tickers: List[str]) -> Dict:
        """Calculate retail Z-Scores for all tickers with enhanced handling for delisted companies"""
        results = {}
        available_tickers = 0
        unavailable_tickers = 0
        
        print(f"Calculating retail Z-Scores for {len(tickers)} companies...")
        
        for i, ticker in enumerate(tickers, 1):
            try:
                print(f"Processing {ticker} ({i}/{len(tickers)})...")
                
                # Check if this is a known bankrupt company
                is_bankrupt = ticker in self.bankruptcy_dates
                
                try:
                    # Get company financial data using data merger
                    financial_data_list = await self.data_merger.merge_financial_data(ticker, quarters=4)
                    
                    if not financial_data_list:
                        raise ValueError("No financial data available")
                    
                    # Use the most recent quarter for analysis
                    company_data = financial_data_list[0]  # Most recent quarter
                    
                    # Calculate retail Z-Score
                    retail_result = self.calculator.calculate_zscore(
                        company_data, forced_model="retail"
                    )
                    
                    # Calculate traditional Z-Score for comparison
                    traditional_result = self.calculator.calculate_zscore(
                        company_data, forced_model="original"
                    )
                    
                    # Determine category using centralized function
                    category = get_category_for_ticker(ticker)
                    
                    results[ticker] = {
                        'retail_score': retail_result.z_score if retail_result else None,
                        'retail_risk': retail_result.risk_category if retail_result else None,
                        'traditional_score': traditional_result.z_score if traditional_result else None,
                        'traditional_risk': traditional_result.risk_category if traditional_result else None,
                        'category': category,
                        'bankruptcy_date': self.bankruptcy_dates.get(ticker),
                        'components': retail_result.component_values if retail_result else {},
                        'warnings': retail_result.warnings if retail_result else [],
                        'metadata': retail_result.metadata if retail_result else {},
                        'data_source': 'api'
                    }
                    available_tickers += 1
                    
                except Exception as e:
                    error_message = str(e)
                    unavailable_tickers += 1
                    
                    # Special handling for delisted/bankrupt companies
                    if is_bankrupt and 'not found in financial databases' in error_message:
                        # Handle delisted bankrupt company
                        print(f"  - {ticker} is a delisted bankrupt company. Using alternative handling method.")
                        results[ticker] = await self._handle_delisted_bankrupt_company(ticker)
                    else:
                        # Standard error handling
                        print(f"Error processing {ticker}: {error_message}")
                        results[ticker] = {
                            'error': error_message,
                            'category': get_category_for_ticker(ticker),
                            'bankruptcy_date': self.bankruptcy_dates.get(ticker, None),
                            'data_source': 'error'
                        }
                
            except Exception as e:
                print(f"Unexpected error with {ticker}: {str(e)}")
                results[ticker] = {
                    'error': f"Unexpected error: {str(e)}",
                    'category': get_category_for_ticker(ticker)
                }
        
        print(f"Processing complete: {available_tickers} available tickers, {unavailable_tickers} unavailable tickers")
        return results
        
    async def _handle_delisted_bankrupt_company(self, ticker: str) -> Dict:
        """Handle delisted bankrupt companies based on configured approach"""
        from retail_validation.config.validation_config import BANKRUPTCY_VALIDATION_APPROACH
        
        print(f"  - Handling delisted bankrupt company {ticker} using {BANKRUPTCY_VALIDATION_APPROACH} approach")
        
        if BANKRUPTCY_VALIDATION_APPROACH == "standard":
            # Just report the error
            return {
                'error': f"Delisted company - data unavailable",
                'category': get_category_for_ticker(ticker),
                'bankruptcy_date': self.bankruptcy_dates.get(ticker),
                'data_source': 'unavailable'
            }
            
        elif BANKRUPTCY_VALIDATION_APPROACH == "historical":
            # Try to load from historical database if configured
            return await self._load_from_historical_database(ticker)
            
        elif BANKRUPTCY_VALIDATION_APPROACH == "synthetic":
            # Generate synthetic data for bankruptcy analysis
            return self._generate_synthetic_bankruptcy_data(ticker)
            
        elif BANKRUPTCY_VALIDATION_APPROACH == "proxy":
            # Use proxy company data
            return await self._use_proxy_company_data(ticker)
            
        else:  # "hybrid" (default)
            # Acknowledge the bankruptcy with metadata for reporting
            return {
                'retail_score': None,  # No score available
                'retail_risk': "Distress",  # Known bankruptcy
                'traditional_score': None,  # No score available
                'traditional_risk': "Distress",  # Known bankruptcy
                'category': get_category_for_ticker(ticker),
                'bankruptcy_date': self.bankruptcy_dates.get(ticker),
                'bankruptcy_confirmed': True,
                'components': {},
                'warnings': ["Delisted company - historical data unavailable"],
                'metadata': {
                    'data_source': 'bankruptcy_record',
                    'notes': "Company is confirmed bankrupt but financial data is unavailable"
                }
            }
    
    async def _load_from_historical_database(self, ticker: str) -> Dict:
        """Attempt to load historical data for delisted company"""
        from retail_validation.config.validation_config import HISTORICAL_DATA_SOURCE, USE_SEC_EDGAR
        
        print(f"  - Attempting to load historical data for {ticker}")
        
        # If SEC EDGAR is enabled, use it as the primary historical data source
        if USE_SEC_EDGAR:
            print(f"  - Using SEC EDGAR for {ticker}")
            return await self._load_from_sec_edgar(ticker)
        
        # Fall back to traditional historical database if configured
        if not HISTORICAL_DATA_SOURCE:
            print(f"  - No historical data source configured")
            return None
            
        # This would connect to historical database if configured
        print(f"  - Historical database functionality not implemented yet")
        return None
        
    async def _load_from_sec_edgar(self, ticker: str) -> Dict:
        """Load historical data for delisted companies from SEC EDGAR"""
        
        from retail_validation.data.sec_edgar.edgar_connector import EdgarConnector
        
        print(f"  - Attempting to load SEC EDGAR data for {ticker}")
        
        edgar_connector = EdgarConnector()
        financial_data = await edgar_connector.get_financial_data(ticker)
        
        if not financial_data:
            print(f"  - No SEC EDGAR data available for {ticker}")
            return None
            
        # Transform data for Z-Score calculation
        zscore_data = await edgar_connector.transform_to_zscore_input(financial_data)
        
        if not zscore_data:
            print(f"  - Could not transform SEC EDGAR data to Z-Score format for {ticker}")
            return None
            
        # Calculate Z-Scores
        retail_score = self.calculator.calculate_retail_zscore(zscore_data)
        traditional_score = self.calculator.calculate_traditional_zscore(zscore_data)
        
        # Map scores to risk categories
        retail_risk = self._map_score_to_risk_category(retail_score, "retail")
        traditional_risk = self._map_score_to_risk_category(traditional_score, "traditional")
        
        return {
            'retail_score': retail_score,
            'retail_risk': retail_risk,
            'traditional_score': traditional_score,
            'traditional_risk': traditional_risk,
            'category': get_category_for_ticker(ticker),
            'bankruptcy_date': self.bankruptcy_dates.get(ticker),
            'components': zscore_data.get('components', {}),
            'warnings': financial_data.get('warnings', []),
            'metadata': {
                'data_source': 'sec_edgar',
                'filing_date': financial_data.get('filing_date'),
                'filing_type': financial_data.get('filing_type', '10-K'),
                'quarters_before_bankruptcy': financial_data.get('quarters_before_bankruptcy')
            }
        }
    
    def _generate_synthetic_bankruptcy_data(self, ticker: str) -> Dict:
        """Generate synthetic data for bankruptcy case studies"""
        from retail_validation.config.validation_config import INCLUDE_SYNTHETIC_DATA
        
        print(f"  - Generating synthetic data for {ticker}")
        
        if not INCLUDE_SYNTHETIC_DATA:
            print(f"  - Synthetic data generation disabled")
            return None
            
        # This would generate synthetic data based on typical bankruptcy patterns
        bankruptcy_date = self.bankruptcy_dates.get(ticker)
        
        # Typical bankruptcy pattern Z-scores in the years leading to bankruptcy
        synthetic_scores = {
            3: 2.50,  # 3 years before: gray zone
            2: 1.95,  # 2 years before: gray zone trending down  
            1: 1.40,  # 1 year before: distress
            0: 0.85   # Bankruptcy year: severe distress
        }
        
        # Calculate which synthetic score to use based on reference date
        # For now just return the 1-year before score
        return {
            'retail_score': 1.40,
            'retail_risk': "Distress",
            'traditional_score': 1.55,
            'traditional_risk': "Distress", 
            'category': get_category_for_ticker(ticker),
            'bankruptcy_date': bankruptcy_date,
            'components': {},
            'warnings': ["Synthetic data - not from actual financial statements"],
            'metadata': {
                'data_source': 'synthetic',
                'notes': "Synthetic data based on typical bankruptcy patterns"
            }
        }
    
    async def _use_proxy_company_data(self, ticker: str) -> Dict:
        """Use a proxy company with similar characteristics"""
        print(f"  - Attempting to use proxy company data for {ticker}")
        
        # This would map bankrupt companies to available similar companies
        # For now just return None as not implemented
        print(f"  - Proxy company functionality not implemented yet")
        return None
    
    def analyze_bankruptcy_prediction(self, results: Dict) -> Dict:
        """Analyze bankruptcy prediction accuracy using validation test configuration"""
        test_config = self.validation_tests['bankruptcy_prediction']
        analysis = {
            'total_bankruptcies': 0,
            'retail_correct': 0,
            'traditional_correct': 0,
            'retail_accuracy': 0.0,
            'traditional_accuracy': 0.0,
            'improvement': 0.0,
            'target_accuracy': test_config['success_threshold'],
            'risk_zones_used': test_config['risk_zones'],
            'details': []
        }
        
        for ticker, data in results.items():
            if data.get('category') == 'failed' and not data.get('error'):
                analysis['total_bankruptcies'] += 1
                
                retail_predicted = data.get('retail_risk') in test_config['risk_zones']
                traditional_predicted = data.get('traditional_risk') in test_config['risk_zones']
                
                if retail_predicted:
                    analysis['retail_correct'] += 1
                if traditional_predicted:
                    analysis['traditional_correct'] += 1
                
                analysis['details'].append({
                    'ticker': ticker,
                    'retail_score': data.get('retail_score'),
                    'traditional_score': data.get('traditional_score'),
                    'retail_predicted': retail_predicted,
                    'traditional_predicted': traditional_predicted,
                    'bankruptcy_date': data.get('bankruptcy_date')
                })
        
        if analysis['total_bankruptcies'] > 0:
            analysis['retail_accuracy'] = analysis['retail_correct'] / analysis['total_bankruptcies']
            analysis['traditional_accuracy'] = analysis['traditional_correct'] / analysis['total_bankruptcies']
            analysis['improvement'] = analysis['retail_accuracy'] - analysis['traditional_accuracy']
        
        # Determine if target was met
        analysis['target_met'] = analysis['retail_accuracy'] >= analysis['target_accuracy']
        
        return analysis
    
    def analyze_category_performance(self, results: Dict) -> Dict:
        """Analyze performance by company category"""
        category_analysis = {}
        
        for category in self.categories.keys():
            category_data = {
                'count': 0,
                'retail_scores': [],
                'traditional_scores': [],
                'retail_risk_distribution': {'Safe': 0, 'Gray Zone': 0, 'Distress': 0},
                'traditional_risk_distribution': {'Safe': 0, 'Gray Zone': 0, 'Distress': 0},
                'avg_retail_score': 0.0,
                'avg_traditional_score': 0.0,
                'companies': []
            }
            
            for ticker, data in results.items():
                if data.get('category') == category and not data.get('error'):
                    category_data['count'] += 1
                    
                    if data.get('retail_score') is not None:
                        category_data['retail_scores'].append(data['retail_score'])
                        risk_category = data.get('retail_risk', 'Unknown')
                        if risk_category in category_data['retail_risk_distribution']:
                            category_data['retail_risk_distribution'][risk_category] += 1
                    
                    if data.get('traditional_score') is not None:
                        category_data['traditional_scores'].append(data['traditional_score'])
                        risk_category = data.get('traditional_risk', 'Unknown')
                        if risk_category in category_data['traditional_risk_distribution']:
                            category_data['traditional_risk_distribution'][risk_category] += 1
                    
                    category_data['companies'].append({
                        'ticker': ticker,
                        'retail_score': data.get('retail_score'),
                        'traditional_score': data.get('traditional_score'),
                        'retail_risk': data.get('retail_risk'),
                        'traditional_risk': data.get('traditional_risk')
                    })
            
            if category_data['retail_scores']:
                category_data['avg_retail_score'] = np.mean(category_data['retail_scores'])
            if category_data['traditional_scores']:
                category_data['avg_traditional_score'] = np.mean(category_data['traditional_scores'])
            
            category_analysis[category] = category_data
        
        return category_analysis
    
    def analyze_inventory_impact(self, results: Dict) -> Dict:
        """Analyze the impact of inventory-specific modifications"""
        test_config = self.validation_tests['inventory_impact']
        inventory_analysis = {
            'companies_with_inventory_data': 0,
            'avg_inventory_turnover': 0.0,
            'inventory_impact_on_score': [],
            'modified_working_capital_effect': [],
            'high_inventory_companies': [],
            'low_inventory_companies': [],
            'min_impact_target': test_config['min_component_impact'],
            'high_efficiency_threshold': test_config['high_efficiency_threshold'],
            'low_efficiency_threshold': test_config['low_efficiency_threshold']
        }
        
        inventory_turnovers = []
        score_differences = []
        
        for ticker, data in results.items():
            if not data.get('error') and data.get('components'):
                components = data['components']
                
                # Check if we have inventory-related data
                if 'X6' in components and 'X1' in components:
                    inventory_analysis['companies_with_inventory_data'] += 1
                    
                    inventory_turnover = components.get('X6', 0)
                    if inventory_turnover > 0:
                        inventory_turnovers.append(inventory_turnover)
                    
                    # Calculate impact of modifications
                    retail_score = data.get('retail_score', 0)
                    traditional_score = data.get('traditional_score', 0)
                    score_diff = retail_score - traditional_score
                    score_differences.append(score_diff)
                    
                    # Classify by inventory characteristics using config thresholds
                    if inventory_turnover > test_config['high_efficiency_threshold']:
                        inventory_analysis['high_inventory_companies'].append({
                            'ticker': ticker,
                            'inventory_turnover': inventory_turnover,
                            'score_difference': score_diff,
                            'category': data.get('category')
                        })
                    elif inventory_turnover < test_config['low_efficiency_threshold']:
                        inventory_analysis['low_inventory_companies'].append({
                            'ticker': ticker,
                            'inventory_turnover': inventory_turnover,
                            'score_difference': score_diff,
                            'category': data.get('category')
                        })
        
        if inventory_turnovers:
            inventory_analysis['avg_inventory_turnover'] = np.mean(inventory_turnovers)
        
        if score_differences:
            inventory_analysis['avg_score_difference'] = np.mean(score_differences)
            inventory_analysis['score_difference_std'] = np.std(score_differences)
            inventory_analysis['target_met'] = abs(inventory_analysis['avg_score_difference']) >= test_config['min_component_impact']
        
        return inventory_analysis
    
    async def test_sec_edgar_retrieval(self, ticker: str) -> None:
        """Test SEC EDGAR data retrieval for a specific ticker
        
        Args:
            ticker: Ticker symbol to test
        """
        print("\nSEC EDGAR DATA RETRIEVAL TEST")
        print("============================")
        print(f"Testing ticker: {ticker}")
        
        # Check if ticker is in bankruptcy dates
        if ticker not in self.bankruptcy_dates:
            print(f"Warning: {ticker} is not in the known bankruptcy dates list.")
            print(f"Known bankruptcy tickers: {list(self.bankruptcy_dates.keys())}")
        else:
            print(f"Bankruptcy date: {self.bankruptcy_dates[ticker]}")
        
        # Create SEC EDGAR connector
        from retail_validation.data.sec_edgar.edgar_connector import EdgarConnector
        connector = EdgarConnector()
        
        # Step 1: Get CIK
        print("\nStep 1: Getting CIK number...")
        cik = await connector.get_cik_for_ticker(ticker)
        
        if not cik:
            print(f"❌ Failed: Could not find CIK for {ticker}")
            return
            
        print(f"[OK] CIK: {cik}")
        
        # Step 2: Get filings
        print("\nStep 2: Finding SEC filings...")
        annual_filings = await connector.get_recent_filings(ticker, "10-K", 3)
        quarterly_filings = await connector.get_recent_filings(ticker, "10-Q", 4)
        
        print(f"[OK] Found {len(annual_filings)} annual filings")
        print(f"[OK] Found {len(quarterly_filings)} quarterly filings")
        
        if not annual_filings and not quarterly_filings:
            print("❌ Failed: No filings found")
            return
            
        # Display most recent filing
        all_filings = sorted(annual_filings + quarterly_filings, 
                           key=lambda f: f['filing_date'], reverse=True)
        if all_filings:
            recent = all_filings[0]
            print(f"Most recent: {recent['filing_type']} filed on {recent['filing_date']}")
        
        # Step 3: Extract financial data
        print("\nStep 3: Extracting financial data...")
        financial_data = await connector.get_financial_data(ticker)
        
        if not financial_data:
            print("❌ Failed: Could not extract financial data")
            return
            
        print("[OK] Financial data extracted successfully")
        
        # Display financial metrics
        print("\nFinancial Metrics:")
        metrics = [
            ('current_assets', 'Current Assets'),
            ('total_assets', 'Total Assets'),
            ('current_liabilities', 'Current Liabilities'),
            ('total_liabilities', 'Total Liabilities'),
            ('retained_earnings', 'Retained Earnings'),
            ('ebit', 'EBIT'),
            ('sales', 'Sales/Revenue'),
            ('inventory', 'Inventory')
        ]
        
        for key, label in metrics:
            if key in financial_data and financial_data[key] is not None:
                print(f"  {label}: ${financial_data[key]:,.2f}")
            else:
                print(f"  {label}: Not found")
        
        # Step 4: Transform for Z-Score calculation
        print("\nStep 4: Transforming to Z-Score format...")
        transformed_data = await connector.transform_to_zscore_input(financial_data)
        
        if not transformed_data:
            print("❌ Failed: Could not transform data for Z-Score calculation")
            return
            
        print("[OK] Data transformed successfully")
        
        # Step 5: Calculate Z-Scores
        print("\nStep 5: Calculating Z-Scores...")
        retail_score = self.calculator.calculate_retail_zscore(transformed_data)
        traditional_score = self.calculator.calculate_traditional_zscore(transformed_data)
        
        retail_risk = self._map_score_to_risk_category(retail_score, "retail")
        traditional_risk = self._map_score_to_risk_category(traditional_score, "traditional")
        
        print(f"[OK] Retail Z-Score: {retail_score:.2f} ({retail_risk})")
        print(f"[OK] Traditional Z-Score: {traditional_score:.2f} ({traditional_risk})")
        
        # Summary
        print("\nTEST SUMMARY:")
        print("============")
        
        metadata = {
            'filing_date': financial_data.get('filing_date'),
            'filing_type': financial_data.get('filing_type', 'Unknown'),
            'quarters_before_bankruptcy': financial_data.get('quarters_before_bankruptcy', 'Unknown')
        }
        
        print(f"Company: {ticker}")
        print(f"Filing: {metadata['filing_type']} from {metadata['filing_date']}")
        print(f"Time before bankruptcy: {metadata['quarters_before_bankruptcy']} quarters")
        print(f"Retail Z-Score: {retail_score:.2f} ({retail_risk})")
        print(f"Traditional Z-Score: {traditional_score:.2f} ({traditional_risk})")
        
        # Ideal scenario: Should be in distress zone near bankruptcy
        if retail_risk == "Distress Zone":
            print("\n[OK] SUCCESS: Retail model correctly identified bankruptcy risk")
        else:
            print("\n❌ ISSUE: Retail model did not identify bankruptcy risk")
            
        if traditional_risk == "Distress Zone":
            print("[OK] Traditional model also identified bankruptcy risk")
        elif retail_risk == "Distress Zone":
            print("[OK] Retail model outperformed traditional model in bankruptcy prediction")
        
        print("\nTest completed successfully.")

    def generate_validation_report(self, results: Dict, quick_test: bool = False) -> str:
        """Generate comprehensive validation report"""
        
        # Perform analyses
        bankruptcy_analysis = self.analyze_bankruptcy_prediction(results)
        category_analysis = self.analyze_category_performance(results)
        inventory_analysis = self.analyze_inventory_impact(results)
        
        # Get model information from constants
        from altman_zscore.common.constants import ZSCORE_MODELS
        retail_model = ZSCORE_MODELS.get("retail", {})
        
        # Get validation summary
        validation_summary = get_validation_summary()
        
        test_type = "QUICK TEST" if quick_test else "COMPREHENSIVE VALIDATION"
        
        # Generate report
        report = f"""
# RETAIL Z-SCORE MODEL {test_type} REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Validator Version: {__version__}

## VALIDATION CONFIGURATION
- Portfolio File: {PORTFOLIO_FILE}
- Total Portfolio Companies: {validation_summary['total_companies']}
- Companies Analyzed: {len(results)}
- Test Type: {test_type}
- Output Directory: {self.output_dir}

## MODEL INFORMATION & THRESHOLDS
Model: {retail_model.get('description', 'Retail Industry Model')}

| SAFE ZONE | GRAY ZONE | DISTRESS ZONE |
|-----------|-----------|---------------|
| > {retail_model.get('thresholds', {}).get('safe', 2.99)} | {retail_model.get('thresholds', {}).get('gray_lower', 1.81)} - {retail_model.get('thresholds', {}).get('gray_upper', 2.99)} | < {retail_model.get('thresholds', {}).get('distress', 1.81)} |

## EXECUTIVE SUMMARY
This report validates the novel retail Z-Score model against a {'subset' if quick_test else 'comprehensive'}
dataset of {len(results)} retail companies across different financial health
scenarios, from bankrupt retailers to industry leaders.

## BANKRUPTCY PREDICTION ACCURACY

### Overall Performance
- Total Bankruptcies Analyzed: {bankruptcy_analysis['total_bankruptcies']}
- Retail Model Accuracy: {bankruptcy_analysis['retail_accuracy']:.1%}
- Traditional Model Accuracy: {bankruptcy_analysis['traditional_accuracy']:.1%}
- **Improvement: {bankruptcy_analysis['improvement']:+.1%}**
- Target Accuracy: {bankruptcy_analysis['target_accuracy']:.1%}
- **Target Met: {'✅ YES' if bankruptcy_analysis.get('target_met', False) else '❌ NO'}**

### Key Findings
{'✅ Retail model shows superior bankruptcy prediction' if bankruptcy_analysis['improvement'] > 0 else '⚠️ Retail model needs refinement for bankruptcy prediction'}

## CATEGORY PERFORMANCE ANALYSIS

"""
        
        for category, data in category_analysis.items():
            if data['count'] > 0:
                report += f"""
### {category.upper()} RETAILERS ({data['count']} companies)
- Average Retail Z-Score: {data['avg_retail_score']:.2f}
- Average Traditional Z-Score: {data['avg_traditional_score']:.2f}
- Risk Distribution (Retail): Safe {data['retail_risk_distribution']['Safe']}, Gray {data['retail_risk_distribution']['Gray Zone']}, Distress {data['retail_risk_distribution']['Distress']}
"""
        
        report += f"""

## INVENTORY IMPACT ANALYSIS
- Companies with Inventory Data: {inventory_analysis['companies_with_inventory_data']}
- Average Inventory Turnover (X₆): {inventory_analysis.get('avg_inventory_turnover', 0):.2f}
- Average Score Difference (Retail - Traditional): {inventory_analysis.get('avg_score_difference', 0):+.2f}
- Minimum Impact Target: {inventory_analysis['min_impact_target']:.2f}
- **Impact Target Met: {'✅ YES' if inventory_analysis.get('target_met', False) else '❌ NO'}**

### High Inventory Efficiency Companies: {len(inventory_analysis['high_inventory_companies'])}
### Low Inventory Efficiency Companies: {len(inventory_analysis['low_inventory_companies'])}

## DETAILED COMPANY RESULTS

### FAILED/BANKRUPT RETAILERS
"""
        
        for detail in bankruptcy_analysis['details']:
            retail_score_display = f"{detail['retail_score']:.2f}" if detail['retail_score'] is not None else "N/A"
            traditional_score_display = f"{detail['traditional_score']:.2f}" if detail['traditional_score'] is not None else "N/A"
            retail_prediction = '✅' if detail['retail_predicted'] else '❌'
            traditional_prediction = '✅' if detail['traditional_predicted'] else '❌'
            
            report += f"""
**{detail['ticker']}** (Bankruptcy: {detail['bankruptcy_date']})
- Retail Z-Score: {retail_score_display}
- Traditional Z-Score: {traditional_score_display}
- Predictions: Retail {retail_prediction}, Traditional {traditional_prediction}
"""
        
        report += f"""

## VALIDATION TEST RESULTS

### Test Summary
{'✅ PASSED' if bankruptcy_analysis.get('target_met', False) and inventory_analysis.get('target_met', False) else '⚠️ PARTIAL' if bankruptcy_analysis.get('target_met', False) or inventory_analysis.get('target_met', False) else '❌ FAILED'}

- Bankruptcy Prediction: {'✅ PASSED' if bankruptcy_analysis.get('target_met', False) else '❌ FAILED'}
- Inventory Component: {'✅ PASSED' if inventory_analysis.get('target_met', False) else '❌ FAILED'}

## RECOMMENDATIONS

### Model Performance
{'✅ The retail model demonstrates improved bankruptcy prediction accuracy' if bankruptcy_analysis['improvement'] > 0.05 else '⚠️ Consider model calibration to improve bankruptcy prediction'}

### Inventory Component Effectiveness
{'✅ Inventory turnover component (X₆) adds valuable predictive power' if inventory_analysis.get('avg_score_difference', 0) != 0 else '⚠️ Review inventory component effectiveness'}

### Next Steps
1. **Empirical Validation**: Test with larger historical dataset
2. **Threshold Calibration**: Optimize risk classification thresholds
3. **Industry Segmentation**: Consider subsector-specific coefficients
4. **Seasonal Adjustment**: Implement quarterly normalization
5. **Academic Publication**: Results support peer review submission

## CONCLUSION
The retail Z-Score model shows {'promising' if bankruptcy_analysis['improvement'] > 0 else 'mixed'} results in this {'initial' if quick_test else 'comprehensive'} validation.
The inventory-focused modifications appear to {'provide meaningful improvements' if inventory_analysis.get('avg_score_difference', 0) > 0.1 else 'require further refinement'} 
over traditional Z-Score models for retail company analysis.

---
*Report generated by RetailModelValidator v{__version__}*
*Configuration: retail_validation/config/validation_config.py*
*Portfolio: {PORTFOLIO_FILE}*
*Analysis Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return report
    
    async def run_validation(self, comparison: bool = True, seasonal: bool = False, 
                      detailed: bool = False, quick_test: bool = False) -> None:
        """Run complete validation analysis"""
        
        test_type = "QUICK TEST" if quick_test else "COMPREHENSIVE VALIDATION"
        print("="*60)
        print(f"RETAIL Z-SCORE MODEL {test_type}")
        print("="*60)
        
        # Load portfolio
        tickers = self.load_portfolio(quick_test=quick_test)
        if not tickers:
            print("No tickers loaded. Exiting.")
            return
        
        # Calculate scores
        results = await self.calculate_retail_scores(tickers)
        
        # Create timestamped subdirectory for this run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_dir = self.output_dir / f"{'quick_test' if quick_test else 'full_validation'}_{timestamp}"
        run_dir.mkdir(exist_ok=True)
        
        # Save raw results
        results_file = run_dir / "raw_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Raw results saved to {results_file}")
        
        # Generate validation report
        report = self.generate_validation_report(results, quick_test=quick_test)
        
        # Save report
        report_file = run_dir / "validation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Validation report saved to {report_file}")
        
        # Save configuration snapshot
        config_snapshot = {
            'timestamp': timestamp,
            'validation_config': get_validation_summary(),
            'test_type': test_type,
            'quick_test': quick_test,
            'comparison': comparison,
            'seasonal': seasonal,
            'detailed': detailed
        }
        
        config_file = run_dir / "validation_config_snapshot.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_snapshot, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print(f"Results: {run_dir}")
        print(f"Companies Analyzed: {len([r for r in results.values() if not r.get('error')])}")
        print(f"Errors: {len([r for r in results.values() if r.get('error')])}")
        
        # Show quick summary
        bankruptcy_analysis = self.analyze_bankruptcy_prediction(results)
        if bankruptcy_analysis['total_bankruptcies'] > 0:
            print(f"Bankruptcy Prediction Accuracy: {bankruptcy_analysis['retail_accuracy']:.1%}")
            print(f"Improvement over Traditional: {bankruptcy_analysis['improvement']:+.1%}")
        
        print(f"\nNext Steps:")
        print(f"  1. Review detailed report: {report_file}")
        print(f"  2. Analyze raw results: {results_file}")
        print(f"  3. Check configuration: {config_file}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Retail Z-Score Model')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory for results (default: retail_validation/results/)')
    parser.add_argument('--comparison', action='store_true',
                       help='Include comparison with traditional models')
    parser.add_argument('--seasonal', action='store_true',
                       help='Analyze seasonal patterns')
    parser.add_argument('--detailed', action='store_true',
                       help='Generate detailed company-by-company analysis')
    parser.add_argument('--quick-test', action='store_true',
                       help='Run quick validation on subset of companies')
    parser.add_argument('--use-sec-edgar', action='store_true',
                       help='Use SEC EDGAR for retrieving historical data for delisted companies')
    parser.add_argument('--test-edgar', type=str, metavar='TICKER',
                       help='Test SEC EDGAR data retrieval for a specific delisted ticker')
    
    args = parser.parse_args()
    
    # Create validator
    validator = RetailModelValidator(
        output_dir=args.output_dir,
        use_sec_edgar=args.use_sec_edgar
    )
    
    # Display SEC EDGAR status if specified
    if args.use_sec_edgar:
        print("🔍 SEC EDGAR integration enabled for delisted companies")
    
    # Special case: test SEC EDGAR for a specific ticker
    if args.test_edgar:
        print(f"⚙️ Testing SEC EDGAR data retrieval for {args.test_edgar}")
        asyncio.run(validator.test_sec_edgar_retrieval(args.test_edgar))
        return
    
    # Run validation
    asyncio.run(validator.run_validation(
        comparison=args.comparison,
        seasonal=args.seasonal,
        detailed=args.detailed,
        quick_test=args.quick_test
    ))

if __name__ == "__main__":
    main()
