# polar-flow

[![CI](https://github.com/StuMason/polar-flow/actions/workflows/tests.yml/badge.svg)](https://github.com/StuMason/polar-flow/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/polar-flow-api.svg)](https://pypi.org/project/polar-flow-api/)
[![Python Version](https://img.shields.io/pypi/pyversions/polar-flow-api.svg)](https://pypi.org/project/polar-flow-api/)
[![License](https://img.shields.io/pypi/l/polar-flow-api.svg)](https://github.com/StuMason/polar-flow/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/StuMason/polar-flow/branch/main/graph/badge.svg)](https://codecov.io/gh/StuMason/polar-flow)

Modern async Python client for Polar AccessLink API.

## Documentation

Full documentation available at **[stumason.github.io/polar-flow](https://stumason.github.io/polar-flow/)**

## Features

- Async-first with httpx
- Full type safety with Pydantic 2 and mypy strict mode
- Python 3.11+ with modern syntax
- Complete V3 API coverage
- 90%+ test coverage

## API Coverage

**Complete Polar AccessLink V3 API implementation:**
- OAuth2 authentication with HTTP Basic Auth
- Sleep endpoint (get/list sleep data)
- Exercises endpoint (list/get/samples/zones/export TCX/GPX)
- Activity endpoint (daily activity with steps/zones/inactivity)
- Nightly Recharge endpoint (ANS charge, HRV, breathing rate)
- Users endpoint (register/get/delete)
- Physical Information endpoint (transaction-based body metrics)
- CLI authentication tool

All endpoints tested and validated against real Polar API.

## Install

```bash
pip install polar-flow-api
```

## Quick Start

### 1. Get Access Token

```bash
# Set your Polar API credentials
export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"

# Run interactive OAuth flow
polar-flow auth
```

This opens your browser, handles the OAuth callback, and saves the token to `~/.polar-flow/token`.

### 2. Use the Client

```python
import asyncio
from polar_flow import PolarFlow

async def main():
    async with PolarFlow(access_token="your_token") as client:
        # Get sleep data
        sleep_data = await client.sleep.list(user_id="self", days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100 ({night.total_sleep_hours:.1f}h)")

        # Get exercises
        exercises = await client.exercises.list()
        for ex in exercises:
            print(f"{ex.start_time}: {ex.sport} - {ex.duration_minutes}min, {ex.calories}cal")

asyncio.run(main())
```

## OAuth2 Flow

```python
from polar_flow.auth import OAuth2Handler

oauth = OAuth2Handler(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8888/callback"
)

# Get authorization URL
auth_url = oauth.get_authorization_url()
print(f"Visit: {auth_url}")

# After user authorizes, exchange code for token
token = await oauth.exchange_code(code="authorization_code")
print(f"Access token: {token.access_token}")
```

## Sleep API

```python
# Get sleep for specific date
sleep = await client.sleep.get(user_id="self", date="2026-01-09")
print(f"Sleep score: {sleep.sleep_score}")
print(f"Total sleep: {sleep.total_sleep_hours}h")
print(f"Deep sleep: {sleep.deep_sleep_seconds / 3600:.1f}h")
print(f"REM sleep: {sleep.rem_sleep_seconds / 3600:.1f}h")
print(f"HRV average: {sleep.hrv_avg}ms")

# List sleep data for date range
sleep_list = await client.sleep.list(user_id="self", days=7)
for night in sleep_list:
    print(f"{night.date}: score {night.sleep_score}, {night.total_sleep_hours:.1f}h")
```

## Exercises API

```python
# List exercises (last 30 days)
exercises = await client.exercises.list()
for ex in exercises:
    print(f"{ex.start_time}: {ex.sport}")
    print(f"  Duration: {ex.duration_minutes} min")
    print(f"  Calories: {ex.calories}")
    if ex.distance_km:
        print(f"  Distance: {ex.distance_km} km")
    if ex.average_heart_rate:
        print(f"  Avg HR: {ex.average_heart_rate} bpm")

# Get detailed exercise
exercise = await client.exercises.get(exercise_id="123")

# Get exercise samples (HR, speed, cadence, altitude)
samples = await client.exercises.get_samples(exercise_id="123")
hr_sample = samples.get_sample_by_type("HEARTRATE")
if hr_sample:
    print(f"HR values: {hr_sample.values[:10]}")  # First 10 values

# Get heart rate zones
zones = await client.exercises.get_zones(exercise_id="123")
for zone in zones.zones:
    print(f"Zone {zone.index}: {zone.lower_limit}-{zone.upper_limit} bpm, {zone.in_zone_minutes} min")

# Export to TCX/GPX
tcx_xml = await client.exercises.export_tcx(exercise_id="123")
gpx_xml = await client.exercises.export_gpx(exercise_id="123")
```

## Error Handling

```python
from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

try:
    data = await client.sleep.get(user_id="self", date="2026-01-09")
except AuthenticationError:
    print("Invalid or expired token")
except NotFoundError:
    print("No data for this date")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e}")
```

## CLI Commands

```bash
# Authenticate (opens browser)
polar-flow auth

# Authenticate with explicit credentials
polar-flow auth --client-id YOUR_ID --client-secret YOUR_SECRET

# Show version
polar-flow version
```

## Development

```bash
git clone https://github.com/StuMason/polar-flow.git
cd polar-flow
uv sync --all-extras
uv run pytest
```

## Requirements

- Python 3.11+
- Polar AccessLink API credentials from [admin.polaraccesslink.com](https://admin.polaraccesslink.com)

## Links

- [Polar AccessLink API Docs](https://www.polar.com/accesslink-api/)
- [Issues](https://github.com/StuMason/polar-flow/issues)

## License

MIT
