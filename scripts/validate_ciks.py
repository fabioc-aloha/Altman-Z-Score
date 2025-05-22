"""Script to validate CIKs in portfolio configuration."""
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configure logging - only show warnings and above
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

# Now import the modules
from src.altman_zscore.cik_lookup import lookup_cik
from portfolio import PORTFOLIO  # Updated import

def main():
    """Validate all CIKs in portfolio."""
    results = {
        "failed": []
    }
    
    total = len(PORTFOLIO)
    valid = 0
    
    for ticker in PORTFOLIO:
        try:
            looked_up_cik = lookup_cik(ticker)
            if looked_up_cik is None:
                results["failed"].append((ticker, "CIK not found"))
            else:
                valid += 1
        except Exception as e:
            logger.error(f"Error validating {ticker}: {e}")
            results["failed"].append((ticker, str(e)))
    
    # Only print results if there are issues
    if results["failed"]:
        print("\n⚠️ CIK Validation Issues:\n")
        for ticker, error in results["failed"]:
            print(f"  {ticker}: {error}")
    
    # Print summary
    print(f"\nSummary: {valid}/{total} companies have valid CIKs")
    if valid == total:
        print("✅ All CIKs are valid")
    
if __name__ == "__main__":
    main()
