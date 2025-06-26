"""
Finnhub Data Fetcher - Company profiles and logo fetching

This module provides access to Finnhub API for company profile enrichment
and logo URL fetching with intelligent caching.

Key Features:
- Company profile data fetching
- Direct logo URL access with validation
- 48-hour caching for all data
- Rate limiting integration
- Graceful fallbacks for missing data
"""

import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import time
import shutil
import hashlib

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ...common.cache import UnifiedCache, CacheBackend
from ...common.api_rate_limiter import rate_limiter

logger = get_logger(__name__)

# Cache TTL for Finnhub data (48 hours)
CACHE_TTL_SECONDS = 48 * 60 * 60


class FinnhubDataFetcher:
    """Fetcher for Finnhub API data with caching and rate limiting."""
    
    def __init__(self):
        """Initialize Finnhub data fetcher with API configuration."""
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
        self.logo_base_url = "https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo"
        
        # Initialize cache
        self.cache = UnifiedCache(
            backend=CacheBackend.FILE,
            cache_dir=".cache/finnhub",
            ttl_seconds=CACHE_TTL_SECONDS
        )
        
        # Initialize logo cache directory
        self.logo_cache_dir = Path(".cache/finnhub/logos")
        self.logo_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Log initialization
        if self.api_key:
            logger.info("Initialized Finnhub data fetcher with API key")
        else:
            logger.info("Initialized Finnhub data fetcher without API key (logo fetching only)")
            
        logger.info(f"Logo cache directory: {self.logo_cache_dir}")

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Finnhub API with rate limiting.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            
        Returns:
            Dict: API response data
            
        Raises:
            DataFetchError: If request fails
        """
        if not self.api_key:
            raise DataFetchError("FINNHUB_API_KEY environment variable not set")
        
        # Apply rate limiting
        rate_limiter.wait_for_rate_limit("finnhub.io")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'X-Finnhub-Token': self.api_key,
            'User-Agent': 'AltmanZScore/3.16.0'
        }
        
        if params is None:
            params = {}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                rate_limiter.record_request("finnhub.io")
                return response.json()
            elif response.status_code == 429:
                logger.warning(f"Finnhub rate limit exceeded for {endpoint}")
                rate_limiter.record_failed_request("finnhub.io", 429)
                raise DataFetchError(f"Finnhub rate limit exceeded: {response.status_code}")
            elif response.status_code == 401:
                logger.error("Finnhub API authentication failed - check FINNHUB_API_KEY")
                raise DataFetchError(f"Finnhub authentication failed: {response.status_code}")
            else:
                logger.warning(f"Finnhub API error {response.status_code} for {endpoint}")
                rate_limiter.record_failed_request("finnhub.io", response.status_code)
                raise DataFetchError(f"Finnhub API error: {response.status_code}")
                
        except requests.RequestException as e:
            rate_limiter.record_failed_request("finnhub.io", 0)
            logger.error(f"Network error calling Finnhub API {endpoint}: {e}")
            raise DataFetchError(f"Network error: {str(e)}")
    
    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company profile from Finnhub API with caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict containing company profile data or None if not available
        """
        cache_key = f"finnhub_profile:{symbol.upper()}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached Finnhub profile for {symbol}")
            return cached_result
        
        try:
            # Fetch from API
            profile_data = self._make_request("stock/profile2", {"symbol": symbol.upper()})
            
            # Validate response has required data
            if not profile_data or not profile_data.get('name'):
                logger.warning(f"No company profile data available for {symbol}")
                # Cache empty result to avoid repeated API calls
                self.cache.set(cache_key, None, ttl=CACHE_TTL_SECONDS)
                return None
            
            # Cache result
            self.cache.set(cache_key, profile_data, ttl=CACHE_TTL_SECONDS)
            logger.debug(f"Fetched and cached Finnhub profile for {symbol}")
            
            return profile_data
            
        except DataFetchError as e:
            logger.warning(f"Failed to fetch Finnhub profile for {symbol}: {e}")
            # Cache empty result to avoid repeated failures
            self.cache.set(cache_key, None, ttl=CACHE_TTL_SECONDS // 4)  # Shorter TTL for failures
            return None
    
    def get_company_logo_url(self, symbol: str) -> Optional[str]:
        """
        Get company logo URL from Finnhub with validation and caching.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            String URL of company logo or None if not available
        """
        cache_key = f"finnhub_logo:{symbol.upper()}"
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached logo URL for {symbol}")
            return cached_result
        
        # Try to get logo URL from company profile first
        profile = self.get_company_profile(symbol)
        logo_url = None
        
        if profile and profile.get('logo'):
            logo_url = profile['logo']
            logger.debug(f"Got logo URL from profile for {symbol}: {logo_url}")
        else:
            # Fallback to direct logo URL construction
            logo_url = f"{self.logo_base_url}/{symbol.upper()}.png"
            logger.debug(f"Using direct logo URL for {symbol}: {logo_url}")
        
        # Validate the logo URL exists
        if logo_url and self._validate_logo_url(logo_url):
            # Cache successful result
            self.cache.set(cache_key, logo_url, ttl=CACHE_TTL_SECONDS)
            logger.info(f"Valid logo URL found for {symbol}: {logo_url}")
            return logo_url
        else:
            # Cache failure to avoid repeated checks
            self.cache.set(cache_key, None, ttl=CACHE_TTL_SECONDS // 2)
            logger.warning(f"No valid logo URL found for {symbol}")
            return None
    
    def _validate_logo_url(self, logo_url: str) -> bool:
        """
        Validate that a logo URL returns a valid image.
        
        Args:
            logo_url: URL to validate
            
        Returns:
            Bool: True if URL returns valid image, False otherwise
        """
        try:
            # Make HEAD request to check if URL exists
            response = requests.head(logo_url, timeout=10)
            
            # Check if response is successful and content type is image
            if response.status_code == 200:
                rate_limiter.record_request("finnhub.io")
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type:
                    return True
                else:
                    logger.debug(f"Logo URL returned non-image content: {content_type}")
            else:
                logger.debug(f"Logo URL validation failed with status {response.status_code}")
                rate_limiter.record_failed_request("finnhub.io", response.status_code)
            
            return False
            
        except requests.RequestException as e:
            logger.debug(f"Logo URL validation failed with network error: {e}")
            rate_limiter.record_failed_request("finnhub.io", 0)
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dict with cache statistics
        """
        stats = self.cache.get_stats()
        stats.update({
            'api_key_configured': bool(self.api_key),
            'backend_type': str(self.cache.backend_type.value)
        })
        return stats
    
    def download_logo(self, symbol: str, force: bool = False) -> Optional[str]:
        """
        Download and cache the company logo image.
        
        Args:
            symbol: Stock ticker symbol
            force: If True, force re-download even if cached version exists
            
        Returns:
            String file path of the downloaded logo image or None if failed
        """
        logo_url = self.get_company_logo_url(symbol)
        if not logo_url:
            logger.warning(f"Cannot download logo, no valid URL found for {symbol}")
            return None
        
        # Generate cache file path
        logo_filename = f"{symbol.upper()}.png"
        logo_cache_path = self.logo_cache_dir / logo_filename
        
        if logo_cache_path.exists() and not force:
            logger.info(f"Logo already downloaded for {symbol}, using cached file")
            return str(logo_cache_path)
        
        try:
            logger.info(f"Downloading logo for {symbol} from {logo_url}")
            response = requests.get(logo_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download and cache the logo image
            with open(logo_cache_path, 'wb') as logo_file:
                shutil.copyfileobj(response.raw, logo_file)
            
            logger.info(f"Logo downloaded and cached for {symbol}: {logo_cache_path}")
            return str(logo_cache_path)
        
        except requests.RequestException as e:
            logger.error(f"Failed to download logo for {symbol}: {e}")
            return None
    
    def download_and_cache_logo(self, symbol: str) -> Optional[str]:
        """
        Download company logo and cache as PNG file, return local file path.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Path to cached logo file or None if not available
        """
        symbol = symbol.upper()
        cache_key = f"finnhub_logo_file:{symbol}"
        
        # Check if we already have the logo file cached
        logo_filename = f"{symbol}.png"
        logo_path = self.logo_cache_dir / logo_filename
        
        # Check if file exists and is not too old (respect TTL)
        if logo_path.exists():
            file_age = time.time() - logo_path.stat().st_mtime
            if file_age < CACHE_TTL_SECONDS:
                logger.debug(f"Using cached logo file for {symbol}: {logo_path}")
                return str(logo_path)
            else:
                logger.debug(f"Cached logo file for {symbol} is expired, re-downloading")
        
        # Get logo URL
        logo_url = self.get_company_logo_url(symbol)
        if not logo_url:
            logger.debug(f"No logo URL available for {symbol}")
            return None
        
        try:
            # Download the logo
            logger.info(f"Downloading logo for {symbol} from {logo_url}")
            
            # Apply rate limiting
            rate_limiter.wait_for_rate_limit("finnhub.io")
            
            response = requests.get(logo_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                logger.warning(f"Logo URL returned non-image content for {symbol}: {content_type}")
                rate_limiter.record_failed_request("finnhub.io", response.status_code)
                return None
            
            # Save to cache
            temp_path = logo_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            # Atomic move to final location
            temp_path.rename(logo_path)
            
            logger.info(f"Successfully cached logo for {symbol}: {logo_path}")
            rate_limiter.record_request("finnhub.io")
            
            return str(logo_path)
                
        except requests.RequestException as e:
            logger.warning(f"Failed to download logo for {symbol}: {e}")
            rate_limiter.record_failed_request("finnhub.io", getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0)
            return None
        except Exception as e:
            logger.warning(f"Error caching logo for {symbol}: {e}")
            return None

    def copy_logo_to_output(self, symbol: str, output_dir: Path) -> Optional[str]:
        """
        Copy cached logo to output directory and return relative path.
        
        Args:
            symbol: Stock ticker symbol
            output_dir: Output directory path
            
        Returns:
            Relative path to logo in output directory or None if not available
        """
        # First ensure we have the logo cached
        cached_logo_path = self.download_and_cache_logo(symbol)
        if not cached_logo_path:
            return None
        
        try:
            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy logo to output directory
            logo_filename = f"{symbol.upper()}_logo.png"
            output_logo_path = output_dir / logo_filename
            
            shutil.copy2(cached_logo_path, output_logo_path)
            logger.info(f"Copied logo for {symbol} to output: {output_logo_path}")
            
            # Return relative path for use in HTML
            return logo_filename
            
        except Exception as e:
            logger.warning(f"Failed to copy logo for {symbol} to output: {e}")
            return None
    
    # ...existing code...


# Async interface for pipeline integration
async def fetch_company_logo_url(symbol: str) -> Optional[str]:
    """
    Async interface for fetching company logo URL.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        String URL of company logo or None if not available
    """
    import asyncio
    
    fetcher = FinnhubDataFetcher()
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetcher.get_company_logo_url, symbol)


async def fetch_company_profile(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Async interface for fetching company profile.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Dict containing company profile data or None if not available
    """
    import asyncio
    
    fetcher = FinnhubDataFetcher()
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetcher.get_company_profile, symbol)
