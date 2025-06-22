"""
API Rate Limiter Module

This module provides a centralized rate limiting mechanism for all external API calls
to ensure compliance with rate limits and avoid spurious 401/429 errors. It implements:

1. A token bucket algorithm for smooth request distribution
2. Per-domain rate limiting with configurable limits
3. Global request tracking and logging
4. Automatic exponential backoff for failed requests
5. Thread-safety for concurrent requests

Usage:
    from altman_zscore.common.api_rate_limiter import APIRateLimiter
    
    # Get the singleton instance
    rate_limiter = APIRateLimiter.get_instance()
    
    # Wait until it's safe to make a request to a specific domain
    rate_limiter.wait_for_rate_limit("sec.gov")
    
    # Record a successful request
    rate_limiter.record_request("sec.gov")
    
    # Record a failed request (will affect backoff)
    rate_limiter.record_failed_request("sec.gov")
    
    # Decorated function usage
    @rate_limiter.rate_limited("sec.gov")
    def fetch_sec_data(url):
        # Your API call here
        pass
"""

import time
import logging
import threading
import random
from typing import Dict, Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """
    Singleton class for managing API rate limits across the application.
    
    Implements a token bucket algorithm with domain-specific configurations
    and global request tracking.
    """
    
    # Default rate limits per domain (requests per second)
    DEFAULT_RATE_LIMITS = {
        "sec.gov": 0.1,           # SEC EDGAR: max 10 requests per second (100ms between requests)
        "finance.yahoo.com": 0.5,  # Yahoo Finance: max 2 requests per second (500ms between requests)
        "finnhub.io": 1.0,         # Finnhub: max 1 request per second
        "openai.azure.com": 1.0,   # Azure OpenAI: max 1 request per second
        "default": 1.0             # Default for any other domain
    }
    
    # Maximum backoff time in seconds
    MAX_BACKOFF = 64  # ~1 minute
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of APIRateLimiter."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = APIRateLimiter()
        return cls._instance
    
    def __init__(self):
        """Initialize the rate limiter with domain-specific configurations."""
        # Track the last request time per domain
        self._last_request_times: Dict[str, float] = {}
        
        # Track backoff state per domain
        self._backoff_state: Dict[str, Dict] = {}
        
        # Rate limit configuration per domain (requests per second)
        self.rate_limits = self.DEFAULT_RATE_LIMITS.copy()
        
        # Global statistics and tracking
        self.request_count = 0
        self.request_times = []
        self.error_count = 0
        
        # Lock for thread safety
        self._domain_locks: Dict[str, threading.Lock] = {}
        
        # Initialize start time
        self.start_time = time.time()
        
        # Initialize domain locks
        for domain in self.rate_limits:
            self._domain_locks[domain] = threading.Lock()
    
    def get_domain_lock(self, domain: str) -> threading.Lock:
        """Get or create a lock for the specified domain."""
        if domain not in self._domain_locks:
            with self._lock:
                if domain not in self._domain_locks:
                    self._domain_locks[domain] = threading.Lock()
        return self._domain_locks[domain]
    
    def extract_domain(self, url: str) -> str:
        """Extract the domain from a URL for rate limiting."""
        # Simple domain extraction - can be made more sophisticated if needed
        for domain in self.rate_limits:
            if domain in url:
                return domain
        return "default"
    
    def wait_for_rate_limit(self, domain: str) -> None:
        """
        Wait until it's safe to make a request to the specified domain.
        
        This implements the token bucket algorithm with exponential backoff
        for failed requests.
        
        Args:
            domain: The domain to check rate limits for
        """
        domain_key = domain if domain in self.rate_limits else "default"
        min_interval = 1.0 / self.rate_limits[domain_key]  # seconds between requests
        
        # Get domain-specific lock
        domain_lock = self.get_domain_lock(domain_key)
        
        with domain_lock:
            current_time = time.time()
            
            # Check if we need to apply backoff
            backoff_seconds = 0
            if domain_key in self._backoff_state:
                state = self._backoff_state[domain_key]
                if state["active"] and current_time < state["expires_at"]:
                    backoff_seconds = state["current_backoff"]
                    
            # Calculate wait time based on rate limit and last request
            wait_time = 0
            if domain_key in self._last_request_times:
                elapsed = current_time - self._last_request_times[domain_key]
                wait_time = max(0, min_interval - elapsed)
            
            # Apply additional jitter (±10%) to prevent request clustering
            jitter = random.uniform(0.9, 1.1)
            total_wait = (wait_time + backoff_seconds) * jitter
            
            if total_wait > 0:
                if backoff_seconds > 0:
                    logger.debug(
                        f"Rate limiting {domain_key}: Waiting {total_wait:.4f}s "
                        f"(backoff: {backoff_seconds:.2f}s, rate limit: {wait_time:.2f}s)"
                    )
                else:
                    logger.debug(f"Rate limiting {domain_key}: Waiting {total_wait:.4f}s")
                    
                time.sleep(total_wait)
    
    def record_request(self, domain: str) -> None:
        """
        Record a successful request to the specified domain.
        
        Args:
            domain: The domain the request was made to
        """
        domain_key = domain if domain in self.rate_limits else "default"
        
        with self._lock:
            # Record global statistics
            self.request_count += 1
            self.request_times.append(time.time())
            
            # Trim request times to keep only the last 1000 entries
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
        
        # Record domain-specific timestamp
        domain_lock = self.get_domain_lock(domain_key)
        with domain_lock:
            self._last_request_times[domain_key] = time.time()
            
            # Reset backoff if it was active
            if domain_key in self._backoff_state and self._backoff_state[domain_key]["active"]:
                self._backoff_state[domain_key]["active"] = False
                logger.info(f"Reset backoff for {domain_key}")
    
    def record_failed_request(self, domain: str, status_code: Optional[int] = None) -> None:
        """
        Record a failed request to the specified domain and apply exponential backoff.
        
        Args:
            domain: The domain the failed request was made to
            status_code: Optional HTTP status code for customized backoff strategies
        """
        domain_key = domain if domain in self.rate_limits else "default"
        
        with self._lock:
            self.error_count += 1
        
        domain_lock = self.get_domain_lock(domain_key)
        with domain_lock:
            current_time = time.time()
            
            # Initialize or update backoff state
            if domain_key not in self._backoff_state:
                self._backoff_state[domain_key] = {
                    "active": True,
                    "attempts": 1,
                    "current_backoff": 1,  # Start with 1 second
                    "expires_at": current_time + 1
                }
            else:
                state = self._backoff_state[domain_key]
                state["active"] = True
                state["attempts"] += 1
                
                # Calculate exponential backoff with max limit
                new_backoff = min(2 ** (state["attempts"] - 1), self.MAX_BACKOFF)
                
                # Special case for SEC 401/429 errors - use longer backoff
                if status_code in (401, 429) and "sec.gov" in domain_key:
                    # For SEC API, use longer backoffs for 401/429 errors
                    new_backoff = min(new_backoff * 2, self.MAX_BACKOFF)
                
                state["current_backoff"] = new_backoff
                state["expires_at"] = current_time + new_backoff
            
            backoff_time = self._backoff_state[domain_key]["current_backoff"]
            logger.warning(
                f"Applied exponential backoff for {domain_key}: "
                f"{backoff_time:.2f}s after {self._backoff_state[domain_key]['attempts']} failed attempts"
            )
    
    def get_statistics(self) -> Dict:
        """Get current rate limiting statistics."""
        with self._lock:
            now = time.time()
            elapsed = now - self.start_time
            
            # Calculate requests per minute in the last minute
            one_minute_ago = now - 60
            recent_requests = [t for t in self.request_times if t >= one_minute_ago]
            rpm = len(recent_requests)
            
            stats = {
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "error_rate": self.error_count / max(1, self.request_count),
                "uptime_seconds": elapsed,
                "requests_per_minute": rpm,
                "requests_per_second": self.request_count / max(1, elapsed),
                "backoff_state": {},
            }
            
            # Add backoff state
            for domain, state in self._backoff_state.items():
                if state["active"] and now < state["expires_at"]:
                    stats["backoff_state"][domain] = {
                        "active": True,
                        "remaining_seconds": state["expires_at"] - now,
                        "attempts": state["attempts"],
                    }
            
            return stats
    
    def rate_limited(self, domain: str):
        """
        Decorator for rate limiting functions making API calls.
        
        Args:
            domain: The domain the decorated function calls
            
        Usage:
            @rate_limiter.rate_limited("sec.gov")
            def fetch_sec_data(url):
                # API call
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.wait_for_rate_limit(domain)
                try:
                    result = func(*args, **kwargs)
                    self.record_request(domain)
                    return result
                except Exception as e:
                    # Check if exception has a status_code attribute
                    status_code = getattr(e, 'status_code', None)
                    if status_code is None and hasattr(e, 'response'):
                        status_code = getattr(e.response, 'status_code', None)
                    
                    self.record_failed_request(domain, status_code)
                    raise
            return wrapper
        return decorator


# Global timer for tracking API call intervals
class GlobalAPITimer:
    """
    Global timer class for tracking API call intervals and ensuring minimum spacing.
    
    This is a simpler alternative to the full APIRateLimiter when only basic
    timing between calls is needed.
    """
    
    def __init__(self):
        """Initialize the global API timer."""
        self.last_call_time = {}
        self.lock = threading.Lock()
    
    def wait_and_mark(self, domain: str, min_interval: float = 0.1) -> None:
        """
        Wait for the minimum interval and mark the call time.
        
        Args:
            domain: Domain identifier for the API
            min_interval: Minimum interval between calls in seconds
        """
        with self.lock:
            now = time.time()
            if domain in self.last_call_time:
                elapsed = now - self.last_call_time[domain]
                if elapsed < min_interval:
                    sleep_time = min_interval - elapsed
                    time.sleep(sleep_time)
            self.last_call_time[domain] = time.time()


# Singleton instances for easy import
rate_limiter = APIRateLimiter.get_instance()
global_timer = GlobalAPITimer()


# Example usage functions
def example_usage():
    """Example usage of the rate limiter."""
    
    # Method 1: Manual wait and record
    rate_limiter.wait_for_rate_limit("sec.gov")
    try:
        # Make API call here
        print("API call succeeded!")
        rate_limiter.record_request("sec.gov")
    except Exception as e:
        rate_limiter.record_failed_request("sec.gov")
        raise
    
    # Method 2: Using decorator
    @rate_limiter.rate_limited("sec.gov")
    def fetch_data(url):
        # Make API call here
        return f"Data from {url}"
    
    result = fetch_data("https://data.sec.gov/api/...")
    print(result)
    
    # Method 3: Using simpler global timer
    global_timer.wait_and_mark("sec.gov", 0.1)
    # Make API call here
    

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    example_usage()
