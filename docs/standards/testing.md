# Testing Standards

## Test Structure

**Follow AAA pattern (Arrange, Act, Assert):**

```python
async def test_get_sleep_success():
    # Arrange
    client = PolarFlow(access_token="test_token")
    expected_score = 85

    # Act
    sleep = await client.sleep.get(date="2026-01-09")

    # Assert
    assert sleep.sleep_score == expected_score
    assert isinstance(sleep, SleepData)
```

## Test Naming

**Use descriptive test names:**

```python
# ✅ Good - describes what is being tested
def test_get_sleep_with_valid_date_returns_sleep_data():
    ...

def test_get_sleep_with_invalid_date_raises_validation_error():
    ...

def test_sleep_efficiency_calculation_with_interruptions():
    ...

# ❌ Bad - unclear what is being tested
def test_sleep():
    ...

def test_error():
    ...
```

## Mocking HTTP Requests

**Use pytest-httpx for mocking:**

```python
import pytest
from pytest_httpx import HTTPXMock

async def test_get_sleep_success(httpx_mock: HTTPXMock):
    """Test successful sleep data retrieval."""
    # Arrange
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123/sleep/2026-01-09",
        json={
            "polar_user": "123",
            "date": "2026-01-09",
            "sleep_score": 85,
            "light_sleep": 3600,
            "deep_sleep": 1800,
            "rem_sleep": 1200,
        },
        status_code=200,
    )

    # Act
    async with PolarFlow(access_token="test_token") as client:
        sleep = await client.sleep.get(user_id="123", date="2026-01-09")

    # Assert
    assert sleep.sleep_score == 85
    assert sleep.total_sleep_hours == pytest.approx(1.83, rel=0.01)
```

## Testing Exceptions

**Test that exceptions are raised correctly:**

```python
import pytest
from polar_flow.exceptions import NotFoundError, AuthenticationError

async def test_get_sleep_not_found_raises_exception(httpx_mock: HTTPXMock):
    """Test that 404 response raises NotFoundError."""
    # Arrange
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123/sleep/2026-01-09",
        status_code=404,
    )

    # Act & Assert
    async with PolarFlow(access_token="test_token") as client:
        with pytest.raises(NotFoundError, match="not found"):
            await client.sleep.get(user_id="123", date="2026-01-09")
```

## Testing Pydantic Models

**Test model validation and computed properties:**

```python
def test_sleep_data_model_validation():
    """Test SleepData model validates correctly."""
    # Arrange
    data = {
        "polar_user": "123",
        "date": "2026-01-09",
        "sleep_score": 85,
        "light_sleep": 3600,
        "deep_sleep": 1800,
        "rem_sleep": 1200,
        "sleep_start_time": "2026-01-08T22:00:00Z",
        "sleep_end_time": "2026-01-09T06:00:00Z",
    }

    # Act
    sleep = SleepData(**data)

    # Assert
    assert sleep.sleep_score == 85
    assert sleep.total_sleep_seconds == 6600  # 3600 + 1800 + 1200
    assert sleep.total_sleep_hours == pytest.approx(1.83, rel=0.01)


def test_sleep_data_invalid_score_raises_error():
    """Test that invalid sleep score raises validation error."""
    # Arrange
    data = {"sleep_score": 150}  # Invalid: > 100

    # Act & Assert
    with pytest.raises(ValidationError):
        SleepData(**data)
```

## Fixtures

**Use fixtures from conftest.py:**

```python
# In tests/conftest.py
@pytest.fixture
def mock_access_token() -> str:
    """Return a mock access token."""
    return "mock_token_12345"

@pytest.fixture
def mock_sleep_data() -> dict:
    """Return mock sleep data for testing."""
    return {
        "polar_user": "123",
        "date": "2026-01-09",
        "sleep_score": 85,
        "light_sleep": 3600,
        "deep_sleep": 1800,
        "rem_sleep": 1200,
    }

# In test file
def test_with_fixtures(mock_access_token: str, mock_sleep_data: dict):
    """Test using shared fixtures."""
    client = PolarFlow(access_token=mock_access_token)
    sleep = SleepData(**mock_sleep_data)
    assert sleep.sleep_score == 85
```

## Async Testing

**Use pytest-asyncio for async tests:**

```python
import pytest

# Mark async tests explicitly
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await some_async_function()
    assert result is not None

# Or configure pytest to detect async tests automatically (in pyproject.toml):
# [tool.pytest.ini_options]
# asyncio_mode = "auto"
```

## Parametrized Tests

**Use pytest.mark.parametrize for multiple test cases:**

```python
@pytest.mark.parametrize(
    "sleep_score,expected_quality",
    [
        (95, "Excellent"),
        (85, "Excellent"),
        (75, "Good"),
        (65, "Fair"),
        (45, "Poor"),
    ],
)
def test_sleep_quality_calculation(sleep_score: int, expected_quality: str):
    """Test sleep quality categorization."""
    sleep = SleepData(sleep_score=sleep_score, ...)
    assert sleep.get_sleep_quality() == expected_quality
```

## Coverage Requirements

**Maintain 80%+ test coverage:**

```bash
# Run tests with coverage report
uv run pytest --cov --cov-report=term --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

**Focus coverage on:**
- All public methods and functions
- Error handling paths
- Edge cases and validation
- Computed properties

**Coverage exclusions (acceptable):**
- Type checking blocks (`if TYPE_CHECKING:`)
- Abstract methods with `raise NotImplementedError`
- Defensive assertions that should never happen

## Test Organization

**Organize tests by module:**

```
tests/
├── conftest.py              # Shared fixtures
├── test_exceptions.py       # Exception tests
├── test_client.py           # Client tests
├── test_auth.py             # OAuth2 tests
├── models/
│   ├── test_sleep.py        # Sleep model tests
│   ├── test_exercise.py     # Exercise model tests
│   └── test_activity.py     # Activity model tests
└── endpoints/
    ├── test_sleep_endpoint.py
    └── test_exercise_endpoint.py
```

## Integration Tests

**Mark integration tests that hit real APIs:**

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("POLAR_API_TOKEN"), reason="Requires API token")
async def test_real_api_call():
    """Integration test using real Polar API."""
    token = os.getenv("POLAR_API_TOKEN")
    async with PolarFlow(access_token=token) as client:
        user = await client.users.me()
        assert user.polar_user_id is not None
```

Run integration tests separately:
```bash
# Skip integration tests (default)
uv run pytest

# Run only integration tests
uv run pytest -m integration
```

## Test Data

**Keep test data realistic:**

```python
# ✅ Good - realistic test data
def test_with_realistic_data():
    data = {
        "sleep_score": 82,
        "light_sleep": 3600,    # 1 hour
        "deep_sleep": 1800,     # 30 minutes
        "rem_sleep": 1200,      # 20 minutes
        "hrv_avg": 45.5,        # Realistic HRV
    }

# ❌ Bad - unrealistic test data
def test_with_bad_data():
    data = {
        "sleep_score": 999,
        "light_sleep": 1,
        "hrv_avg": -100,
    }
```
