"""
Rate limiting implementation using token bucket algorithm.

This module implements a token bucket rate limiter to control API request rates
and prevent exceeding external service limits. It provides configurable strategies
for handling rate limit conditions.

Note: This code follows PEP 8 style guidelines.
"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded and timeout occurs."""


class RateLimitStrategy(Enum):
    """Strategy to use when rate limit is exceeded."""

    FAIL_FAST = "fail_fast"  # Immediately return False if no tokens available
    WAIT = "wait"  # Wait for tokens to become available (default)
    TRY_ONCE = "try_once"  # Try once and fail if no tokens


@dataclass
class RateLimitMetrics:
    """Rate limit monitoring metrics."""

    requests_allowed: int = 0
    requests_denied: int = 0
    current_tokens: float = 0.0
    last_refill: datetime = datetime.now()
    total_wait_time: float = 0.0


class TokenBucket:
    """Token bucket rate limiter implementation."""

    def __init__(
        self,
        rate: float,  # Tokens per second
        capacity: float,  # Maximum tokens
        initial_tokens: Optional[float] = None,  # Initial token count
        strategy: RateLimitStrategy = RateLimitStrategy.WAIT,
    ):
        """Initialize token bucket."""
        self.rate = float(rate)
        self.capacity = float(capacity)
        self.tokens = float(initial_tokens if initial_tokens is not None else capacity)
        self.last_update = time.time()
        self.lock = threading.RLock()
        self.metrics = RateLimitMetrics()
        self.strategy = strategy

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        delta = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        self.last_update = now
        self.metrics.last_refill = datetime.now()
        self.metrics.current_tokens = self.tokens

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired, False otherwise
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.metrics.requests_allowed += 1
                self.metrics.current_tokens = self.tokens
                return True
            self.metrics.requests_denied += 1
            return False

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> float:
        """
        Acquire tokens, waiting if necessary.

        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait for tokens (in seconds)

        Returns:
            Time spent waiting in seconds

        Raises:
            RateLimitExceeded: If timeout occurs before tokens are acquired
        """
        if self.strategy == RateLimitStrategy.FAIL_FAST and not self.try_acquire(tokens):
            raise RateLimitExceeded("Rate limit exceeded (fail-fast mode)")

        wait_start = time.time()

        while not self.try_acquire(tokens):
            if timeout is not None and (time.time() - wait_start) >= timeout:
                raise RateLimitExceeded(
                    f"Rate limit exceeded, could not acquire {tokens} tokens within {timeout} seconds"
                )

            if self.strategy == RateLimitStrategy.TRY_ONCE:
                raise RateLimitExceeded("Rate limit exceeded (try-once mode)")

            # Calculate wait time needed for enough tokens
            with self.lock:
                self._refill()
                wait_time = (tokens - self.tokens) / self.rate
                if wait_time > 0:
                    time.sleep(min(wait_time, timeout or float("inf")))

        wait_time = time.time() - wait_start
        self.metrics.total_wait_time += wait_time
        return wait_time


class RateLimiterFactory:
    """Factory for creating and managing rate limiters."""

    def __init__(self):
        """Initialize rate limiter factory."""
        self._limiters: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def get_limiter(
        self,
        name: str,
        rate: float,
        capacity: float,
        strategy: RateLimitStrategy = RateLimitStrategy.WAIT,
        initial_tokens: Optional[float] = None,
    ) -> TokenBucket:
        """
        Get or create a rate limiter.

        Args:
            name: Unique identifier for the limiter
            rate: Tokens per second
            capacity: Maximum tokens
            strategy: Strategy to use when rate limit is exceeded
            initial_tokens: Initial token count (default: capacity)

        Returns:
            Token bucket rate limiter
        """
        with self._lock:
            if name not in self._limiters:
                self._limiters[name] = TokenBucket(
                    rate=rate, capacity=capacity, initial_tokens=initial_tokens, strategy=strategy
                )
            return self._limiters[name]

    def get_metrics(self, name: str) -> Optional[RateLimitMetrics]:
        """Get metrics for a specific rate limiter."""
        limiter = self._limiters.get(name)
        return limiter.metrics if limiter is not None else None

    def get_all_metrics(self) -> Dict[str, RateLimitMetrics]:
        """Get metrics for all rate limiters."""
        return {name: limiter.metrics for name, limiter in self._limiters.items()}
