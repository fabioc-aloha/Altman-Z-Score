"""
Portfolio Section Extractor
Extracts specific model sections from the comprehensive portfolio file
"""

import os
import re
from typing import List, Dict, Optional


class PortfolioSectionExtractor:
    """Extract specific model sections from the comprehensive portfolio file."""
    
    def __init__(self, portfolio_file: str = "portfolios/comprehensive_model_portfolio.txt"):
        """Initialize with the comprehensive portfolio file path."""
        self.portfolio_file = portfolio_file
        self.sections = {}
        self._load_sections()
    
    def _load_sections(self):
        """Load and parse all sections from the comprehensive portfolio file."""
        if not os.path.exists(self.portfolio_file):
            raise FileNotFoundError(f"Portfolio file not found: {self.portfolio_file}")
        
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define section patterns
        section_patterns = {
            'original_zscore': r'MODEL 1: ORIGINAL ALTMAN Z-SCORE.*?(?=MODEL 2:|$)',
            'zprime_zscore': r'MODEL 2: ALTMAN Z\'-SCORE.*?(?=MODEL 3:|$)',
            'zdoubleprime_zscore': r'MODEL 3: ALTMAN Z\'\'-SCORE.*?(?=MODEL 4:|$)',
            'financial_institutions': r'MODEL 4: FINANCIAL INSTITUTIONS.*?(?=MODEL 5:|$)',
            'regulated_utilities': r'MODEL 5: REGULATED UTILITIES.*?(?=MODEL 6:|$)',
            'technology_growth': r'MODEL 6: TECHNOLOGY GROWTH.*?(?=MODEL 7:|$)',
            'retail_consumer': r'MODEL 7: RETAIL.*?$'
        }
        
        # Extract sections
        for model_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(0)
                self.sections[model_name] = self._extract_tickers_from_section(section_content)
    
    def _extract_tickers_from_section(self, section_content: str) -> List[str]:
        """Extract ticker symbols from a section."""
        tickers = []
        lines = section_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip comments, empty lines, headers
            if (line.startswith('#') or 
                line.startswith('=') or 
                not line or
                line.startswith('Formula:') or
                line.startswith('Models:') or
                line.startswith('Focus:') or
                line.startswith('Note:') or
                line.startswith('Key') or
                line.startswith('Limitations:') or
                line.startswith('Total') or
                line.startswith('Replaces:') or
                line.startswith('Designed') or
                line.startswith('Best For:') or
                line.startswith('Alternative') or
                'Europe' in line or
                'Asia' in line or
                'Latin America' in line or
                'Canada' in line or
                'Global' in line or
                'Middle East' in line or
                'Africa' in line or
                'International' in line):
                continue
            
            # Check if line looks like a ticker (all caps, sometimes with dots/numbers)
            if re.match(r'^[A-Z0-9\.\-]+$', line) and len(line) <= 10:
                tickers.append(line)
        
        return tickers
    
    def get_model_tickers(self, model_name: str) -> List[str]:
        """Get ticker symbols for a specific model."""
        return self.sections.get(model_name, [])
    
    def get_all_models(self) -> Dict[str, List[str]]:
        """Get all models and their ticker symbols."""
        return self.sections.copy()
    
    def create_legacy_portfolio_file(self, model_name: str, output_file: str):
        """Create a legacy-format portfolio file for a specific model."""
        tickers = self.get_model_tickers(model_name)
        
        if not tickers:
            raise ValueError(f"No tickers found for model: {model_name}")
        
        # Model metadata
        model_info = {
            'original_zscore': {
                'title': 'ALTMAN Z-SCORE MODEL PORTFOLIO',
                'subtitle': 'Original Altman Z-Score (1968) - Best for Manufacturing & Industrial Companies',
                'formula': 'Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E',
                'best_for': 'Manufacturing, Industrial, Capital-Intensive Companies',
                'limitations': 'Not suitable for service companies, financial institutions, utilities'
            },
            'zprime_zscore': {
                'title': 'ALTMAN Z\'-SCORE MODEL PORTFOLIO',
                'subtitle': 'Modified Altman Z\'-Score (1983) - Best for Private & Non-Manufacturing Companies',
                'formula': 'Z\' = 0.717A + 0.847B + 3.107C + 0.420D + 0.998E',
                'best_for': 'Private companies, Non-manufacturing, Service companies',
                'limitations': 'Replaces market value of equity with book value (ratio D)'
            },
            'zdoubleprime_zscore': {
                'title': 'ALTMAN Z\'\'-SCORE MODEL PORTFOLIO',
                'subtitle': 'Altman Z\'\'-Score (2012) - Best for Emerging Market & Non-US Companies',
                'formula': 'Z\'\' = 3.25 + 6.56A + 3.26B + 6.72C + 1.05D',
                'best_for': 'Emerging market companies, Non-US companies, Different accounting standards',
                'limitations': 'Designed for companies with different financial reporting standards'
            },
            'financial_institutions': {
                'title': 'FINANCIAL INSTITUTIONS MODEL PORTFOLIO',
                'subtitle': 'Special Models for Banks, Insurance, and Financial Services',
                'formula': 'Modified ratios for financial institutions',
                'best_for': 'Capital adequacy, Asset quality, Management quality, Earnings, Liquidity',
                'limitations': 'Traditional Z-Score not applicable - use CAMELS or similar frameworks'
            },
            'regulated_utilities': {
                'title': 'REGULATED UTILITIES MODEL PORTFOLIO',
                'subtitle': 'Special Models for Utilities and Regulated Industries',
                'formula': 'Modified financial ratios for regulated utilities',
                'best_for': 'FFO/Debt, Interest Coverage, Regulatory Environment Stability',
                'limitations': 'Traditional Z-Score less applicable due to regulated nature and stable cash flows'
            },
            'technology_growth': {
                'title': 'TECHNOLOGY GROWTH MODEL PORTFOLIO',
                'subtitle': 'Modified Models for High-Growth Technology Companies',
                'formula': 'Growth-adjusted Z-Score and Technology-specific ratios',
                'best_for': 'Revenue growth, R&D intensity, Customer acquisition costs, Recurring revenue',
                'limitations': 'Traditional Z-Score may penalize growth investments and R&D spending'
            },
            'retail_consumer': {
                'title': 'RETAIL & CONSUMER MODEL PORTFOLIO',
                'subtitle': 'Modified Models for Retail and Consumer-Focused Companies',
                'formula': 'Retail-specific financial ratios and working capital analysis',
                'best_for': 'Inventory turnover, same-store sales growth, seasonal adjustments',
                'limitations': 'Traditional Z-Score applicable but requires industry-specific context'
            }
        }
        
        info = model_info.get(model_name, {})
        
        # Create legacy format content
        content = f"""# ===============================================================================
# {info.get('title', 'MODEL PORTFOLIO')}
# {info.get('subtitle', 'Specialized Analysis Model')}
# ===============================================================================

# PORTFOLIO SUMMARY
# ===============================================================================
# Model: {info.get('title', 'Custom Model')}
# Formula: {info.get('formula', 'Specialized ratios')}
# Best For: {info.get('best_for', 'Specific industry analysis')}
# Limitations: {info.get('limitations', 'Model-specific considerations')}
# Total Stocks: {len(tickers)}
# ===============================================================================

"""
        
        # Add tickers
        for ticker in tickers:
            content += f"{ticker}\n"
        
        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created legacy portfolio file: {output_file} ({len(tickers)} tickers)")


def main():
    """Demo usage of the portfolio section extractor."""
    extractor = PortfolioSectionExtractor()
    
    print("Available models:")
    for model_name, tickers in extractor.get_all_models().items():
        print(f"  {model_name}: {len(tickers)} companies")
    
    print("\nExample tickers for 'original_zscore' model:")
    original_tickers = extractor.get_model_tickers('original_zscore')
    print(f"  {original_tickers[:10]}... ({len(original_tickers)} total)")
    
    # Create a legacy file example
    extractor.create_legacy_portfolio_file(
        'original_zscore', 
        'portfolios/temp_original.txt'
    )


if __name__ == "__main__":
    main()
