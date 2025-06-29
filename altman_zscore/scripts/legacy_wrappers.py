#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Legacy Wrapper Scripts for Portfolio Generation

This module provides simple wrapper scripts that maintain backward compatibility
with the original generate_*_picks.py files while using the new modular system.

These scripts can be used as drop-in replacements for:
- generate_strong_buys.py
- generate_value_picks.py
- generate_growth_picks.py
- generate_dividend_picks.py
- generate_conservative_picks.py
- generate_aggressive_picks.py
- generate_sell_picks.py
- generate_strong_sell_picks.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from altman_zscore.scripts.generate_portfolio import PortfolioGeneratorScript


def create_legacy_wrapper(portfolio_type: str):
    """Create a legacy wrapper function for a specific portfolio type."""
    def wrapper():
        """Generate portfolio using the unified system."""
        print(f"=== {portfolio_type.upper()} Portfolio Generator ===")
        print("Using modular portfolio generation system...")
        
        # Create generator and run
        generator = PortfolioGeneratorScript()
        success = generator.generate_portfolio(portfolio_type)
        
        if success:
            print(f"✅ {portfolio_type.title()} portfolio generated successfully!")
        else:
            print(f"❌ Failed to generate {portfolio_type} portfolio.")
            
        return success
    
    return wrapper


# Create wrapper functions for each portfolio type
generate_strong_buys = create_legacy_wrapper('strong_buy')
generate_value_picks = create_legacy_wrapper('value')
generate_growth_picks = create_legacy_wrapper('growth')
generate_dividend_picks = create_legacy_wrapper('dividend')
generate_conservative_picks = create_legacy_wrapper('conservative')
generate_aggressive_picks = create_legacy_wrapper('aggressive')
generate_sell_picks = create_legacy_wrapper('sell')
generate_strong_sell_picks = create_legacy_wrapper('strong_sell')


def main():
    """Main entry point when script is run directly."""
    script_name = Path(sys.argv[0]).stem
    
    # Map script names to portfolio types
    name_mapping = {
        'generate_strong_buys': 'strong_buy',
        'generate_strong_buys_modular': 'strong_buy',
        'generate_value_picks': 'value',
        'generate_growth_picks': 'growth',
        'generate_dividend_picks': 'dividend',
        'generate_conservative_picks': 'conservative',
        'generate_aggressive_picks': 'aggressive',
        'generate_sell_picks': 'sell',
        'generate_strong_sell_picks': 'strong_sell'
    }
    
    portfolio_type = name_mapping.get(script_name)
    
    if portfolio_type:
        wrapper_func = create_legacy_wrapper(portfolio_type)
        success = wrapper_func()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown script name: {script_name}")
        print(f"Available types: {list(name_mapping.values())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
