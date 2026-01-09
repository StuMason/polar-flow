# Error Handling

All errors inherit from `PolarFlowError`.

## Exception Hierarchy

```
PolarFlowError (base)
├── AuthenticationError (401)
├── NotFoundError (404)
├── RateLimitError (429)
└── ValidationError (400/422)
```

## Exception Attributes

All exceptions have these attributes:

- `endpoint: str | None` - API endpoint that failed
- `status_code: int | None` - HTTP status code
- `response_body: str | None` - Response body (truncated to 500 chars)

`RateLimitError` additionally has:

- `retry_after: int` - Seconds to wait before retrying

## Exception Types

### AuthenticationError

**When raised:**

- Token is invalid or expired (401 Unauthorized)
- Token has been revoked by user

**Example:**

```python
from polar_flow import AuthenticationError

try:
    sleep = await client.sleep.list(user_id="self")
except AuthenticationError as e:
    print(f"Authentication failed at {e.endpoint}")
    print("Token expired. Re-run 'polar-flow auth' to get a new token.")
```

**Solutions:**

- Re-run `polar-flow auth` to get a new access token
- Check that your token hasn't been revoked in the Polar dashboard

### NotFoundError

**When raised:**

- Resource doesn't exist (404 Not Found)
- Sleep data not yet processed (usually available by 10am)
- Requesting future dates
- No data recorded for that date

**Example:**

```python
from polar_flow import NotFoundError

try:
    sleep = await client.sleep.get(user_id="self", date="2026-01-09")
except NotFoundError as e:
    print(f"No data found: {e}")
    print(f"Endpoint: {e.endpoint}")
    print(f"Status: {e.status_code}")
```

**Solutions:**

- Check if the date is valid and in the past
- For sleep data, wait until later in the day (Polar processes sleep data in the morning)
- Verify you have data recorded for that date in the Polar Flow app

### RateLimitError

**When raised:**

- Too many requests too quickly (429 Too Many Requests)
- Polar API enforces rate limits per user

**Example:**

```python
import asyncio
from polar_flow import RateLimitError

try:
    data = await client.sleep.list(user_id="self", days=28)
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
    # Retry the request
    data = await client.sleep.list(user_id="self", days=28)
```

**Solutions:**

- Implement backoff logic using the `retry_after` attribute
- Reduce request frequency
- Batch operations when possible

### ValidationError

**When raised:**

- Invalid request parameters (400/422)
- Invalid date format (must be YYYY-MM-DD)
- Date out of range (max 28-30 days history)
- Invalid exercise ID or other identifiers

**Example:**

```python
from polar_flow import ValidationError

try:
    sleep = await client.sleep.get(user_id="self", date="01-09-2026")  # Wrong format
except ValidationError as e:
    print(f"Invalid request: {e}")
    print(f"Details: {e.response_body}")
```

**Solutions:**

- Use YYYY-MM-DD format for dates
- Check parameter ranges and constraints
- Read the error message details in `response_body`

## Common Patterns

### Graceful Degradation

Handle missing data gracefully:

```python
from polar_flow import NotFoundError

async def get_sleep_safe(client, date):
    try:
        return await client.sleep.get(user_id="self", date=date)
    except NotFoundError:
        return None  # No data for this date

# Use it
sleep = await get_sleep_safe(client, "2026-01-09")
if sleep:
    print(f"Sleep score: {sleep.sleep_score}")
else:
    print("No sleep data for this date")
```

### Retry with Backoff

Handle rate limits with exponential backoff:

```python
import asyncio
from polar_flow import RateLimitError

async def fetch_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.sleep.list(user_id="self", days=28)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Max retries reached
            print(f"Rate limited. Waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)

data = await fetch_with_retry(client)
```

### Logging Errors

Log errors with full context:

```python
import logging
from polar_flow import PolarFlowError

logger = logging.getLogger(__name__)

try:
    sleep = await client.sleep.list(user_id="self")
except PolarFlowError as e:
    logger.error(
        f"API error: {e}",
        extra={
            "endpoint": e.endpoint,
            "status_code": e.status_code,
            "response_body": e.response_body,
        }
    )
    raise
```

## Production Recommendations

1. **Always use the async context manager** to ensure proper cleanup:

   ```python
   async with PolarFlow(access_token=token) as client:
       # Your code here
   ```

2. **Handle RateLimitError** with proper backoff logic

3. **Log errors** with full context for debugging

4. **Don't retry forever** - set maximum retry limits

5. **Handle NotFoundError gracefully** - missing data is normal
