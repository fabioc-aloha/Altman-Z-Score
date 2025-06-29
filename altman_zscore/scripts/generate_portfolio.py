#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified Portfolio Generator Script

This module replaces all the individual generate_*_picks.py scripts with a single,
modular solution that uses the portfolio generation system in altman_zscore/.

Usage:
    python -m altman_zscore.scripts.generate_portfolio strong_buy
    python -m altman_zscore.scripts.generate_portfolio value
    python -m altman_zscore.scripts.generate_portfolio growth
    python -m altman_zscore.scripts.generate_portfolio dividend
    python -m altman_zscore.scripts.generate_portfolio conservative
    python -m altman_zscore.scripts.generate_portfolio aggressive
    python -m altman_zscore.scripts.generate_portfolio sell
    python -m altman_zscore.scripts.generate_portfolio strong_sell
    
Or generate all:
    python -m altman_zscore.scripts.generate_portfolio all
"""

import argparse
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from altman_zscore.portfolio_generation import (
    PortfolioGenerator, PortfolioConfig,
    StrongBuyStrategy, BuyStrategy, SellStrategy, StrongSellStrategy,
    ValueStrategy, GrowthStrategy, DividendStrategy,
    ConservativeStrategy, AggressiveStrategy,
    HTMLPortfolioGenerator, CompanyDataExtractor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class PortfolioGeneratorScript:
    """Unified portfolio generator script replacing individual generate_*_picks.py files."""
    
    # Portfolio type configurations
    PORTFOLIO_CONFIGS = {
        'strong_buy': {
            'strategy_class': StrongBuyStrategy,
            'title': 'Strong Buy Portfolio',
            'description': 'High-conviction investment opportunities with strong fundamentals',
            'filename': 'strong_buys.html',
            'min_z_score': 1.5,
            'max_companies': 25,
            'color_scheme': 'strong_buy'
        },
        'value': {
            'strategy_class': ValueStrategy,
            'title': 'Value Investor Dashboard',
            'description': 'Undervalued stocks with strong fundamentals for long-term value creation',
            'filename': 'value_picks.html',
            'min_z_score': 2.6,
            'max_companies': 20,
            'color_scheme': 'value'
        },
        'growth': {
            'strategy_class': GrowthStrategy,
            'title': 'Growth Investor Portfolio',
            'description': 'High-growth companies with solid financial foundations',
            'filename': 'growth_picks.html',
            'min_z_score': 2.0,
            'max_companies': 20,
            'color_scheme': 'growth'
        },
        'dividend': {
            'strategy_class': DividendStrategy,
            'title': 'Dividend Income Portfolio',
            'description': 'Reliable dividend-paying companies for income-focused investors',
            'filename': 'dividend_picks.html',
            'min_z_score': 2.3,
            'max_companies': 20,
            'color_scheme': 'dividend'
        },
        'conservative': {
            'strategy_class': ConservativeStrategy,
            'title': 'Conservative Investor Portfolio',
            'description': 'Low-risk, stable companies for capital preservation',
            'filename': 'conservative_picks.html',
            'min_z_score': 2.8,
            'max_companies': 15,
            'color_scheme': 'conservative'
        },
        'aggressive': {
            'strategy_class': AggressiveStrategy,
            'title': 'Aggressive Growth Portfolio',
            'description': 'High-risk, high-reward opportunities for aggressive investors',
            'filename': 'aggressive_picks.html',
            'min_z_score': 1.2,
            'max_companies': 25,
            'color_scheme': 'aggressive'
        },
        'sell': {
            'strategy_class': SellStrategy,
            'title': 'Sell Recommendations',
            'description': 'Companies showing warning signs requiring careful consideration',
            'filename': 'sell_picks.html',
            'min_z_score': 0.0,
            'max_companies': 20,
            'color_scheme': 'sell'
        },
        'strong_sell': {
            'strategy_class': StrongSellStrategy,
            'title': 'Strong Sell Portfolio',
            'description': 'Companies exhibiting severe financial distress indicators',
            'filename': 'strong_sell_picks.html',
            'min_z_score': 0.0,
            'max_companies': 20,
            'color_scheme': 'strong_sell'
        }
    }
    
    def __init__(self, base_dir: str = None):
        """Initialize the portfolio generator script."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.output_dir = self.base_dir / "output"
        self.web_dir = self.base_dir / "web"
        
        # Ensure output directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.web_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized portfolio generator in {self.base_dir}")
        logger.info(f"HTML files will be generated in {self.web_dir}")
    
    def generate_portfolio(self, portfolio_type: str) -> bool:
        """Generate a specific portfolio type."""
        if portfolio_type not in self.PORTFOLIO_CONFIGS:
            logger.error(f"Unknown portfolio type: {portfolio_type}")
            logger.info(f"Available types: {list(self.PORTFOLIO_CONFIGS.keys())}")
            return False
        
        config_data = self.PORTFOLIO_CONFIGS[portfolio_type]
        logger.info(f"Generating {portfolio_type} portfolio...")
        
        try:
            # Create portfolio configuration
            config = PortfolioConfig(
                name=portfolio_type,
                title=config_data['title'],
                description=config_data['description'],
                output_filename=config_data['filename'],
                max_companies=config_data['max_companies'],
                min_companies=min(5, config_data['max_companies'] // 2)
            )
            
            # Create strategy instance
            strategy = config_data['strategy_class'](config)
            
            # Create portfolio generator
            generator = PortfolioGenerator(str(self.base_dir))
            
            # Generate portfolio using the modular system
            output_path = generator.generate_portfolio(strategy)
            
            logger.info(f"✅ Successfully generated {portfolio_type} portfolio: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating {portfolio_type} portfolio: {str(e)}")
            return False
    
    def generate_all_portfolios(self) -> Dict[str, bool]:
        """Generate all portfolio types."""
        logger.info("🚀 Generating all portfolio types...")
        
        results = {}
        for portfolio_type in self.PORTFOLIO_CONFIGS:
            results[portfolio_type] = self.generate_portfolio(portfolio_type)
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"📊 Portfolio generation complete: {successful}/{total} successful")
        
        if successful < total:
            logger.warning("❌ Some portfolios failed to generate:")
            for portfolio_type, success in results.items():
                if not success:
                    logger.warning(f"  - {portfolio_type}")
        
        return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate investment portfolios using modular strategy system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s strong_buy          Generate strong buy portfolio
  %(prog)s value              Generate value investor portfolio  
  %(prog)s all                Generate all portfolio types
        """
    )
    
    parser.add_argument(
        'portfolio_type',
        choices=list(PortfolioGeneratorScript.PORTFOLIO_CONFIGS.keys()) + ['all'],
        help='Type of portfolio to generate'
    )
    
    parser.add_argument(
        '--base-dir',
        type=str,
        default=None,
        help='Base directory (defaults to current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create generator
    generator = PortfolioGeneratorScript(args.base_dir)
    
    # Generate portfolio(s)
    if args.portfolio_type == 'all':
        results = generator.generate_all_portfolios()
        success = all(results.values())
    else:
        success = generator.generate_portfolio(args.portfolio_type)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
