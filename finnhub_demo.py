import os
from dotenv import load_dotenv
import finnhub

# Load environment variables from .env if present
load_dotenv()

# Get API key from environment
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise RuntimeError("FINNHUB_API_KEY not set in environment. Please add it to your .env file.")

# Setup client - using the package's recommended initialization
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# --- FREE ENDPOINTS ONLY BELOW ---

def try_call(label, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        result_str = str(result)
        if len(result_str) > 200:
            result_str = result_str[:200] + '... [truncated]'
        print(f"\n--- {label} ---\n{result_str}")
    except Exception as e:
        print(f"\n--- {label} FAILED ---\n{e}")


# Fetch and pretty print company profile and download logo for AAPL
import json
import requests
from pathlib import Path
import pprint

try:
    # Get profile data
    profile = finnhub_client.company_profile2(symbol='AAPL')
    
    # Pretty print the full profile data
    print("\n--- Company Profile (AAPL) ---")
    pprint.pprint(profile, width=100, sort_dicts=False)
    
    # Download logo if available
    logo_url = profile.get('logo')
    if logo_url:
        # Create output directory if it doesn't exist
        output_dir = Path('output/AAPL')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Download and save the logo
        logo_path = output_dir / 'company_logo.png'
        response = requests.get(logo_url)
        if response.status_code == 200:
            with open(logo_path, 'wb') as f:
                f.write(response.content)
            print(f"\nLogo downloaded successfully to: {logo_path}")
        else:
            print(f"\nFailed to download logo. Status code: {response.status_code}")
            
        print(f"\nLogo URL: {logo_url}")
    else:
        print("\nNo logo URL found in profile response.")
except Exception as e:
    print(f"\n--- Company Profile/Logo Download FAILED ---\n{e}")

