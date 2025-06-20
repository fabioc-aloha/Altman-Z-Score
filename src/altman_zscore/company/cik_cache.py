"""
CIK Cache Module
================

Provides a robust caching system for SEC CIK (Central Index Key) lookups.
Implements a fallback strategy:
1. Use local cache if available and fresh (< 24 hours old)
2. If cache is stale, try to update from SEC; if update fails, use stale cache with warning
3. If no cache exists, download it initially

This module replaces the previous shipped/bootstrap cache system with a simpler
user-managed cache that gracefully handles SEC API availability issues.
"""

import json
import logging
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import warnings
from .. import __version__

logger = logging.getLogger(__name__)

# Global SEC rate limiter to prevent 401 errors across all SEC API calls
class _GlobalSECRateLimiter:
    """Global rate limiter for all SEC API calls to prevent 401 errors."""
    
    def __init__(self):
        self._last_request_time = 0
        self._min_interval = 1.0 / 6.0  # 6 requests per second (conservative)
    
    def wait_if_needed(self):
        """Wait if necessary to respect SEC rate limits."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

# Global instance
_sec_rate_limiter = _GlobalSECRateLimiter()

class CIKCache:
    """
    Robust CIK cache with fallback strategy for handling SEC API unavailability.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize CIK cache.
        
        Args:
            cache_dir: Directory to store cache files. If None, uses default location.
        """
        if cache_dir is None:
            # Default cache location in the api/cache directory
            self.cache_dir = Path(__file__).parent.parent / "api" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "sec_company_tickers_cache.json"
        self.metadata_file = self.cache_dir / "sec_cache_metadata.json"
        
        # SEC URLs
        self.company_tickers_url = "https://www.sec.gov/files/company_tickers.json"
        
        # Cache freshness threshold (24 hours)
        self.cache_max_age = timedelta(hours=24)
        
        # Load cache on initialization
        self._cache_data: Dict[str, str] = {}
        self._cache_metadata: Dict[str, Any] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache data and metadata from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    # Convert to ticker -> CIK mapping
                    self._cache_data = {}
                    for entry in raw_data.values():
                        if isinstance(entry, dict) and 'ticker' in entry and 'cik_str' in entry:
                            ticker = entry['ticker'].upper()
                            cik = str(entry['cik_str']).zfill(10)
                            self._cache_data[ticker] = cik
                
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self._cache_metadata = json.load(f)
            else:
                self._cache_metadata = {}
                
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self._cache_data = {}
            self._cache_metadata = {}
    
    def _save_cache(self, raw_data: Dict[str, Any]) -> None:
        """Save cache data and update metadata."""
        try:
            # Save raw data
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2)
            
            # Update metadata
            self._cache_metadata = {
                'last_updated': datetime.now().isoformat(),
                'source': 'sec_company_tickers',
                'url': self.company_tickers_url,
                'total_entries': len(raw_data)
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_metadata, f, indent=2)
            
            logger.info(f"Cache updated with {len(raw_data)} entries")
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            raise
    
    def _is_cache_fresh(self) -> bool:
        """Check if cache is fresh (less than 24 hours old)."""
        if not self._cache_metadata.get('last_updated'):
            return False
        
        try:
            last_updated = datetime.fromisoformat(self._cache_metadata['last_updated'])
            age = datetime.now() - last_updated
            return age < self.cache_max_age
        except (ValueError, TypeError):
            return False
    
    def _update_cache_from_sec(self) -> bool:
        """
        Attempt to update cache from SEC API.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating CIK cache from SEC...")
            headers = {
                'User-Agent': self._get_dynamic_user_agent(),
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'www.sec.gov'
            }
            _sec_rate_limiter.wait_if_needed()  # Respect SEC rate limit
            response = requests.get(
                self.company_tickers_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            raw_data = response.json()
            
            # Validate data structure
            if not isinstance(raw_data, dict) or not raw_data:
                logger.error("Invalid data structure received from SEC")
                return False
            
            # Save cache
            self._save_cache(raw_data)
            
            # Reload cache
            self._load_cache()
            
            return True
            
        except requests.RequestException as e:
            logger.warning(f"Failed to update cache from SEC: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating cache: {e}")
            return False
    
    def _ensure_cache_available(self) -> bool:
        """
        Ensure cache is available, implementing fallback strategy.
        
        Returns:
            True if cache is available (fresh or stale), False if no cache at all
        """
        # If no cache exists, try to download it
        if not self._cache_data:
            logger.info("No CIK cache found, attempting initial download...")
            if self._update_cache_from_sec():
                return True
            else:
                logger.error("Failed to download initial CIK cache from SEC")
                return False
        
        # If cache exists but is stale, try to update
        if not self._is_cache_fresh():
            logger.info("CIK cache is stale, attempting update...")
            if self._update_cache_from_sec():
                logger.info("Cache updated successfully")
            else:
                # Use stale cache with warning
                age_str = "unknown"
                if self._cache_metadata.get('last_updated'):
                    try:
                        last_updated = datetime.fromisoformat(self._cache_metadata['last_updated'])
                        age = datetime.now() - last_updated
                        age_str = f"{age.days} days old"
                    except:
                        pass
                
                warning_msg = (
                    f"Using stale CIK cache ({age_str}). "
                    f"SEC API may be temporarily unavailable. "
                    f"CIK lookups will use cached data which may be outdated."
                )
                warnings.warn(warning_msg, UserWarning)
                logger.warning(warning_msg)
        
        return True
    
    def lookup_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK for a ticker symbol.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            10-digit CIK string if found, None otherwise
        """
        if not ticker:
            return None
        
        ticker = ticker.upper().strip()
        
        # Ensure cache is available
        if not self._ensure_cache_available():
            logger.error("CIK cache is not available")
            return None
        
        # Look up in cache
        cik = self._cache_data.get(ticker)
        if cik:
            logger.debug(f"Found CIK {cik} for ticker {ticker} in cache")
            return cik
        else:
            logger.debug(f"No CIK found for ticker {ticker} in cache")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'total_entries': len(self._cache_data),
            'cache_file_exists': self.cache_file.exists(),
            'metadata': self._cache_metadata.copy(),
            'is_fresh': self._is_cache_fresh(),
            'cache_location': str(self.cache_file)
        }
    
    def _get_dynamic_user_agent(self):
        user_agent = os.environ.get("SEC_EDGAR_USER_AGENT", None)
        if user_agent:
            if "__version__" in user_agent:
                user_agent = user_agent.replace("__version__", __version__)
            return user_agent
        # If not set, try to build from components
        email = os.environ.get("SEC_API_EMAIL", "info@example.com")
        return f"AltmanZScore/{__version__} {email}"


# Global cache instance
_global_cache: Optional[CIKCache] = None

def get_cache() -> CIKCache:
    """Get the global CIK cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CIKCache()
    return _global_cache

def lookup_cik_cached(ticker: str) -> Optional[str]:
    """
    Convenience function for CIK lookup using global cache.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        10-digit CIK string if found, None otherwise
    """
    return get_cache().lookup_cik(ticker)

def refresh_cache() -> bool:
    """
    Force refresh the global cache from SEC.
    
    Returns:
        True if successful, False otherwise
    """
    cache = get_cache()
    return cache._update_cache_from_sec()

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the global cache."""
    return get_cache().get_cache_stats()
