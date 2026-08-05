"""Tests for physical information endpoint."""

import datetime as dt

import pytest
from pytest_httpx import HTTPXMock

from polar_flow.client import PolarFlow
from polar_flow.exceptions import NotFoundError


@pytest.mark.asyncio
class TestPhysicalInfoEndpoint:
    """Tests for the non-transactional physical info endpoint."""

    async def test_get_physical_info(self, httpx_mock: HTTPXMock) -> None:
        """Test getting the user's current physical information."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/users/physical-info",
            json={
                "weight": 70.5,
                "height": 175,
                "created": "2024-06-01T12:00:00Z",
                "modified": "2024-06-10T12:00:00Z",
                "birthday": "1990-01-01",
                "gender": "MALE",
                "maximum_heart_rate": 190,
                "resting_heart_rate": 60,
                "aerobic_threshold": 140,
                "anaerobic_threshold": 170,
                "vo2_max": 50,
                "weight_source": "SOURCE_USER",
                "training_background": "REGULAR",
                "typical_day": "MOSTLY_MOVING",
                "sleep_goal": "PT8H",
            },
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            info = await client.physical_info.get()

        assert info.weight == 70.5
        assert info.height == 175
        assert info.vo2_max == 50
        assert info.resting_heart_rate == 60
        assert info.maximum_heart_rate == 190
        assert info.aerobic_threshold == 140
        assert info.anaerobic_threshold == 170
        assert info.birthday == dt.date(1990, 1, 1)
        assert info.gender == "MALE"
        assert info.training_background == "REGULAR"
        assert info.sleep_goal == "PT8H"
        assert info.created is not None
        assert info.created.year == 2024

    async def test_get_physical_info_partial(self, httpx_mock: HTTPXMock) -> None:
        """Test partial payload — every field is optional."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/users/physical-info",
            json={"weight": 82.0, "height": 180},
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            info = await client.physical_info.get()

        assert info.weight == 82.0
        assert info.vo2_max is None
        assert info.resting_heart_rate is None

    async def test_get_physical_info_not_found(self, httpx_mock: HTTPXMock) -> None:
        """Test 404 when no physical info exists."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/users/physical-info",
            status_code=404,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(NotFoundError):
                await client.physical_info.get()

    async def test_transaction_flow_warns_deprecated(self, httpx_mock: HTTPXMock) -> None:
        """Test the transaction flow raises a DeprecationWarning."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/users/12345/physical-information-transactions",
            status_code=204,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.warns(DeprecationWarning, match="13.01.2026"):
                result = await client.physical_info.create_transaction(12345)

        assert result is None
