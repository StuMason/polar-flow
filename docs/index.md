# polar-flow

Modern async Python client for Polar AccessLink API.

## Features

- Async-first with httpx
- Full type safety with Pydantic 2 and mypy strict mode
- Python 3.11+ with modern syntax
- Complete V3 API coverage
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
        sleep_data = await client.sleep.list(user_id="self", days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100")

asyncio.run(main())
```

## API Coverage

Complete Polar AccessLink V3 API implementation:

- OAuth2 authentication with HTTP Basic Auth
- Sleep endpoint (get/list sleep data)
- Exercises endpoint (list/get/samples/zones/export TCX/GPX)
- Activity endpoint (daily activity with steps/zones/inactivity)
- Nightly Recharge endpoint (ANS charge, HRV, breathing rate)
- Users endpoint (register/get/delete)
- Physical Information endpoint (transaction-based body metrics)
- CLI authentication tool

All endpoints tested and validated against real Polar API.

## Links

- [GitHub Repository](https://github.com/StuMason/polar-flow)
- [PyPI Package](https://pypi.org/project/polar-flow-api/)
- [Quick Start Guide](quickstart.md)
- [API Reference](api/client.md)
