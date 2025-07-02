#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify enhanced logo handling in company cards
"""

import os
import sys
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from altman_zscore.portfolio_generation.html_generator_enhanced import EnhancedHTMLPortfolioGenerator

def test_logo_handling():
    """Test the enhanced logo handling functionality."""
    print("🧪 Testing Enhanced Logo Handling...")
    
    # Initialize the enhanced generator
    generator = EnhancedHTMLPortfolioGenerator(".")
    
    # Test with various company scenarios
    test_companies = [
        {"ticker": "AAPL", "name": "Apple Inc."},
        {"ticker": "MSFT", "name": "Microsoft Corporation"},
        {"ticker": "GOOGL", "name": "Alphabet Inc."},
        {"ticker": "TSLA", "name": "Tesla, Inc."},
        {"ticker": "NVDA", "name": "NVIDIA Corporation"},
        {"ticker": "AMZN", "name": "Amazon.com, Inc."},
    ]
    
    print("📋 Testing logo generation for sample companies:")
    for company in test_companies:
        ticker = company["ticker"]
        name = company["name"]
        
        # Generate logo HTML
        logo_html = generator._generate_enhanced_logo_html(ticker, name)
        
        # Generate initials
        initials = generator._get_company_initials(name)
        
        print(f"  • {name} ({ticker})")
        print(f"    Initials: {initials}")
        print(f"    Logo HTML: {logo_html[:80]}...")
        print()
    
    print("✅ Logo handling test completed!")
    print("💡 The enhanced system will:")
    print("   - Check multiple logo path variations")
    print("   - Provide fallback to default logo with error handling")
    print("   - Generate company initials for additional fallback")
    print("   - Apply modern styling with hover effects")

if __name__ == "__main__":
    test_logo_handling()
