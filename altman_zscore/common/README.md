# API Rate Limiter

This module provides a robust rate limiting system to prevent API rate limit errors (401/429) and ensure reliable API interactions across the Altman Z-Score pipeline.

## Key Features

- **Token Bucket Algorithm**: Smooth distribution of API requests over time
- **Per-Domain Configuration**: Customized limits for each API provider
- **Exponential Backoff**: Automatic retry with increasing delays after failures
- **Domain-Specific Handling**: Special handling for SEC 401/429 errors
- **Thread Safety**: Lock-based synchronization for concurrent requests
- **Comprehensive Logging**: Detailed logging of all rate limiting actions
- **Usage Statistics**: Real-time monitoring of API request patterns

## Installation

The API rate limiter is automatically included as part of the Altman Z-Score package. No separate installation is required.

## Usage

### Decorator Pattern (Recommended)

```python
from altman_zscore.common.api_rate_limiter import rate_limiter

@rate_limiter.rate_limited("sec.gov")
def fetch_sec_data(url):
    # Make API call here
    return response
```

### Manual Usage

```python
from altman_zscore.common.api_rate_limiter import rate_limiter

# Before making the API call
rate_limiter.wait_for_rate_limit("sec.gov")

try:
    # Make your API call
    response = requests.get(url)
    rate_limiter.record_request("sec.gov")  # Record successful request
    return response
except Exception as e:
    # Get status code if available
    status_code = getattr(e, 'status_code', None)
    if status_code is None and hasattr(e, 'response'):
        status_code = getattr(e.response, 'status_code', None)
    
    # Record failure with status code for better backoff
    rate_limiter.record_failed_request("sec.gov", status_code)
    raise  # Re-raise the exception
```

### Simplified Global Timer

For simpler use cases:

```python
from altman_zscore.common.api_rate_limiter import global_timer

# Wait and mark in one call
global_timer.wait_and_mark("sec.gov", min_interval=0.1)
# Make your API call
```

## Default Rate Limits

| API Domain          | Requests Per Second | Minimum Interval |
|---------------------|---------------------|-----------------|
| sec.gov             | 10                  | 100ms           |
| finance.yahoo.com   | 2                   | 500ms           |
| finnhub.io          | 1                   | 1000ms          |
| openai.azure.com    | 1                   | 1000ms          |

These can be customized by modifying the `rate_limits` dictionary:

```python
from altman_zscore.common.api_rate_limiter import rate_limiter

# Customize rate limits
rate_limiter.rate_limits.update({
    "sec.gov": 0.05  # 20 requests per second (50ms interval)
})
```

## Statistics and Monitoring

```python
# Get current statistics
stats = rate_limiter.get_statistics()

print(f"Total requests: {stats['total_requests']}")
print(f"Error rate: {stats['error_rate']:.2%}")
print(f"Requests per minute: {stats['requests_per_minute']}")

# Check active backoffs
for domain, backoff in stats['backoff_state'].items():
    print(f"{domain}: {backoff['remaining_seconds']:.1f}s remaining")
```

## Thread Safety

The API rate limiter is fully thread-safe and can be used in multi-threaded environments. It uses per-domain locks to ensure that concurrent requests to the same domain are properly rate-limited.

## Error Handling

The rate limiter automatically applies exponential backoff when API requests fail:

1. First failure: 1 second delay
2. Second failure: 2 seconds delay
3. Third failure: 4 seconds delay
4. Fourth failure: 8 seconds delay
5. And so on, up to a maximum of 64 seconds

For SEC API 401/429 errors, an enhanced backoff strategy is applied with doubled delay times.

## Logging

The rate limiter logs all actions at the DEBUG level for normal operations and WARNING level for backoff events:

```
2025-06-21 10:15:23 - api_rate_limiter - DEBUG - Rate limiting sec.gov: Waiting 0.1025s
2025-06-21 10:15:30 - api_rate_limiter - WARNING - Applied exponential backoff for sec.gov: 2.00s after 1 failed attempts
```

To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
