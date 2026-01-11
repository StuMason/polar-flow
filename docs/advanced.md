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
        new_sleep_data = await client.sleep.list(since=last_sync_date)

        print(f"Fetched {len(new_sleep_data)} new sleep records")

        for sleep in new_sleep_data:
            await store_sleep_data(sleep)

        return str(date.today())

# Run sync
last_sync = "2026-01-01"
new_last_sync = await sync_sleep_data(last_sync)
```

## Bulk Data Fetching

Fetch all data types efficiently using parallel requests:

```python
import asyncio
from polar_flow import PolarFlow

async def fetch_all_data(client: PolarFlow):
    """Fetch all available data in one session."""

    # Fetch in parallel using asyncio.gather
    results = await asyncio.gather(
        client.sleep.list(days=28),
        client.recharge.list(days=28),
        client.activity.list(days=28),
        client.exercises.list(),
        client.cardio_load.list(days=28),
        return_exceptions=True  # Don't fail if one endpoint fails
    )

    sleep, recharge, activity, exercises, cardio = results

    # Handle potential errors
    return {
        "sleep": sleep if not isinstance(sleep, Exception) else [],
        "recharge": recharge if not isinstance(recharge, Exception) else [],
        "activity": activity if not isinstance(activity, Exception) else [],
        "exercises": exercises if not isinstance(exercises, Exception) else [],
        "cardio_load": cardio if not isinstance(cardio, Exception) else [],
    }
```

## Rate Limit Handling

Implement sophisticated rate limit handling for production:

```python
import asyncio
from polar_flow import PolarFlow, RateLimitError

class RateLimitedClient:
    def __init__(self, client: PolarFlow):
        self.client = client
        self.max_retries = 3

    async def fetch_with_backoff(self, coro):
        """Execute coroutine with exponential backoff on rate limits."""
        for attempt in range(self.max_retries):
            try:
                return await coro
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = e.retry_after * (2 ** attempt)
                print(f"Rate limited. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)

# Use it
async with PolarFlow(access_token=token) as client:
    rl_client = RateLimitedClient(client)
    sleep_data = await rl_client.fetch_with_backoff(
        client.sleep.list(days=28)
    )
```

## Biosensing Data

Fetch and process biosensing data (requires compatible device):

```python
from polar_flow import PolarFlow

async def fetch_biosensing_data(client: PolarFlow):
    """Fetch all biosensing metrics."""

    # SpO2 - Blood oxygen
    spo2_data = await client.biosensing.get_spo2()
    for s in spo2_data:
        print(f"SpO2: {s.blood_oxygen_percent}% at {s.test_time}")
        print(f"  Class: {s.spo2_class}")
        print(f"  HR: {s.average_heart_rate_bpm} bpm")
        print(f"  HRV: {s.heart_rate_variability_ms} ms")

    # ECG - Electrocardiogram
    ecg_data = await client.biosensing.get_ecg()
    for e in ecg_data:
        print(f"ECG at {e.test_time}")
        print(f"  HR: {e.average_heart_rate_bpm} bpm")
        print(f"  HRV: {e.heart_rate_variability_ms} ms ({e.heart_rate_variability_level})")
        print(f"  RRI: {e.rri_ms} ms")
        if e.samples:
            print(f"  Samples: {len(e.samples)} waveform points")

    # Body temperature
    body_temp = await client.biosensing.get_body_temperature()
    for t in body_temp:
        print(f"Body temp: {t.start_time} - {t.end_time}")
        print(f"  Avg: {t.avg_temperature:.1f}°C")
        print(f"  Min: {t.min_temperature:.1f}°C")
        print(f"  Max: {t.max_temperature:.1f}°C")

    # Skin temperature (nightly)
    skin_temp = await client.biosensing.get_skin_temperature()
    for t in skin_temp:
        print(f"Skin temp ({t.sleep_date}): {t.sleep_time_skin_temperature_celsius:.1f}°C")
        if t.deviation_from_baseline_celsius:
            print(f"  Deviation: {t.deviation_from_baseline_celsius:+.1f}°C")
```

## Data Export Patterns

### Export to JSON

```python
import json
from pathlib import Path
from polar_flow import PolarFlow

async def export_to_json(client: PolarFlow, output_path: Path):
    """Export all data to JSON file."""
    sleep_data = await client.sleep.list(days=28)

    # Convert Pydantic models to dicts
    data = [sleep.model_dump() for sleep in sleep_data]

    output_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Exported {len(data)} records to {output_path}")
```

### Export to CSV

```python
import csv
from pathlib import Path
from polar_flow import PolarFlow

async def export_exercises_to_csv(client: PolarFlow, output_path: Path):
    """Export exercises to CSV file."""
    exercises = await client.exercises.list()

    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Date", "Sport", "Duration (min)",
            "Calories", "Distance (km)", "Avg HR"
        ])

        for ex in exercises:
            writer.writerow([
                ex.start_time.date() if ex.start_time else "",
                ex.sport,
                ex.duration_minutes or 0,
                ex.calories or 0,
                ex.distance_km or 0,
                ex.average_heart_rate or 0,
            ])

    print(f"Exported {len(exercises)} exercises to {output_path}")
```

## Scheduled Sync Jobs

Run periodic syncs with APScheduler:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from polar_flow import PolarFlow, load_token_from_file
import asyncio

async def sync_job():
    """Sync all data from Polar API."""
    token = load_token_from_file()

    async with PolarFlow(access_token=token) as client:
        sleep = await client.sleep.list(days=7)
        print(f"Synced {len(sleep)} sleep records")

        recharge = await client.recharge.list(days=7)
        print(f"Synced {len(recharge)} recharge records")

        cardio = await client.cardio_load.list(days=7)
        print(f"Synced {len(cardio)} cardio load records")

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
from polar_flow import PolarFlow, load_token_from_file

async def store_sleep_data(db_path: str):
    """Fetch and store sleep data in SQLite."""
    token = load_token_from_file()

    async with aiosqlite.connect(db_path) as db:
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
            sleep_data = await client.sleep.list(days=28)

            for sleep in sleep_data:
                await db.execute("""
                    INSERT OR REPLACE INTO sleep VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    sleep.date,
                    sleep.sleep_score,
                    sleep.total_sleep_seconds,
                    sleep.deep_sleep_seconds,
                    sleep.rem_sleep_seconds,
                    getattr(sleep, 'hrv_avg', None),
                ))

        await db.commit()
        print(f"Stored {len(sleep_data)} sleep records")
```

## Error Recovery

Implement robust error recovery:

```python
from polar_flow import PolarFlow, PolarFlowError, NotFoundError
import logging

logger = logging.getLogger(__name__)

async def sync_with_recovery(client: PolarFlow, dates: list[str]):
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

@pytest.mark.asyncio
async def test_sleep_fetch(httpx_mock):
    """Test sleep data fetching."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/sleep",
        json={
            "nights": [{
                "date": "2026-01-09",
                "sleep_score": 85,
                "total_sleep_seconds": 28800,
            }]
        }
    )

    async with PolarFlow(access_token="test_token") as client:
        sleep = await client.sleep.list(days=1)
        assert len(sleep) == 1
        assert sleep[0].sleep_score == 85
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

## Device Compatibility

Not all Polar devices support all endpoints:

| Feature | Vantage V3 | Vantage V2 | Grit X Pro | Ignite 3 | Pacer Pro |
|---------|------------|------------|------------|----------|-----------|
| Sleep | ✅ | ✅ | ✅ | ✅ | ✅ |
| Recharge | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cardio Load | ✅ | ✅ | ✅ | ✅ | ✅ |
| SpO2 | ✅ | ❌ | ❌ | ❌ | ❌ |
| ECG | ✅ | ❌ | ❌ | ❌ | ❌ |
| Temperature | ✅ | ❌ | ❌ | ❌ | ❌ |

Biosensing features (SpO2, ECG, Temperature) require the Elixir sensor platform found in Vantage V3.
