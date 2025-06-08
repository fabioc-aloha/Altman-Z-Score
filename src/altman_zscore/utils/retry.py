"""
Retry utilities for network requests.
"""

import logging
import time
from functools import wraps
from typing import TypeVar, Callable, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')

def exponential_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Initial delay between retries in seconds
        backoff_factor (float): Factor to multiply delay by after each retry
        exceptions (tuple): Tuple of exceptions to catch and retry on

    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed with error: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries} retries failed. "
                            f"Final error: {str(e)}"
                        )

            if last_exception:
                raise last_exception
            return None  # Unreachable but keeps type checker happy

        return wrapper
    return decorator
