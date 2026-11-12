"""Tests for activity samples endpoint."""

import pytest
from pytest_httpx import HTTPXMock

from polar_flow.client import PolarFlow


@pytest.mark.asyncio
class TestActivitySamplesEndpoint:
    """Tests for GET /v3/users/activities/samples."""

    async def test_list_samples(self, httpx_mock: HTTPXMock) -> None:
        """Test a day with step samples (documented wire format)."""
        httpx_mock.add_response(
            json=[
                {
                    "date": "2026-09-01",
                    "steps": {
                        "interval_ms": 60000,
                        "total_steps": 42,
                        "samples": [{"steps": 42, "timestamp": "2026-09-01T00:02"}],
                    },
                    "activity_zones": {
                        "samples": [{"zone": "SEDENTARY", "timestamp": "2026-09-01T00:08:30"}]
                    },
                    "inactivity_stamps": [{"stamp": "2026-09-01T16:04"}],
                }
            ],
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            days = await client.activity_samples.list(from_date="2026-09-01", to_date="2026-09-01")

        assert len(days) == 1
        assert days[0].steps is not None
        assert days[0].steps.total_steps == 42

    async def test_list_samples_day_without_steps(self, httpx_mock: HTTPXMock) -> None:
        """A day with no `steps` key validates (issue #17; `steps` is optional in the docs)."""
        httpx_mock.add_response(
            json=[
                {
                    "date": "2026-09-02",
                    "activity_zones": {
                        "samples": [{"zone": "SEDENTARY", "timestamp": "2026-09-02T00:08:30"}]
                    },
                    "inactivity_stamps": [],
                }
            ],
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            days = await client.activity_samples.list(from_date="2026-09-02", to_date="2026-09-02")

        assert len(days) == 1
        assert days[0].date == "2026-09-02"
        assert days[0].steps is None
