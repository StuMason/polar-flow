# polar-flow

Modern async Python client for Polar AccessLink API.

## Features

- Async-first with httpx
- Full type safety with Pydantic 2 and mypy strict mode
- Python 3.11+ with modern syntax
- Complete V3 API coverage (14 endpoints)
- 90%+ test coverage

## Installation

```bash
pip install polar-flow-api
```

## Quick Example

```python
import asyncio
from polar_flow import PolarFlow

async def main():
    async with PolarFlow(access_token="your_token") as client:
        # Get last 7 days of sleep
        sleep_data = await client.sleep.list(days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100")

asyncio.run(main())
```

## API Coverage

Complete Polar AccessLink V3 API implementation:

### Core Endpoints
- **Sleep** - Sleep tracking data (score, stages, duration)
- **Nightly Recharge** - Recovery metrics (ANS charge, HRV, breathing rate)
- **Activity** - Daily activity (steps, calories, distance, active time)
- **Exercises** - Workout data with samples, zones, TCX/GPX export

### Advanced Analytics
- **Cardio Load** - Training load, strain, tolerance
- **SleepWise Alertness** - Hourly alertness predictions
- **SleepWise Circadian Bedtime** - Optimal sleep timing recommendations
- **Activity Samples** - Minute-by-minute activity data
- **Continuous Heart Rate** - Daily HR summaries

### Biosensing (v1.4.0+)
- **SpO2** - Blood oxygen measurements
- **ECG** - Electrocardiogram data with waveforms
- **Body Temperature** - Continuous temperature monitoring
- **Skin Temperature** - Nightly skin temperature

### Account Management
- **Users** - Register, get, delete users
- **Physical Info** - Body metrics (height, weight, etc.)

### Utilities
- OAuth2 authentication with HTTP Basic Auth
- CLI authentication tool (`polar-flow auth`)

All endpoints tested and validated against real Polar API.

## Links

- [GitHub Repository](https://github.com/StuMason/polar-flow)
- [PyPI Package](https://pypi.org/project/polar-flow-api/)
- [Quick Start Guide](quickstart.md)
- [API Reference](api/client.md)
