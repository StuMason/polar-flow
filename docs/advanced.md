# Advanced Usage

Advanced patterns for building production applications with polar-flow.

## Incremental Sync

Fetch only new data since last sync using the `since=` parameter.

```python
from datetime import date
from polar_flow import PolarFlow, load_token_from_file

async def sync_sleep_data(last_sync_date: str):
    """Sync sleep data since last sync date."""
    token = load_token_from_file()

    async with PolarFlow(access_token=token) as client:
        # Fetch only data since last sync
        new_sleep_data = await client.sleep.list(
            user_id="self",
            since=last_sync_date
        )

        print(f"Fetched {len(new_sleep_data)} new sleep records")

        for sleep in new_sleep_data:
            # Store in database
            await store_sleep_data(sleep)

        return str(date.today())

# Run sync
last_sync = "2026-01-01"
new_last_sync = await sync_sleep_data(last_sync)
```

## Bulk Data Fetching

Fetch all data types efficiently:

```python
async def fetch_all_data(client):
    """Fetch all available data in one session."""

    # Fetch in parallel using asyncio.gather
    sleep, recharge, activities, exercises = await asyncio.gather(
        client.sleep.list(user_id="self", days=28),
        client.recharge.list(),
        client.activity.list(),
        client.exercises.list(),
        return_exceptions=True  # Don't fail if one endpoint fails
    )

    # Handle potential errors
    if isinstance(sleep, Exception):
        print(f"Sleep fetch failed: {sleep}")
        sleep = []

    return {
        "sleep": sleep if not isinstance(sleep, Exception) else [],
        "recharge": recharge if not isinstance(recharge, Exception) else [],
        "activities": activities if not isinstance(activities, Exception) else [],
        "exercises": exercises if not isinstance(exercises, Exception) else [],
    }
```

## Rate Limit Handling

Implement sophisticated rate limit handling for production:

```python
import asyncio
from polar_flow import RateLimitError

class RateLimitedClient:
    def __init__(self, client):
        self.client = client
        self.max_retries = 3
        self.backoff_factor = 2

    async def fetch_with_backoff(self, coro):
        """Execute coroutine with exponential backoff on rate limits."""
        for attempt in range(self.max_retries):
            try:
                return await coro
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = e.retry_after * (self.backoff_factor ** attempt)
                print(f"Rate limited. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)

# Use it
async with PolarFlow(access_token=token) as client:
    rl_client = RateLimitedClient(client)
    sleep_data = await rl_client.fetch_with_backoff(
        client.sleep.list(user_id="self", days=28)
    )
```

## Custom Timeout Configuration

Configure request timeouts:

```python
from polar_flow import PolarFlow
import httpx

# Create client with custom timeout
async def main():
    async with PolarFlow(access_token=token) as client:
        # Override default timeout (30s)
        client._client.timeout = httpx.Timeout(60.0)  # 60 second timeout

        # Long-running request
        exercises = await client.exercises.list()
```

## Data Export Patterns

### Export to JSON

```python
import json
from pathlib import Path

async def export_sleep_to_json(client, output_path: Path):
    """Export sleep data to JSON file."""
    sleep_data = await client.sleep.list(user_id="self", days=28)

    # Convert Pydantic models to dicts
    data = [sleep.model_dump() for sleep in sleep_data]

    output_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Exported {len(data)} sleep records to {output_path}")

await export_sleep_to_json(client, Path("sleep_data.json"))
```

### Export to CSV

```python
import csv
from pathlib import Path

async def export_exercises_to_csv(client, output_path: Path):
    """Export exercises to CSV file."""
    exercises = await client.exercises.list()

    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            "Date", "Sport", "Duration (min)",
            "Calories", "Distance (km)", "Avg HR"
        ])

        # Write data
        for ex in exercises:
            writer.writerow([
                ex.start_time.date(),
                ex.sport,
                ex.duration_minutes,
                ex.calories or 0,
                ex.distance_km or 0,
                ex.average_heart_rate or 0,
            ])

    print(f"Exported {len(exercises)} exercises to {output_path}")

await export_exercises_to_csv(client, Path("exercises.csv"))
```

## Scheduled Sync Jobs

Run periodic syncs with APScheduler:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from polar_flow import PolarFlow, load_token_from_file

async def sync_job():
    """Sync all data from Polar API."""
    token = load_token_from_file()

    async with PolarFlow(access_token=token) as client:
        # Sync sleep data
        sleep = await client.sleep.list(user_id="self", since="2026-01-01")
        print(f"Synced {len(sleep)} sleep records")

        # Sync recharge data
        recharge = await client.recharge.list(since="2026-01-01")
        print(f"Synced {len(recharge)} recharge records")

# Setup scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(sync_job, "interval", hours=1)
scheduler.start()

# Keep running
await asyncio.Event().wait()
```

## Database Integration

Store data in SQLite:

```python
import aiosqlite
from datetime import date

async def store_sleep_data(db_path: str):
    """Fetch and store sleep data in SQLite."""
    token = load_token_from_file()

    async with aiosqlite.connect(db_path) as db:
        # Create table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sleep (
                date TEXT PRIMARY KEY,
                sleep_score INTEGER,
                total_sleep_seconds INTEGER,
                deep_sleep_seconds INTEGER,
                rem_sleep_seconds INTEGER,
                hrv_avg REAL
            )
        """)

        async with PolarFlow(access_token=token) as client:
            sleep_data = await client.sleep.list(user_id="self", days=28)

            for sleep in sleep_data:
                await db.execute("""
                    INSERT OR REPLACE INTO sleep VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    sleep.date,
                    sleep.sleep_score,
                    sleep.total_sleep_seconds,
                    sleep.deep_sleep_seconds,
                    sleep.rem_sleep_seconds,
                    sleep.hrv_avg,
                ))

        await db.commit()

await store_sleep_data("polar_data.db")
```

## Error Recovery

Implement robust error recovery:

```python
from polar_flow import PolarFlowError, NotFoundError
import logging

logger = logging.getLogger(__name__)

async def sync_with_recovery(client, dates: list[str]):
    """Sync data with error recovery."""
    successful = []
    failed = []

    for date in dates:
        try:
            sleep = await client.sleep.get(user_id="self", date=date)
            successful.append(date)
            await store_sleep(sleep)

        except NotFoundError:
            logger.info(f"No data for {date}")
            # Not an error - just no data

        except PolarFlowError as e:
            logger.error(f"Failed to fetch {date}: {e}")
            failed.append(date)

    print(f"Success: {len(successful)}, Failed: {len(failed)}")
    return successful, failed
```

## Testing

Mock the Polar API for testing:

```python
import pytest
from polar_flow import PolarFlow
from polar_flow.models.sleep import SleepData

@pytest.mark.asyncio
async def test_sleep_fetch(httpx_mock):
    """Test sleep data fetching."""
    # Mock API response
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/self/sleep/2026-01-09",
        json={
            "date": "2026-01-09",
            "sleep-score": 85,
            "total-sleep-time-seconds": 28800,
        }
    )

    async with PolarFlow(access_token="test_token") as client:
        sleep = await client.sleep.get(user_id="self", date="2026-01-09")
        assert sleep.sleep_score == 85
```

## Performance Tips

1. **Use `since=` parameter** for incremental syncs instead of fetching all data
2. **Batch operations** with `asyncio.gather()` when fetching multiple endpoints
3. **Handle rate limits** proactively - don't retry immediately
4. **Cache token** in memory if making multiple client instances
5. **Use connection pooling** - the async context manager handles this automatically

## Security Best Practices

1. **Never hardcode tokens** - use environment variables or secure vaults
2. **Rotate tokens regularly** - re-authenticate periodically
3. **Store tokens securely** - use proper file permissions (600)
4. **Don't log tokens** - redact sensitive data from logs
5. **Use HTTPS only** - the client enforces this by default
