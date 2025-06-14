import os
import sys
from pathlib import Path
import pprint

# Add the project root and src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from altman_zscore.api.finnhub_client import FinnhubClient
    from PIL import Image
except ImportError as e:
    print(f"Import error: {e}")
    print("sys.path:", sys.path)

def _test_company(client, symbol: str, size=(200, 200)):
    """Test logo download and profile fetch for a company (helper, not a pytest test)."""
    print(f"\nTesting {symbol} with size {size}:")
    try:
        profile = client.get_company_profile(symbol)
        print("\nCompany Profile Data:")
        pprint.pprint(profile, width=100, sort_dicts=False)
        
        # Verify logo size if downloaded
        logo_path = Path(f'output/{symbol}/company_logo.png')
        if logo_path.exists():
            with Image.open(logo_path) as img:
                print(f"\nActual logo dimensions: {img.size}")
                
    except Exception as e:
        print(f"Error fetching profile: {e}")

def test_finnhub_company_profile():
    from altman_zscore.api.finnhub_client import FinnhubClient
    client = FinnhubClient()
    symbol = "MSFT"
    profile = client.get_company_profile(symbol)
    assert isinstance(profile, dict)
    assert "name" in profile or "Name" in profile or len(profile) > 0

def main():
    try:
        client = FinnhubClient()
        
        # Test with different companies and resolutions
        _test_company(client, 'AAPL', (200, 200))  # Square resolution
        _test_company(client, 'MSFT', (300, 200))  # Rectangular resolution
        _test_company(client, 'GOOGL', (150, 150))  # Smaller resolution
            
    except Exception as e:
        print(f"Error initializing client: {e}")

if __name__ == "__main__":
    main()
