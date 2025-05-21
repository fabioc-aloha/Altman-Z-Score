"""Simple script to validate a single CIK."""
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

from src.altman_zscore.cik_lookup import lookup_cik

def validate_single_cik(ticker: str, expected_cik: str) -> None:
    """Validate a single CIK."""
    try:
        looked_up_cik = lookup_cik(ticker)
        print(f"\nResults for {ticker}:")
        print(f"Expected CIK: {expected_cik}")
        print(f"Looked up CIK: {looked_up_cik}")
        if looked_up_cik == expected_cik:
            print("✅ Match!")
        else:
            print("❌ Mismatch!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Configure logging to show debug output
    logging.basicConfig(level=logging.DEBUG)
    
    test_cases = [
        ("IBM", "0000051143"),    # IBM
        ("ORCL", "0001341439"),   # Oracle
        ("CRM", "0001108524"),    # Salesforce
        ("ADBE", "0000796343"),   # Adobe
        ("SNOW", "0001640147"),   # Snowflake
        ("PLTR", "0001321655"),   # Palantir
        ("AI", "0001577526"),     # C3.ai
        ("DDOG", "0001561550"),   # Datadog
        ("PATH", "0001734722"),   # UiPath
        ("NOW", "0001373715"),    # ServiceNow
        ("CRWD", "0001535527"),   # CrowdStrike
        ("INTU", "0000896878"),   # Intuit
        ("UPST", "0001647639")    # Upstart
    ]
    
    for ticker, expected_cik in test_cases:
        validate_single_cik(ticker, expected_cik)
