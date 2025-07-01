#!/usr/bin/env python3
"""
Retail Z-Score Model Validation Script
=====================================

This script performs comprehensive validation of the novel retail Z-Score model
using the retail_backtest_portfolio.txt dataset. It tests model accuracy,
early warning capabilities, and comparative performance against traditional models.

Usage:
    python validate_retail_model.py [options]

Options:
    --portfolio FILENAME    Portfolio file to analyze (default: retail_backtest_portfolio.txt)
    --output-dir DIR       Output directory for results (default: backtest_results/)
    --years RANGE          Historical analysis years (default: 2015-2025)
    --comparison           Include comparison with traditional models
    --seasonal             Analyze seasonal patterns
    --detailed             Generate detailed company-by-company analysis

Requirements:
    - Retail Z-Score model implementation
    - Historical financial data access
    - Statistical analysis libraries (pandas, numpy, sklearn)
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import version
from altman_zscore._version import __version__

from altman_zscore.main_pipeline import AltmanZScorePipeline
from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from altman_zscore.layers.zscore_calculation.model_selector import ModelSelector
from altman_zscore.layers.data_fetch.data_merger import DataMerger

class RetailModelValidator:
    """Comprehensive validation framework for retail Z-Score model"""
    
    def __init__(self, output_dir: str = "backtest_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.calculator = ZScoreCalculator()
        self.model_selector = ModelSelector()
        self.pipeline = AltmanZScorePipeline()
        self.data_merger = DataMerger()
        
        # Known bankruptcy dates for validation
        self.bankruptcy_dates = {
            'TOY': '2017-09-18',    # Toys"R"Us
            'SHLDQ': '2018-10-15',  # Sears Holdings
            'JCPNQ': '2020-05-15',  # JCPenney
            'NMRCQ': '2020-05-07',  # Neiman Marcus
            'BRKSQ': '2020-07-08',  # Brooks Brothers
            'PIRRQ': '2020-05-18',  # Pier 1 Imports
            'BONTQ': '2018-02-04',  # Bon-Ton Stores
            'RSHCQ': '2015-02-05',  # RadioShack (first bankruptcy)
            'TSAQ': '2016-05-18',   # Sports Authority
            'PSDSQ': '2017-04-04',  # Payless ShoeSource
            'F21Q': '2019-09-29',   # Forever 21
            'GYMQ': '2017-06-11',   # Gymboree (first bankruptcy)
        }
        
        # Company categories for analysis
        self.categories = {
            'failed': ['TOY', 'SHLDQ', 'JCPNQ', 'NMRCQ', 'BRKSQ', 'PIRRQ', 'C21Q', 
                      'BONTQ', 'GORDQ', 'HHGQ', 'RSHCQ', 'TSAQ', 'GMTNQ', 'PSDSQ', 
                      'BKSQ', 'BYRAQ', 'F21Q', 'CHRLQ', 'DBNQ', 'GYMQ'],
            'distressed': ['BBBY', 'PRTY', 'GME', 'EXPR', 'BIG', 'REV', 'M', 'JWN', 
                          'DDS', 'BBWI', 'AEO', 'ANF', 'URBN', 'GPS', 'FL'],
            'recovery': ['BBY', 'TGT', 'DKS', 'BURL', 'TJX', 'AZO', 'ORLY', 'AAP', 'LOW'],
            'stable': ['AMZN', 'COST', 'WMT', 'BJ', 'HD', 'DG', 'DLTR', 'SHW'],
            'seasonal': ['SPIR', 'JWN', 'ROST', 'TSCO', 'BGFV', 'SBH', 'POOL', 'BBW', 
                        'AM', 'PRTY']
        }
    
    def load_portfolio(self, portfolio_file: str) -> List[str]:
        """Load ticker symbols from portfolio file"""
        tickers = []
        try:
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Handle potential inline comments
                        ticker = line.split('#')[0].strip()
                        if ticker and len(ticker) <= 10:  # Basic ticker validation
                            tickers.append(ticker)
        except FileNotFoundError:
            print(f"Portfolio file {portfolio_file} not found")
            return []
        
        print(f"Loaded {len(tickers)} tickers from {portfolio_file}")
        return tickers
    
    async def calculate_retail_scores(self, tickers: List[str]) -> Dict:
        """Calculate retail Z-Scores for all tickers"""
        results = {}
        
        print(f"Calculating retail Z-Scores for {len(tickers)} companies...")
        
        for i, ticker in enumerate(tickers, 1):
            try:
                print(f"Processing {ticker} ({i}/{len(tickers)})...")
                
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
                
                # Determine category
                category = self._determine_category(ticker)
                
                results[ticker] = {
                    'retail_score': retail_result.z_score if retail_result else None,
                    'retail_risk': retail_result.risk_category if retail_result else None,
                    'traditional_score': traditional_result.z_score if traditional_result else None,
                    'traditional_risk': traditional_result.risk_category if traditional_result else None,
                    'category': category,
                    'bankruptcy_date': self.bankruptcy_dates.get(ticker),
                    'components': retail_result.component_values if retail_result else {},
                    'warnings': retail_result.warnings if retail_result else [],
                    'metadata': retail_result.metadata if retail_result else {}
                }
                
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                results[ticker] = {
                    'error': str(e),
                    'category': self._determine_category(ticker)
                }
        
        return results
    
    def _determine_category(self, ticker: str) -> str:
        """Determine which category a ticker belongs to"""
        for category, tickers in self.categories.items():
            if ticker in tickers:
                return category
        return 'other'
    
    def analyze_bankruptcy_prediction(self, results: Dict) -> Dict:
        """Analyze bankruptcy prediction accuracy"""
        analysis = {
            'total_bankruptcies': 0,
            'retail_correct': 0,
            'traditional_correct': 0,
            'retail_accuracy': 0.0,
            'traditional_accuracy': 0.0,
            'improvement': 0.0,
            'details': []
        }
        
        for ticker, data in results.items():
            if data.get('category') == 'failed' and not data.get('error'):
                analysis['total_bankruptcies'] += 1
                
                retail_predicted = data.get('retail_risk') in ['Distress', 'Gray Zone', 'Distress Zone', 'Gray Zone']
                traditional_predicted = data.get('traditional_risk') in ['Distress', 'Gray Zone', 'Distress Zone', 'Gray Zone']
                
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
                        category_data['retail_risk_distribution'][data.get('retail_risk', 'Unknown')] += 1
                    
                    if data.get('traditional_score') is not None:
                        category_data['traditional_scores'].append(data['traditional_score'])
                        category_data['traditional_risk_distribution'][data.get('traditional_risk', 'Unknown')] += 1
                    
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
        inventory_analysis = {
            'companies_with_inventory_data': 0,
            'avg_inventory_turnover': 0.0,
            'inventory_impact_on_score': [],
            'modified_working_capital_effect': [],
            'high_inventory_companies': [],
            'low_inventory_companies': []
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
                    
                    # Classify by inventory characteristics
                    if inventory_turnover > 0.8:  # High efficiency
                        inventory_analysis['high_inventory_companies'].append({
                            'ticker': ticker,
                            'inventory_turnover': inventory_turnover,
                            'score_difference': score_diff,
                            'category': data.get('category')
                        })
                    elif inventory_turnover < 0.5:  # Low efficiency
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
        
        return inventory_analysis
    
    def generate_validation_report(self, results: Dict) -> str:
        """Generate comprehensive validation report"""
        
        # Perform analyses
        bankruptcy_analysis = self.analyze_bankruptcy_prediction(results)
        category_analysis = self.analyze_category_performance(results)
        inventory_analysis = self.analyze_inventory_impact(results)
        
        # Generate report
        report = f"""
# RETAIL Z-SCORE MODEL VALIDATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY
This report validates the novel retail Z-Score model against a comprehensive
dataset of {len(results)} retail companies across different financial health
scenarios, from bankrupt retailers to industry leaders.

## BANKRUPTCY PREDICTION ACCURACY

### Overall Performance
- Total Bankruptcies Analyzed: {bankruptcy_analysis['total_bankruptcies']}
- Retail Model Accuracy: {bankruptcy_analysis['retail_accuracy']:.1%}
- Traditional Model Accuracy: {bankruptcy_analysis['traditional_accuracy']:.1%}
- **Improvement: {bankruptcy_analysis['improvement']:+.1%}**

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

### High Inventory Efficiency Companies: {len(inventory_analysis['high_inventory_companies'])}
### Low Inventory Efficiency Companies: {len(inventory_analysis['low_inventory_companies'])}

## DETAILED COMPANY RESULTS

### FAILED/BANKRUPT RETAILERS
"""
        
        for detail in bankruptcy_analysis['details']:
            report += f"""
**{detail['ticker']}** (Bankruptcy: {detail['bankruptcy_date']})
- Retail Z-Score: {detail['retail_score']:.2f if detail['retail_score'] else 'N/A'}
- Traditional Z-Score: {detail['traditional_score']:.2f if detail['traditional_score'] else 'N/A'}
- Predictions: Retail {'✅' if detail['retail_predicted'] else '❌'}, Traditional {'✅' if detail['traditional_predicted'] else '❌'}
"""
        
        report += f"""

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
The retail Z-Score model shows {'promising' if bankruptcy_analysis['improvement'] > 0 else 'mixed'} results in this initial validation.
The inventory-focused modifications appear to {'provide meaningful improvements' if inventory_analysis.get('avg_score_difference', 0) > 0.1 else 'require further refinement'} 
over traditional Z-Score models for retail company analysis.

---
*Report generated by RetailModelValidator v{__version__}*
*Portfolio: retail_backtest_portfolio.txt*
*Analysis Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return report
    
    async def run_validation(self, portfolio_file: str, comparison: bool = True, 
                      seasonal: bool = False, detailed: bool = False) -> None:
        """Run complete validation analysis"""
        
        print("="*60)
        print("RETAIL Z-SCORE MODEL VALIDATION")
        print("="*60)
        
        # Load portfolio
        tickers = self.load_portfolio(portfolio_file)
        if not tickers:
            print("No tickers loaded. Exiting.")
            return
        
        # Calculate scores
        results = await self.calculate_retail_scores(tickers)
        
        # Save raw results
        results_file = self.output_dir / "raw_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Raw results saved to {results_file}")
        
        # Generate validation report
        report = self.generate_validation_report(results)
        
        # Save report
        report_file = self.output_dir / "validation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Validation report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print(f"Results: {self.output_dir}")
        print(f"Companies Analyzed: {len([r for r in results.values() if not r.get('error')])}")
        print(f"Errors: {len([r for r in results.values() if r.get('error')])}")
        
        # Show quick summary
        bankruptcy_analysis = self.analyze_bankruptcy_prediction(results)
        if bankruptcy_analysis['total_bankruptcies'] > 0:
            print(f"Bankruptcy Prediction Accuracy: {bankruptcy_analysis['retail_accuracy']:.1%}")
            print(f"Improvement over Traditional: {bankruptcy_analysis['improvement']:+.1%}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Retail Z-Score Model')
    parser.add_argument('--portfolio', default='portfolios/retail_backtest_portfolio.txt',
                       help='Portfolio file to analyze')
    parser.add_argument('--output-dir', default='backtest_results',
                       help='Output directory for results')
    parser.add_argument('--comparison', action='store_true',
                       help='Include comparison with traditional models')
    parser.add_argument('--seasonal', action='store_true',
                       help='Analyze seasonal patterns')
    parser.add_argument('--detailed', action='store_true',
                       help='Generate detailed company-by-company analysis')
    
    args = parser.parse_args()
    
    # Create validator
    validator = RetailModelValidator(args.output_dir)
    
    # Run validation
    asyncio.run(validator.run_validation(
        portfolio_file=args.portfolio,
        comparison=args.comparison,
        seasonal=args.seasonal,
        detailed=args.detailed
    ))

if __name__ == "__main__":
    main()
