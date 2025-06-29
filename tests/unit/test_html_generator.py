#!/usr/bin/env python3
"""
Test the new modular HTML Portfolio Generator
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from altman_zscore.portfolio_generation.html_generator import HTMLPortfolioGenerator

def test_html_generator():
    """Test the HTML Portfolio Generator with sample data."""
    
    # Sample company data
    sample_companies = [
        {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'z_score': 3.45,
            'risk_category': 'Safe',
            'recommendation': 'Strong Buy'
        },
        {
            'ticker': 'MSFT', 
            'name': 'Microsoft Corporation',
            'z_score': 2.87,
            'risk_category': 'Safe',
            'recommendation': 'Buy'
        },
        {
            'ticker': 'GOOGL',
            'name': 'Alphabet Inc.',
            'z_score': 2.12,
            'risk_category': 'Moderate',
            'recommendation': 'Buy'
        }
    ]
    
    # Initialize HTML generator
    generator = HTMLPortfolioGenerator(base_dir="web")
    
    # Generate portfolio HTML
    html_path = generator.generate_portfolio_html(
        companies=sample_companies,
        portfolio_type='strong_buy',
        title='Strong Buy Portfolio - Test',
        description='Test portfolio demonstrating the new modular HTML generator',
        output_filename='test_portfolio.html'
    )
    
    if html_path:
        print(f"✅ HTML Portfolio generated successfully: {html_path}")
        
        # Check if file exists and has content
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 1000:  # Basic content check
                    print(f"✅ Generated HTML file has substantial content ({len(content)} characters)")
                    print(f"📄 Test HTML file: {os.path.abspath(html_path)}")
                    return True
                else:
                    print(f"❌ Generated HTML file is too small ({len(content)} characters)")
        else:
            print(f"❌ Generated HTML file does not exist: {html_path}")
    else:
        print("❌ Failed to generate HTML portfolio")
    
    return False

if __name__ == "__main__":
    print("Testing Modular HTML Portfolio Generator...")
    print("=" * 50)
    
    success = test_html_generator()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The modular HTML generator is working correctly.")
    else:
        print("💥 Tests failed. Check the HTML generator implementation.")
