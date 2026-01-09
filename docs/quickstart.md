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
        # Get sleep data
        sleep_data = await client.sleep.list(user_id="self", days=7)
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
        sleep_data = await client.sleep.list(user_id="self", days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100")

asyncio.run(main())
```

## 3. Explore Different Endpoints

### Sleep Data

```python
async with PolarFlow(access_token=token) as client:
    # Get sleep for specific date
    sleep = await client.sleep.get(user_id="self", date="2026-01-09")
    print(f"Sleep score: {sleep.sleep_score}")
    print(f"Total sleep: {sleep.total_sleep_hours}h")
    print(f"Deep sleep: {sleep.deep_sleep_seconds / 3600:.1f}h")

    # List sleep data for date range
    sleep_list = await client.sleep.list(user_id="self", days=7)
    for night in sleep_list:
        print(f"{night.date}: score {night.sleep_score}")
```

### Exercises

```python
async with PolarFlow(access_token=token) as client:
    # List exercises (last 30 days)
    exercises = await client.exercises.list()
    for ex in exercises:
        print(f"{ex.start_time}: {ex.sport}")
        print(f"  Duration: {ex.duration_minutes} min")
        print(f"  Calories: {ex.calories}")

    # Get detailed exercise with samples
    exercise = await client.exercises.get(exercise_id="123")
    samples = await client.exercises.get_samples(exercise_id="123")
```

### Activity Data

```python
async with PolarFlow(access_token=token) as client:
    # Get today's activity
    from datetime import date
    activity = await client.activity.get(date=str(date.today()))
    print(f"Steps: {activity.steps}")
    print(f"Calories: {activity.calories}")
    print(f"Distance: {activity.distance_km} km")
```

### Nightly Recharge

```python
async with PolarFlow(access_token=token) as client:
    # Get recharge data
    recharge = await client.recharge.list()
    for r in recharge:
        print(f"{r.date}: ANS charge {r.ans_charge}")
```

## Next Steps

- Read the [Error Handling](error-handling.md) guide to handle exceptions properly
- Explore the [API Reference](api/client.md) for complete documentation
- Check [Advanced Usage](advanced.md) for patterns like incremental sync and rate limit handling
