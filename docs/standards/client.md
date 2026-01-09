# Client Development Standards

## HTTP Client Patterns

**Always use httpx (async-first):**

```python
# ✅ Good
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers)

# ❌ Bad - using requests (synchronous)
import requests

response = requests.get(url, headers=headers)
```

## Base Client Structure

**Use a base client class with common functionality:**

```python
class BaseClient:
    """Base client with authentication and error handling."""

    def __init__(self, access_token: str, base_url: str = "https://..."):
        self.access_token = access_token
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> BaseClient:
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
```

## Error Handling

**Map HTTP status codes to typed exceptions:**

```python
async def _handle_response(self, response: httpx.Response) -> dict:
    """Handle HTTP response and raise appropriate exceptions."""
    if response.status_code == 401:
        raise AuthenticationError("Invalid or expired access token")

    if response.status_code == 404:
        raise NotFoundError(f"Resource not found: {response.url}")

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitError("Rate limit exceeded", retry_after=retry_after)

    if response.status_code == 422:
        raise ValidationError(f"Invalid request: {response.text}")

    if not response.is_success:
        raise PolarFlowError(f"API error: {response.status_code} {response.text}")

    return response.json()
```

## Rate Limiting

**Respect rate limit headers:**

```python
def _check_rate_limit(self, response: httpx.Response) -> None:
    """Check rate limit headers and warn if close to limit."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    limit = response.headers.get("X-RateLimit-Limit")

    if remaining and limit:
        if int(remaining) < int(limit) * 0.1:  # Less than 10% remaining
            logger.warning(
                f"Rate limit warning: {remaining}/{limit} requests remaining"
            )
```

## Request Methods

**Create generic request method with type safety:**

```python
from typing import TypeVar, Generic

T = TypeVar("T")

async def _request(
    self,
    method: str,
    path: str,
    response_model: type[T],
    **kwargs
) -> T:
    """Make HTTP request and parse response into Pydantic model.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        response_model: Pydantic model class for response
        **kwargs: Additional arguments for httpx request

    Returns:
        Parsed response as Pydantic model

    Raises:
        AuthenticationError: If token is invalid
        NotFoundError: If resource not found
        RateLimitError: If rate limit exceeded
    """
    if not self._client:
        raise RuntimeError("Client not initialized. Use 'async with' context manager.")

    response = await self._client.request(method, path, **kwargs)
    data = await self._handle_response(response)
    return response_model.model_validate(data)
```

## Context Manager Usage

**Always use context managers for resource cleanup:**

```python
# ✅ Good
async with PolarFlow(access_token="...") as client:
    sleep = await client.sleep.get(date="2026-01-09")

# ❌ Bad - no resource cleanup
client = PolarFlow(access_token="...")
sleep = await client.sleep.get(date="2026-01-09")
# Client connection never closed!
```

## Authentication

**Handle token validation at client initialization:**

```python
def __init__(self, access_token: str):
    if not access_token:
        raise ValueError("access_token is required")

    if len(access_token) < 10:  # Basic sanity check
        raise ValueError("access_token appears to be invalid")

    self.access_token = access_token
```

## Logging

**Use structured logging for debugging:**

```python
import logging

logger = logging.getLogger(__name__)

async def _request(self, method: str, path: str) -> dict:
    """Make HTTP request."""
    logger.debug(f"Request: {method} {path}")

    response = await self._client.request(method, path)

    logger.debug(f"Response: {response.status_code}")

    return await self._handle_response(response)
```
