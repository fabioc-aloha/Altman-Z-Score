"""Request manager for handling concurrent API requests with rate limiting."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

import aiohttp

from .rate_limiter import TokenBucket

T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Request performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    retried_requests: int = 0
    total_time: float = 0.0
    last_request: Optional[datetime] = None


class RequestManager(Generic[T]):
    """Manages concurrent API requests with rate limiting and retries."""

    def __init__(
        self,
        rate_limiter: TokenBucket,
        max_concurrent: int = 5,
        max_retries: int = 3,
        retry_codes: Optional[List[int]] = None,
        backoff_factor: float = 1.5,
    ):
        """
        Initialize request manager.

        Args:
            rate_limiter: Token bucket rate limiter
            max_concurrent: Maximum concurrent requests
            max_retries: Maximum retry attempts
            retry_codes: HTTP status codes to retry
            backoff_factor: Exponential backoff multiplier
        """
        self.rate_limiter = rate_limiter
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_retries = max_retries
        self.retry_codes = retry_codes or [429, 500, 502, 503, 504]
        self.backoff_factor = backoff_factor
        self.metrics = RequestMetrics()

    async def make_request(self, url: str, method: str = "GET", **kwargs) -> aiohttp.ClientResponse:
        """
        Make an HTTP request with rate limiting and retries.

        Args:
            url: Request URL
            method: HTTP method
            kwargs: Additional arguments for aiohttp request
        Returns:
            aiohttp.ClientResponse: The HTTP response object if successful.
        Raises:
            RuntimeError: If all retries fail.
        """
        for attempt in range(self.max_retries + 1):
            async with self.semaphore:
                # Convert synchronous rate limiter to async
                await asyncio.get_event_loop().run_in_executor(None, self.rate_limiter.acquire)
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.request(method, url, **kwargs) as response:
                            self.metrics.total_requests += 1
                            self.metrics.last_request = datetime.utcnow()
                            if response.status in self.retry_codes and attempt < self.max_retries:
                                self.metrics.retried_requests += 1
                                await asyncio.sleep(self.backoff_factor ** attempt)
                                continue
                            if response.status >= 400:
                                self.metrics.failed_requests += 1
                            else:
                                self.metrics.successful_requests += 1
                            return response
                except aiohttp.ClientError as exc:
                    logger.warning(f"Request failed: {exc}")
                    if attempt < self.max_retries:
                        self.metrics.retried_requests += 1
                        await asyncio.sleep(self.backoff_factor ** attempt)
                        continue
                    self.metrics.failed_requests += 1
                    raise
        # If all retries fail, raise an error to satisfy the declared return type
        raise RuntimeError(f"All retries failed for request to {url}")

    async def _acquire_slot(self) -> None:
        """Acquire both a rate limit token and concurrency slot."""
        async with self.semaphore:
            # Convert synchronous rate limiter to async
            await asyncio.get_event_loop().run_in_executor(None, self.rate_limiter.acquire)
            self.metrics.total_requests += 1

    def _get_retry_wait_time(self, attempt: int) -> float:
        """Calculate retry wait time using exponential backoff."""
        return self.backoff_factor**attempt


class BatchRequestManager(Generic[T]):
    """Manages batched API requests with automatic rate limiting."""

    def __init__(
        self,
        request_manager: RequestManager[T],
        batch_size: int = 10,
        max_concurrent_batches: int = 2,
    ):
        """
        Initialize batch request manager.

        Args:
            request_manager: Request manager for individual requests
            batch_size: Maximum items per batch
            max_concurrent_batches: Maximum concurrent batch requests
        """
        self.request_manager = request_manager
        self.batch_size = batch_size
        self.batch_semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def process_items(self, items: List[T], process_func: Callable[[T], Any]) -> Dict[T, Any]:
        """
        Process items in batches.

        Args:
            items: Items to process
            process_func: Function to process each item

        Returns:
            Dictionary mapping items to their results
        """
        results: Dict[T, Any] = {}
        batches = [items[i: i + self.batch_size] for i in range(0, len(items), self.batch_size)]

        async def process_batch(batch: List[T]) -> None:
            async with self.batch_semaphore:
                batch_results = await asyncio.gather(*[process_func(item) for item in batch], return_exceptions=True)
                for item, result in zip(batch, batch_results):
                    if not isinstance(result, Exception):
                        results[item] = result

        await asyncio.gather(*[process_batch(batch) for batch in batches])
        return results
