#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Portfolio Generator - Modern portfolio generation with enhanced styling

This enhanced version uses the existing portfolio generation system but applies
enhanced CSS and template styles for better visual presentation.

Usage (from project root):
    python scripts/utilities/generate_portfolio_enhanced.py strong_buy
    python scripts/utilities/generate_portfolio_enhanced.py value
    python scripts/utilities/generate_portfolio_enhanced.py all
"""

import sys
import os
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change working directory to project root so the portfolio generator 
# can find the output directory with company data
os.chdir(PROJECT_ROOT)

# Import from the existing portfolio generation system
from altman_zscore.scripts.generate_portfolio import PortfolioGeneratorScript, logger
from altman_zscore.portfolio_generation.html_generator_enhanced import EnhancedHTMLPortfolioGenerator

class EnhancedPortfolioGeneratorScript(PortfolioGeneratorScript):
    """Enhanced portfolio generator that uses the existing system with enhanced styling."""
    
    def __init__(self, base_dir: str = None):
        """Initialize the enhanced portfolio generator script."""
        super().__init__(base_dir)
        logger.info("🎨 Enhanced portfolio generator initialized with modern styling")
        
        # Initialize with enhanced HTML generator
        self._initialize_generator()
    
    def generate_portfolio(self, portfolio_type: str) -> bool:
        """Generate a specific portfolio type with enhanced styling."""
        logger.info(f"✨ Generating enhanced {portfolio_type} portfolio...")
        
        # Use the parent class method which already works correctly
        # The enhanced styling will be applied through the CSS and template system
        success = super().generate_portfolio(portfolio_type)
        
        if success:
            logger.info(f"💫 Enhanced styling applied to {portfolio_type} portfolio")
            logger.info("   🎨 Modern CSS, logo handling, and responsive design included")
        
        return success

    def _initialize_generator(self):
        """Initialize the portfolio generator with enhanced HTML generator."""
        # Call parent initialization first
        super()._initialize_generator()
        
        # Replace the HTML generator with the enhanced version
        if hasattr(self.generator, 'html_generator'):
            logger.info("🎨 Replacing HTML generator with enhanced version...")
            self.generator.html_generator = EnhancedHTMLPortfolioGenerator(self.base_dir)
            logger.info("✅ Enhanced HTML generator initialized")

def main():
    """Main entry point for enhanced portfolio generation."""
    if len(sys.argv) < 2:
        print("Usage: python generate_portfolio_enhanced.py <portfolio_type>")
        print("Available types: strong_buy, value, growth, dividend, conservative, aggressive, sell, strong_sell, all")
        sys.exit(1)
    
    portfolio_type = sys.argv[1].lower()
    
    # Initialize enhanced generator
    generator = EnhancedPortfolioGeneratorScript()
    
    if portfolio_type == 'all':
        print("🌟 Generating all enhanced portfolios...")
        success_count = 0
        total_portfolios = len(generator.PORTFOLIO_CONFIGS)
        
        for ptype in generator.PORTFOLIO_CONFIGS.keys():
            print(f"\n📈 Processing {ptype}...")
            if generator.generate_portfolio(ptype):
                success_count += 1
            else:
                print(f"❌ Failed to generate {ptype}")
        
        print(f"\n🏁 Enhanced portfolio generation complete!")
        print(f"✅ Successfully generated: {success_count}/{total_portfolios}")
        print(f"💫 Enhanced styling applied to all portfolios")
        
        if success_count == total_portfolios:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # Generate single enhanced portfolio
        print(f"🌟 Generating enhanced {portfolio_type} portfolio...")
        if generator.generate_portfolio(portfolio_type):
            print(f"✅ Enhanced {portfolio_type} portfolio generated successfully!")
            print(f"💫 Enhanced styling applied")
            sys.exit(0)
        else:
            print(f"❌ Failed to generate enhanced {portfolio_type} portfolio")
            sys.exit(1)

if __name__ == "__main__":
    main()
