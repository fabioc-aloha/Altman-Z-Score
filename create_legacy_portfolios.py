"""
Create Legacy Portfolio Files
Creates individual portfolio files from the consolidated portfolio for backward compatibility
"""

from portfolio_section_extractor import PortfolioSectionExtractor
import os


def create_all_legacy_portfolios():
    """Create all legacy portfolio files from the consolidated portfolio."""
    extractor = PortfolioSectionExtractor()
    
    # Mapping of model names to legacy filenames
    legacy_files = {
        'original_zscore': 'portfolios/altman_original_portfolio.txt',
        'zprime_zscore': 'portfolios/altman_zprime_portfolio.txt',
        'zdoubleprime_zscore': 'portfolios/altman_zdoubleprime_portfolio.txt',
        'financial_institutions': 'portfolios/financial_institutions_portfolio.txt',
        'regulated_utilities': 'portfolios/regulated_utilities_portfolio.txt',
        'technology_growth': 'portfolios/technology_growth_portfolio.txt',
        'retail_consumer': 'portfolios/retail_consumer_portfolio.txt'
    }
    
    print("Creating legacy portfolio files from consolidated portfolio...")
    print("=" * 60)
    
    total_companies = 0
    for model_name, filename in legacy_files.items():
        try:
            extractor.create_legacy_portfolio_file(model_name, filename)
            tickers = extractor.get_model_tickers(model_name)
            total_companies += len(tickers)
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    print("=" * 60)
    print(f"Legacy portfolio creation complete!")
    print(f"Total companies across all portfolios: {total_companies}")
    print()
    print("Note: These files are created for backward compatibility.")
    print("The recommended approach is to use the consolidated portfolio:")
    print("  portfolios/comprehensive_model_portfolio.txt")


if __name__ == "__main__":
    create_all_legacy_portfolios()
