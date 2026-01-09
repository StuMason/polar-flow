"""Tests for sleep endpoint."""

from datetime import date

import pytest
from pytest_httpx import HTTPXMock

from polar_flow import PolarFlow
from polar_flow.models.sleep import SleepData


@pytest.fixture
def mock_sleep_response() -> dict:
    """Return mock sleep API response."""
    return {
        "polar_user": "12345678",
        "date": "2026-01-09",
        "sleep_start_time": "2026-01-08T22:00:00Z",
        "sleep_end_time": "2026-01-09T06:00:00Z",
        "device_id": "ABCD1234",
        "continuity": 3.5,
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
        "group_duration_score": 85.5,
        "group_solidity_score": 80.0,
        "group_regeneration_score": 90.0,
        "heart_rate_avg": 55,
        "hrv_avg": 45.5,
    }


@pytest.mark.asyncio
async def test_sleep_get_with_string_date(httpx_mock: HTTPXMock, mock_sleep_response: dict) -> None:
    """Test getting sleep data with string date."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/12345678/sleep/2026-01-09",
        json=mock_sleep_response,
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        sleep = await client.sleep.get(user_id="12345678", date="2026-01-09")

    assert isinstance(sleep, SleepData)
    assert sleep.polar_user == "12345678"
    assert sleep.date == date(2026, 1, 9)
    assert sleep.sleep_score == 85
    assert sleep.total_sleep_hours == 7.0


@pytest.mark.asyncio
async def test_sleep_get_with_date_object(httpx_mock: HTTPXMock, mock_sleep_response: dict) -> None:
    """Test getting sleep data with date object."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/12345678/sleep/2026-01-09",
        json=mock_sleep_response,
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        sleep = await client.sleep.get(user_id="12345678", date=date(2026, 1, 9))

    assert isinstance(sleep, SleepData)
    assert sleep.sleep_score == 85


@pytest.mark.asyncio
async def test_sleep_get_computed_properties(
    httpx_mock: HTTPXMock, mock_sleep_response: dict
) -> None:
    """Test that sleep data includes computed properties."""
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/12345678/sleep/2026-01-09",
        json=mock_sleep_response,
    )

    async with PolarFlow(access_token="test_token_1234567890") as client:
        sleep = await client.sleep.get(user_id="12345678", date="2026-01-09")

    # Check computed properties
    assert sleep.total_sleep_seconds == 25200  # 14400 + 7200 + 3600
    assert sleep.total_sleep_hours == 7.0
    assert sleep.time_in_bed_hours == 8.0
    assert sleep.sleep_efficiency == 87.5  # 7h sleep / 8h in bed


@pytest.mark.asyncio
async def test_sleep_list_default_days(httpx_mock: HTTPXMock) -> None:
    """Test listing sleep data for default 7 days."""
    # Mock responses for last 7 days
    for i in range(7):
        day = date.today() - __import__("datetime").timedelta(days=i)
        httpx_mock.add_response(
            url=f"https://www.polaraccesslink.com/v3/users/123/sleep/{day.isoformat()}",
            json={
                "polar_user": "123",
                "date": day.isoformat(),
                "sleep_start_time": "2026-01-08T22:00:00Z",
                "sleep_end_time": "2026-01-09T06:00:00Z",
                "device_id": "DEV123",
                "continuity": 3.0,
                "continuity_class": 3,
                "light_sleep": 14400,
                "deep_sleep": 7200,
                "rem_sleep": 3600,
                "unrecognized_sleep_stage": 0,
                "sleep_score": 80 + i,  # Vary scores
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
        sleep_list = await client.sleep.list(user_id="123", days=7)

    assert len(sleep_list) == 7
    assert all(isinstance(s, SleepData) for s in sleep_list)

    # Should be sorted by date, most recent first
    for i in range(len(sleep_list) - 1):
        assert sleep_list[i].date >= sleep_list[i + 1].date


@pytest.mark.asyncio
async def test_sleep_list_custom_days(httpx_mock: HTTPXMock) -> None:
    """Test listing sleep data for custom number of days."""
    # Mock responses for 3 days
    for i in range(3):
        day = date.today() - __import__("datetime").timedelta(days=i)
        httpx_mock.add_response(
            url=f"https://www.polaraccesslink.com/v3/users/123/sleep/{day.isoformat()}",
            json={
                "polar_user": "123",
                "date": day.isoformat(),
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
        sleep_list = await client.sleep.list(user_id="123", days=3)

    assert len(sleep_list) == 3


@pytest.mark.asyncio
async def test_sleep_list_invalid_days_raises_error() -> None:
    """Test that invalid days parameter raises ValueError."""
    async with PolarFlow(access_token="test_token_1234567890") as client:
        with pytest.raises(ValueError, match="days must be between 1 and 30"):
            await client.sleep.list(user_id="123", days=0)

        with pytest.raises(ValueError, match="days must be between 1 and 30"):
            await client.sleep.list(user_id="123", days=31)


@pytest.mark.asyncio
async def test_sleep_list_skips_missing_dates(httpx_mock: HTTPXMock) -> None:
    """Test that list() skips dates with no data (404 errors)."""
    # Mock 3 days: first exists, second 404, third exists
    day0 = date.today()
    day1 = date.today() - __import__("datetime").timedelta(days=1)
    day2 = date.today() - __import__("datetime").timedelta(days=2)

    httpx_mock.add_response(
        url=f"https://www.polaraccesslink.com/v3/users/123/sleep/{day0.isoformat()}",
        json={
            "polar_user": "123",
            "date": day0.isoformat(),
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

    httpx_mock.add_response(
        url=f"https://www.polaraccesslink.com/v3/users/123/sleep/{day1.isoformat()}",
        status_code=404,
    )

    httpx_mock.add_response(
        url=f"https://www.polaraccesslink.com/v3/users/123/sleep/{day2.isoformat()}",
        json={
            "polar_user": "123",
            "date": day2.isoformat(),
            "sleep_start_time": "2026-01-08T22:00:00Z",
            "sleep_end_time": "2026-01-09T06:00:00Z",
            "device_id": "DEV123",
            "continuity": 3.0,
            "continuity_class": 3,
            "light_sleep": 14400,
            "deep_sleep": 7200,
            "rem_sleep": 3600,
            "unrecognized_sleep_stage": 0,
            "sleep_score": 80,
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
        sleep_list = await client.sleep.list(user_id="123", days=3)

    # Should only return 2 items (skipping the 404)
    assert len(sleep_list) == 2
    assert sleep_list[0].date == day0
    assert sleep_list[1].date == day2
