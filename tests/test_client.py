"""Tests for HTTP client."""

import pytest
from pytest_httpx import HTTPXMock

from polar_flow import PolarFlow
from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    PolarFlowError,
    RateLimitError,
    ValidationError,
)


def test_client_initialization_valid_token() -> None:
    """Test client initializes with valid token."""
    client = PolarFlow(access_token="valid_token_1234567890")
    assert client.access_token == "valid_token_1234567890"
    assert client.base_url == "https://www.polaraccesslink.com"


def test_client_initialization_custom_base_url() -> None:
    """Test client accepts custom base URL."""
    client = PolarFlow(access_token="test_token_1234567890", base_url="https://custom.api.com")
    assert client.base_url == "https://custom.api.com"


def test_client_initialization_strips_token() -> None:
    """Test that access token is stripped of whitespace."""
    client = PolarFlow(access_token="  test_token_1234567890  ")
    assert client.access_token == "test_token_1234567890"


def test_client_initialization_empty_token_raises_error() -> None:
    """Test that empty token raises ValueError."""
    with pytest.raises(ValueError, match="access_token is required"):
        PolarFlow(access_token="")

    with pytest.raises(ValueError, match="access_token is required"):
        PolarFlow(access_token="   ")


def test_client_initialization_short_token_raises_error() -> None:
    """Test that suspiciously short token raises ValueError."""
    with pytest.raises(ValueError, match="appears to be invalid"):
        PolarFlow(access_token="short")


@pytest.mark.asyncio
async def test_client_context_manager() -> None:
    """Test client works as async context manager."""
    async with PolarFlow(access_token="test_token_1234567890") as client:
        assert client._client is not None

    # Client should be closed after exiting context
    assert client._client is None


@pytest.mark.asyncio
async def test_request_without_context_manager_raises_error() -> None:
    """Test that making request without context manager raises RuntimeError."""
    client = PolarFlow(access_token="test_token_1234567890")

    with pytest.raises(RuntimeError, match="Client not initialized"):
        await client._request("GET", "/v3/users/123")


@pytest.mark.asyncio
async def test_request_adds_v3_prefix(httpx_mock: HTTPXMock) -> None:
    """Test that /v3 prefix is added to paths automatically."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123", json={"user_id": "123"}
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        await client._request("GET", "/users/123")

    # Verify the request was made with /v3 prefix
    request = httpx_mock.get_requests()[0]
    assert "/v3/users/123" in str(request.url)


@pytest.mark.asyncio
async def test_request_authentication_header(httpx_mock: HTTPXMock) -> None:
    """Test that Authorization header is set correctly."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123", json={"user_id": "123"}
    )

    async with PolarFlow(access_token="mytest_token_1234567890") as client:
        await client._request("GET", "/users/123")

    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer mytest_token_1234567890"


@pytest.mark.asyncio
async def test_request_401_raises_authentication_error(httpx_mock: HTTPXMock) -> None:
    """Test that 401 response raises AuthenticationError."""
    httpx_mock.add_response(url="https://www.polaraccesslink.com/v3/users/123", status_code=401)

    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(AuthenticationError, match="Invalid or expired"):
            await client._request("GET", "/users/123")


@pytest.mark.asyncio
async def test_request_404_raises_not_found_error(httpx_mock: HTTPXMock) -> None:
    """Test that 404 response raises NotFoundError."""
    httpx_mock.add_response(url="https://www.polaraccesslink.com/v3/users/999", status_code=404)

    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(NotFoundError, match="not found"):
            await client._request("GET", "/users/999")


@pytest.mark.asyncio
async def test_request_429_raises_rate_limit_error(httpx_mock: HTTPXMock) -> None:
    """Test that 429 response raises RateLimitError with retry_after."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123",
        status_code=429,
        headers={"Retry-After": "120"},
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(RateLimitError, match="Rate limit exceeded") as exc_info:
            await client._request("GET", "/users/123")

        assert exc_info.value.retry_after == 120


@pytest.mark.asyncio
async def test_request_422_raises_validation_error(httpx_mock: HTTPXMock) -> None:
    """Test that 422 response raises ValidationError."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123",
        status_code=422,
        json={"message": "Invalid date format"},
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(ValidationError, match="Invalid date format"):
            await client._request("GET", "/users/123")


@pytest.mark.asyncio
async def test_request_500_raises_polar_flow_error(httpx_mock: HTTPXMock) -> None:
    """Test that 500 response raises PolarFlowError."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123",
        status_code=500,
        text="Internal server error",
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(PolarFlowError, match="API error 500"):
            await client._request("GET", "/users/123")


@pytest.mark.asyncio
async def test_request_returns_json_dict(httpx_mock: HTTPXMock) -> None:
    """Test that successful request returns JSON dict."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123",
        json={"user_id": "123", "name": "Test User"},
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        result = await client._request("GET", "/users/123")

    assert result == {"user_id": "123", "name": "Test User"}


@pytest.mark.asyncio
async def test_sleep_endpoint_accessible(httpx_mock: HTTPXMock) -> None:
    """Test that sleep endpoint is accessible from client."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123/sleep/2026-01-09",
        json={
            "polar_user": "123",
            "date": "2026-01-09",
            "sleep_start_time": "2026-01-08T22:00:00Z",
            "sleep_end_time": "2026-01-09T06:00:00Z",
            "device_id": "DEV123",
            "continuity": 3.0,
            "continuity_class": 3,
            "light_sleep": 14400,
            "deep_sleep": 7200,
            "rem_sleep": 3600,
            "unrecognized_sleep_stage": 0,
            "sleep_score": 85,
            "total_interruption_duration": 600,
            "sleep_charge": 80,
            "sleep_goal": 28800,
            "sleep_rating": 4,
            "short_interruption_duration": 300,
            "long_interruption_duration": 300,
            "sleep_cycles": 5,
            "group_duration_score": 85.0,
            "group_solidity_score": 80.0,
            "group_regeneration_score": 90.0,
        },
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        assert hasattr(client, "sleep")
        sleep = await client.sleep.get(user_id="123", date="2026-01-09")
        assert sleep.sleep_score == 85
