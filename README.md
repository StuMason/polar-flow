# polar-flow

[![CI](https://github.com/StuMason/polar-flow/actions/workflows/tests.yml/badge.svg)](https://github.com/StuMason/polar-flow/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/polar-flow-api.svg)](https://pypi.org/project/polar-flow-api/)
[![Python Version](https://img.shields.io/pypi/pyversions/polar-flow-api.svg)](https://pypi.org/project/polar-flow-api/)
[![License](https://img.shields.io/pypi/l/polar-flow-api.svg)](https://github.com/StuMason/polar-flow/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/StuMason/polar-flow/branch/main/graph/badge.svg)](https://codecov.io/gh/StuMason/polar-flow)

**Modern async Python client for Polar AccessLink API**

## Why This Exists

The existing `polar-accesslink` package is abandoned (v0.0.5, last updated 2020), has no type hints, no async support, uses raw dicts, and is missing most modern API endpoints. This is a complete rewrite with:

- **Async-first** with httpx (sync wrapper available)
- **Fully typed** with Pydantic 2 models and mypy strict mode
- **Modern Python** 3.11+ with latest syntax
- **Complete API coverage** including sleep, nightly recharge, activity, exercises
- **Developer-friendly** with rich error handling and helpful exceptions
- **Production-ready** with 80%+ test coverage and comprehensive CI/CD

## Quick Start

```bash
pip install polar-flow-api
```

```python
from polar_flow import PolarFlow
import asyncio

async def main():
    async with PolarFlow(access_token="your_token") as client:
        # Get sleep data for the last 7 days
        sleep_data = await client.sleep.list(days=7)
        for night in sleep_data:
            print(f"{night.date}: {night.sleep_score}/100")
            print(f"  Sleep: {night.total_sleep_hours:.1f}h")
            print(f"  HRV: {night.hrv_avg}ms")

asyncio.run(main())
```

## Features

### Complete API Coverage

- **Users** - Registration, info, deletion
- **Sleep** - Sleep tracking data, sleep-wise scores
- **Nightly Recharge** - ANS charge, HRV measurements
- **Daily Activity** - Steps, calories, activity zones
- **Exercises** - Training sessions, samples, HR zones, TCX/GPX exports
- **Physical Info** - Height, weight, max HR (transactional API)
- **Webhooks** - Signature verification for webhook events

### OAuth2 Made Simple

```python
from polar_flow.auth import OAuth2Handler

oauth = OAuth2Handler(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8000/callback"
)

# Step 1: Get authorization URL
auth_url = oauth.get_authorization_url()
# Redirect user to auth_url

# Step 2: Exchange code for token
token = await oauth.exchange_code(code="authorization_code")

# Step 3: Use with client
async with PolarFlow(access_token=token.access_token) as client:
    user = await client.users.me()
```

### Type-Safe Models

All responses are Pydantic models with full type hints:

```python
sleep = await client.sleep.get(date="2026-01-09")
print(sleep.sleep_score)           # int
print(sleep.total_sleep_hours)     # float (computed property)
print(sleep.sleep_efficiency)      # float (computed property)
print(sleep.hrv_avg)                # float | None
```

### Rich Error Handling

```python
from polar_flow.exceptions import RateLimitError, AuthenticationError

try:
    data = await client.sleep.list()
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except AuthenticationError:
    print("Invalid or expired token")
```

### CLI Tool

```bash
# Authenticate
polar-flow auth login

# Fetch data
polar-flow sleep --days 7
polar-flow recharge --today
polar-flow exercises --limit 10

# Export
polar-flow exercises export --format tcx --output ./exports/
```

## Installation

**Using pip:**
```bash
pip install polar-flow-api
```

**Using uv:**
```bash
uv add polar-flow
```

**Development:**
```bash
git clone https://github.com/StuMason/polar-flow.git
cd polar-flow
uv sync --dev
```

## Requirements

- Python 3.11+
- Polar AccessLink API credentials ([Get them here](https://admin.polaraccesslink.com))

## Documentation

See the [docs/standards](./docs/standards/) directory for:
- API reference
- Code examples
- Migration guide from `polar-accesslink`

## Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](./LICENSE)

## Links

- [Polar AccessLink API Docs](https://www.polar.com/accesslink-api/)
- [Polar Admin Console](https://admin.polaraccesslink.com)
- [Issues](https://github.com/StuMason/polar-flow/issues)
