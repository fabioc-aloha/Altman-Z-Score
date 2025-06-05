"""Test script for Finnhub client logo download functionality."""

import sys
from pathlib import Path
import pprint
from typing import Tuple

# Add the project root and src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.altman_zscore.api import FinnhubClient
    from PIL import Image
except ImportError as e:
    print(f"Import error: {e}")
    print("sys.path:", sys.path)
    sys.exit(1)

def test_company_with_size(client: FinnhubClient, symbol: str, size: Tuple[int, int]) -> None:
    """Test logo download and profile fetch for a company with specific size."""
    print(f"\nTesting {symbol} with size {size}:")
    try:
        profile = client.get_company_profile(symbol, logo_size=size)
        print("\nCompany Profile Data:")
        pprint.pprint(profile, width=100, sort_dicts=False)
        
        # Verify logo size if downloaded
        logo_path = Path(f'output/{symbol}/company_logo.png')
        if logo_path.exists():
            with Image.open(logo_path) as img:
                print(f"\nActual logo dimensions: {img.size}")
                if img.size != size:
                    print(f"Warning: Logo dimensions {img.size} don't match requested size {size}")
                else:
                    print("Logo dimensions match requested size")
        else:
            print("No logo file found")
                
    except Exception as e:
        print(f"Error fetching profile: {e}")

def main():
    """Main test function."""
    client = FinnhubClient()
    
    # Test different companies with various sizes
    test_sizes = [
        (100, 100),   # Small square
        (200, 200),   # Default size
        (300, 150),   # Wide rectangle
        (150, 300),   # Tall rectangle
        (500, 500),   # Large square
    ]
    
    companies = ['AAPL', 'MSFT', 'GOOGL', 'SAP']
    
    for company in companies:
        for size in test_sizes:
            test_company_with_size(client, company, size)
        print("\n" + "="*80)

if __name__ == "__main__":
    main()
