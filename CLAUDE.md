# Claude Code Guide for polar-flow

This document helps AI assistants (Claude Code, GitHub Copilot, etc.) understand the project structure and make appropriate changes.

## Project Overview

`polar-flow` is a modern async Python client for the Polar AccessLink API. It replaces the abandoned `polar-accesslink` package with full type safety, async support, and Pydantic models.

## Tech Stack

- **Python**: 3.11+ (use modern syntax: `X | None`, not `Optional[X]`)
- **Package manager**: uv (not pip, not Poetry)
- **HTTP client**: httpx (async-first, NOT requests)
- **Validation**: Pydantic 2.x
- **CLI**: Typer + Rich
- **Testing**: pytest + pytest-asyncio + pytest-httpx
- **Linting**: Ruff (formatting + linting, NOT black/flake8/isort)
- **Type checking**: mypy in strict mode

## Project Structure

```
src/polar_flow/
├── __init__.py              # Package exports
├── exceptions.py            # Custom typed exceptions
├── client.py                # Main async client (when implemented)
├── client_sync.py           # Sync wrapper (when implemented)
├── auth.py                  # OAuth2 handler (when implemented)
├── models/                  # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── sleep.py
│   ├── exercise.py
│   ├── recharge.py
│   ├── activity.py
│   └── physical_info.py
├── endpoints/               # API endpoint handlers
│   ├── __init__.py
│   ├── base.py
│   ├── users.py
│   ├── sleep.py
│   ├── exercises.py
│   ├── recharge.py
│   └── activity.py
├── webhooks.py              # Webhook signature verification
└── cli.py                   # CLI tool

tests/
├── conftest.py              # Shared fixtures
├── test_exceptions.py
├── test_client.py
├── test_models.py
└── test_webhooks.py
```

## Code Style Rules

### 1. Type Hints (STRICT)
- ALL functions must have type hints for parameters and return values
- Use modern syntax: `str | None` not `Optional[str]`
- Use `from __future__ import annotations` if needed for forward references
- mypy strict mode must pass with ZERO errors

### 2. Imports
- Group imports: stdlib → third-party → local
- Use absolute imports, never relative
- Sort with ruff (isort rules)

### 3. Async/Await
- Primary API is async (httpx, not requests)
- Use `async with` for context managers
- All client methods are async: `async def get_sleep(...)`

### 4. Pydantic Models
- Use Pydantic 2.x syntax
- Add docstrings to all models and fields
- Use `Field()` for validation and descriptions
- Add computed properties with `@property` for derived values
- Example:
  ```python
  from pydantic import BaseModel, Field

  class SleepData(BaseModel):
      """Sleep tracking data for a single night."""

      sleep_score: int = Field(ge=0, le=100, description="Overall sleep quality score")
      light_sleep: int = Field(description="Light sleep duration in seconds")

      @property
      def total_sleep_hours(self) -> float:
          """Total sleep time in hours."""
          return self.total_sleep_seconds / 3600
  ```

### 5. Error Handling
- Never raise generic `Exception`
- Use typed custom exceptions from `exceptions.py`
- Include helpful context in error messages
- Handle HTTP status codes explicitly:
  - 401 → `AuthenticationError`
  - 404 → `NotFoundError`
  - 429 → `RateLimitError` (include retry_after)
  - 422 → `ValidationError`

### 6. Testing
- Minimum 80% coverage (enforced by pytest-cov)
- Use pytest-httpx to mock HTTP requests
- Test file naming: `test_<module>.py`
- Use fixtures from `conftest.py`
- Follow AAA pattern: Arrange, Act, Assert
- Example:
  ```python
  def test_sleep_model():
      # Arrange
      data = {"sleep_score": 85, "light_sleep": 3600}

      # Act
      sleep = SleepData(**data)

      # Assert
      assert sleep.sleep_score == 85
  ```

### 7. Documentation
- All public functions/classes need docstrings (Google style)
- Include type information in docstrings for clarity
- Document exceptions raised
- Example:
  ```python
  async def get_sleep(self, date: str) -> SleepData:
      """Fetch sleep data for a specific date.

      Args:
          date: Date in YYYY-MM-DD format

      Returns:
          Sleep data for the specified date

      Raises:
          NotFoundError: If no sleep data exists for the date
          AuthenticationError: If access token is invalid
      """
  ```

## Common Tasks

### Adding a New Endpoint

1. Create Pydantic model in `src/polar_flow/models/<resource>.py`
2. Create endpoint handler in `src/polar_flow/endpoints/<resource>.py`
3. Add to client in `src/polar_flow/client.py`
4. Write tests in `tests/test_<resource>.py`
5. Update exports in `src/polar_flow/__init__.py`

### Running Tests

```bash
# All tests with coverage
uv run pytest

# Watch mode
uv run pytest --watch

# Specific test file
uv run pytest tests/test_exceptions.py

# With verbose output
uv run pytest -v
```

### Type Checking

```bash
# Run mypy (must pass with zero errors)
uv run mypy src/polar_flow

# Check specific file
uv run mypy src/polar_flow/client.py
```

### Linting and Formatting

```bash
# Format code (run automatically in pre-commit)
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Building the Package

```bash
# Build wheel
uv build

# Install locally
uv pip install -e .
```

## Publishing Process

Automatic publishing on version bump to main:

1. Update version in `pyproject.toml`
2. Update version in `src/polar_flow/__init__.py`
3. Add entry to `CHANGELOG.md`
4. Commit and push to main
5. GitHub Actions auto-publishes to PyPI

## CI/CD Workflows

- **tests.yml** - Runs on all PRs/pushes to main (Python 3.11, 3.12, 3.13)
- **lint.yml** - Enforces Ruff formatting and linting
- **publish.yml** - Auto-publishes to PyPI when version changes
- **claude-code-review.yml** - AI code review on new PRs
- **dependabot-automerge.yml** - Auto-merges minor/patch dependency updates

## API Reference

Base URL: `https://www.polaraccesslink.com/v3`

All requests require: `Authorization: Bearer {access_token}`

### Key Endpoints (to be implemented)

- `GET /v3/users/{user-id}` - User info
- `GET /v3/users/{user-id}/sleep` - List sleep data
- `GET /v3/users/{user-id}/nightly-recharge` - Nightly recharge data
- `GET /v3/users/{user-id}/activity` - Daily activity
- `GET /v3/exercises` - List exercises (last 30 days)
- `GET /v3/exercises/{id}/samples` - Exercise samples

Rate limits are enforced (check `X-RateLimit-*` headers).

## Important Notes

- Polar API only returns last 30 days of exercises
- Some endpoints are transactional (data deleted after retrieval)
- Sleep and recharge are non-transactional (can be re-fetched)
- TCX/GPX exports return XML, not JSON
- Webhook payloads are signed with HMAC SHA-256

## Version Management

Version is defined in two places (must be kept in sync):
1. `pyproject.toml` → `version = "x.y.z"`
2. `src/polar_flow/__init__.py` → `__version__ = "x.y.z"`

Use semantic versioning (MAJOR.MINOR.PATCH).
