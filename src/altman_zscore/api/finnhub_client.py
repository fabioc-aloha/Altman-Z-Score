"""
Finnhub API client for fetching financial data.
This module provides a wrapper around the Finnhub API with specific methods
for fetching company data needed for Altman Z-Score calculations.
"""

import os
from pathlib import Path
import json
import logging
import requests
from decimal import Decimal
from typing import Dict, Optional, Any, Union
import finnhub
from dotenv import load_dotenv

from .base_fetcher import BaseFinancialFetcher, FinancialValue
from ..validation.data_validation import FinancialDataValidator
from ..utils.retry import exponential_retry

# Network exceptions to retry on
FINNHUB_EXCEPTIONS = (
    requests.exceptions.RequestException,  # Base exception
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError,
    finnhub.FinnhubAPIException,  # Finnhub specific exceptions
    finnhub.FinnhubRequestException,
)


class FinnhubClient(BaseFinancialFetcher):
    """A client for interacting with the Finnhub API."""
    
    def __init__(self):
        """Initialize the Finnhub client with validator and API client."""
        super().__init__()
        
        # Initialize API client
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY not set in environment")
        self.client = finnhub.Client(api_key=api_key)
        
    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=FINNHUB_EXCEPTIONS
    )
    def fetch_financial_data(self, symbol: str) -> Dict[str, FinancialValue]:
        """
        Fetch financial data needed for Altman Z-Score calculation.
        
        Args:
            symbol: Company stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing financial metrics needed for Z-Score calculation
        
        Raises:
            Exception: If data fetching fails after retries.
        """
        try:
            # Get basic financials with retries
            financials = self.client.company_basic_financials(symbol, 'all')
            
            # Extract relevant metrics for Z-Score calculation
            metrics = {}
            
            if financials and 'metric' in financials:
                metric_data = financials['metric']
                
                # Working Capital = Current Assets - Current Liabilities
                current_assets = Decimal(str(metric_data.get('currentRatio', 0))) * Decimal(str(metric_data.get('currentLiabilities', 0)))
                current_liabilities = Decimal(str(metric_data.get('currentLiabilities', 0)))
                working_capital = current_assets - current_liabilities
                
                metrics.update({
                    'working_capital': working_capital,
                    'total_assets': Decimal(str(metric_data.get('totalAssets', 0))),
                    'retained_earnings': Decimal(str(metric_data.get('retainedEarnings', 0))),
                    'ebit': Decimal(str(metric_data.get('ebit', 0))),
                    'market_value_equity': Decimal(str(metric_data.get('marketCapitalization', 0))),
                    'total_liabilities': Decimal(str(metric_data.get('totalLiabilities', 0))),
                    'sales': Decimal(str(metric_data.get('totalRevenue', 0)))
                })
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Failed to fetch financial data for {symbol}: {str(e)}")        
    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=FINNHUB_EXCEPTIONS
    )
    def _try_direct_logo_download(self, symbol: str, size: tuple[int, int] = (1000, 1000)) -> Optional[tuple[str, bytes]]:
        """
        Try to download and resize a company logo using Finnhub's direct URL format.
        Implements exponential backoff retry for network-related errors.

        Args:
            symbol: Company stock symbol (e.g., 'AAPL')
            size: Desired resolution as (width, height) tuple. Default is (1000, 1000), which is the Finnhub direct logo API's native size.

        Returns:
            Tuple of (URL string, resized image bytes) if successful, None if failed
        """
        from PIL import Image
        from io import BytesIO
        
        direct_url = f"https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/{symbol}.png"
        logger = logging.getLogger(__name__)
        
        # Check if URL exists
        head_response = requests.head(direct_url)
        if head_response.status_code != 200:
            logger.debug(f"Logo not available at {direct_url}")
            return None
        
        # Download image
        response = requests.get(direct_url)
        if response.status_code != 200:
            logger.debug(f"Failed to download logo from {direct_url}")
            return None
        
        try:
            # Open the original image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGBA if needed (to preserve transparency)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Calculate new size maintaining aspect ratio
            orig_width, orig_height = image.size
            target_width, target_height = size
            ratio = min(target_width/orig_width, target_height/orig_height)
            new_size = (int(orig_width * ratio), int(orig_height * ratio))
            
            # Resize image using high-quality downsampling
            resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create a new RGBA image with desired size and paste resized image centered
            final_image = Image.new('RGBA', size, (0, 0, 0, 0))
            paste_x = (size[0] - new_size[0]) // 2
            paste_y = (size[1] - new_size[1]) // 2
            final_image.paste(resized_image, (paste_x, paste_y), resized_image)
            
            # Save resized image to bytes with optimization
            output = BytesIO()
            final_image.save(output, format='PNG', optimize=True)
            image_bytes = output.getvalue()
            
            return direct_url, image_bytes
        
        except (IOError, ValueError) as e:
            logger.warning(f"Error processing logo image: {str(e)}")
            return None

    @exponential_retry(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=FINNHUB_EXCEPTIONS
    )
    def get_company_profile(self, symbol: str, logo_size: tuple[int, int] = (1000, 1000), logo_path: str = None) -> Dict[str, Any]:
        """
        Fetch company profile information and download company logo.
        Implements exponential backoff retry for network-related errors.
        
        Args:
            symbol: Company stock symbol (e.g., 'AAPL')
            logo_size: Desired logo resolution as (width, height) tuple. Default is (1000, 1000), which is the Finnhub direct logo API's native size.
            logo_path: Optional. Full path (str or Path) to save the logo file. If not provided, defaults to company_logo.png in the company dir.
            
        Returns:
            Dictionary containing company profile information
        """
        logger = logging.getLogger(__name__)
        
        profile = self.client.company_profile2(symbol=symbol)
        
        # Try to get logo URL from profile or direct URL
        logo_url = profile.get('logo')
        logo_data = None
        
        if not logo_url:
            # Try direct download with resizing
            result = self._try_direct_logo_download(symbol, size=logo_size)
            if result:
                logo_url, logo_data = result
                profile['logo'] = logo_url
        
        # Save profile data and logo
        company_dir = self.get_company_dir(symbol)
        if company_dir:
            # Save profile data
            profile_path = company_dir / 'company_info.json'
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            # Download and resize logo if available
            if logo_url:
                # Determine logo save path
                if logo_path is not None:
                    logo_path_final = Path(logo_path)
                else:
                    logo_path_final = company_dir / 'company_logo.png'
                if logo_data:
                    # Save pre-resized logo from direct download
                    with open(logo_path_final, 'wb') as f:
                        f.write(logo_data)
                    logger.info(f"Resized logo downloaded successfully from: {logo_url}")
                else:
                    # Download and resize from profile URL
                    try:
                        response = requests.get(logo_url)
                        if response.status_code == 200:
                            result = self._try_direct_logo_download(symbol, size=logo_size)
                            if result:
                                _, logo_data = result
                                with open(logo_path_final, 'wb') as f:
                                    f.write(logo_data)
                                logger.info("Logo downloaded and resized successfully from profile URL")
                            else:
                                logger.warning("Failed to resize logo from profile URL")
                        else:
                            logger.warning(f"Failed to download logo from profile URL. Status code: {response.status_code}")
                    except Exception as e:
                        logger.warning(f"Error processing logo from profile URL: {str(e)}")
    
        return profile
            
    def get_company_dir(self, symbol: str) -> Optional[Path]:
        """Get the company directory for saving data."""
        output_dir = Path('output')
        if output_dir.exists():
            company_dir = output_dir / symbol
            company_dir.mkdir(parents=True, exist_ok=True)
            return company_dir
        return None
