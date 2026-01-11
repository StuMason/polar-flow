# Quick Start

Get up and running with polar-flow in 5 minutes.

## Installation

```bash
pip install polar-flow-api
```

## 1. Get Access Token

First, you need to authenticate with the Polar API to get an access token.

### Option A: CLI Authentication (Recommended)

The easiest way is to use the built-in CLI tool:

```bash
# Set your Polar API credentials
export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"

# Run interactive OAuth flow
polar-flow auth
```

This opens your browser, handles the OAuth callback, and saves the token to `~/.polar-flow/token`.

### Option B: Manual OAuth Flow

```python
from polar_flow.auth import OAuth2Handler
import asyncio

async def main():
    oauth = OAuth2Handler(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="http://localhost:8888/callback"
    )

    # Get authorization URL
    auth_url = oauth.get_authorization_url()
    print(f"Visit: {auth_url}")

    # After user authorizes, exchange code for token
    code = input("Enter authorization code: ")
    token = await oauth.exchange_code(code)
    print(f"Access token: {token.access_token}")

asyncio.run(main())
```

## 2. Use the Client

### Basic Usage

```python
import asyncio
from polar_flow import PolarFlow

async def main():
    async with PolarFlow(access_token="your_token") as client:
        # Get sleep data (no user_id needed)
        sleep_data = await client.sleep.list(days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100 ({night.total_sleep_hours:.1f}h)")

asyncio.run(main())
```

### Load Token from File

If you used the CLI authentication, load the token from the saved file:

```python
from polar_flow import PolarFlow, load_token_from_file
import asyncio

async def main():
    token = load_token_from_file()  # Reads ~/.polar-flow/token

    async with PolarFlow(access_token=token) as client:
        sleep_data = await client.sleep.list(days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100")

asyncio.run(main())
```

## 3. Explore Endpoints

### Sleep Data

```python
async with PolarFlow(access_token=token) as client:
    # List sleep data (last 7 days)
    sleep_list = await client.sleep.list(days=7)
    for night in sleep_list:
        print(f"{night.date}: score {night.sleep_score}")
        print(f"  Total: {night.total_sleep_hours:.1f}h")
        print(f"  Deep: {night.deep_sleep_seconds / 3600:.1f}h")
```

### Nightly Recharge (HRV)

```python
async with PolarFlow(access_token=token) as client:
    recharge = await client.recharge.list(days=7)
    for r in recharge:
        print(f"{r.date}: ANS {r.ans_charge}, HRV {r.hrv_avg}ms")
```

### Exercises

```python
async with PolarFlow(access_token=token) as client:
    # List exercises (last 30 days)
    exercises = await client.exercises.list()
    for ex in exercises:
        print(f"{ex.start_time}: {ex.sport}")
        print(f"  Duration: {ex.duration_minutes:.0f} min")
        print(f"  Calories: {ex.calories}")

    # Get detailed exercise with samples
    if exercises:
        samples = await client.exercises.get_samples(exercises[0].id)
```

### Activity Data

```python
async with PolarFlow(access_token=token) as client:
    activities = await client.activity.list(days=7)
    for a in activities:
        print(f"{a.date}: {a.steps} steps, {a.calories} cal")
```

### Cardio Load

```python
async with PolarFlow(access_token=token) as client:
    cardio = await client.cardio_load.list(days=7)
    for c in cardio:
        print(f"{c.date}: strain {c.strain}, tolerance {c.tolerance}")
        print(f"  Load ratio: {c.cardio_load_ratio:.2f}")
```

### SleepWise Alertness

```python
async with PolarFlow(access_token=token) as client:
    alertness = await client.sleepwise_alertness.list(days=3)
    for a in alertness:
        print(f"Grade: {a.grade}/5 ({a.grade_classification})")
```

### Biosensing (SpO2, ECG, Temperature)

Requires a compatible device (e.g., Vantage V3 with Elixir sensor):

```python
async with PolarFlow(access_token=token) as client:
    # Blood oxygen
    spo2 = await client.biosensing.get_spo2()
    for s in spo2:
        print(f"SpO2: {s.blood_oxygen_percent}% ({s.spo2_class})")

    # ECG
    ecg = await client.biosensing.get_ecg()
    for e in ecg:
        print(f"ECG: HR {e.average_heart_rate_bpm}, HRV {e.heart_rate_variability_ms}ms")

    # Body temperature
    body_temp = await client.biosensing.get_body_temperature()
    for t in body_temp:
        print(f"Temp: {t.avg_temperature:.1f}°C")

    # Skin temperature
    skin_temp = await client.biosensing.get_skin_temperature()
    for t in skin_temp:
        print(f"Skin: {t.sleep_time_skin_temperature_celsius:.1f}°C")
```

## 4. Error Handling

```python
from polar_flow import PolarFlow, NotFoundError, RateLimitError
import asyncio

async with PolarFlow(access_token=token) as client:
    try:
        sleep = await client.sleep.list(days=7)
    except NotFoundError:
        print("No sleep data found")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
```

## Next Steps

- Read the [Error Handling](error-handling.md) guide for robust error handling
- Explore the [API Reference](api/client.md) for complete documentation
- Check [Advanced Usage](advanced.md) for patterns like incremental sync and bulk fetching
