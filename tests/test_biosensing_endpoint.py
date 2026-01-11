"""Tests for Biosensing endpoint."""

import pytest
from pytest_httpx import HTTPXMock

from polar_flow import PolarFlow
from polar_flow.models.biosensing import (
    BodyTemperaturePeriod,
    ECGResult,
    SkinTemperature,
    SpO2Result,
)


@pytest.fixture
def spo2_response() -> list[dict]:
    """Sample SpO2 API response."""
    return [
        {
            "source_device_id": "DEVICE123",
            "test_time": 1704844800000,  # 2024-01-10 00:00:00 UTC
            "time_zone_offset": 0,
            "test_status": "COMPLETED",
            "blood_oxygen_percent": 98,
            "spo2_class": "NORMAL",
            "spo2_value_deviation_from_baseline": "WITHIN_BASELINE",
            "spo2_quality_average_percent": 95.5,
            "average_heart_rate_bpm": 65,
            "heart_rate_variability_ms": 45.2,
            "spo2_hrv_deviation_from_baseline": "WITHIN_BASELINE",
            "altitude_meters": 150.0,
        }
    ]


@pytest.fixture
def ecg_response() -> list[dict]:
    """Sample ECG API response."""
    return [
        {
            "source_device_id": "DEVICE123",
            "test_time": 1704844800000,
            "time_zone_offset": 0,
            "average_heart_rate_bpm": 68,
            "heart_rate_variability_ms": 52.3,
            "heart_rate_variability_level": "NORMAL",
            "rri_ms": 882.4,
            "pulse_transit_time_systolic_ms": 120.5,
            "pulse_transit_time_diastolic_ms": 85.2,
            "pulse_transit_time_quality_index": 0.92,
            "samples": [
                {"recording_time_delta_ms": 0, "amplitude_mv": 0.1},
                {"recording_time_delta_ms": 4, "amplitude_mv": 0.15},
                {"recording_time_delta_ms": 8, "amplitude_mv": 0.8},
            ],
            "quality_measurements": [
                {"recording_time_delta_ms": 0, "quality_level": "GOOD"},
                {"recording_time_delta_ms": 1000, "quality_level": "GOOD"},
            ],
        }
    ]


@pytest.fixture
def body_temp_response() -> list[dict]:
    """Sample body temperature API response."""
    return [
        {
            "source_device_id": "DEVICE123",
            "measurement_type": "CONTINUOUS",
            "sensor_location": "WRIST",
            "start_time": "2024-01-10T22:00:00Z",
            "end_time": "2024-01-11T06:00:00Z",
            "modified_time": "2024-01-11T06:05:00Z",
            "samples": [
                {"temperature_celsius": 36.2, "recording_time_delta_milliseconds": 0},
                {"temperature_celsius": 36.4, "recording_time_delta_milliseconds": 3600000},
                {"temperature_celsius": 36.1, "recording_time_delta_milliseconds": 7200000},
            ],
        }
    ]


@pytest.fixture
def skin_temp_response() -> list[dict]:
    """Sample skin temperature API response."""
    return [
        {
            "sleep_time_skin_temperature_celsius": 35.8,
            "deviation_from_baseline_celsius": 0.3,
            "sleep_date": "2024-01-10",
        },
        {
            "sleep_time_skin_temperature_celsius": 36.5,
            "deviation_from_baseline_celsius": 1.0,
            "sleep_date": "2024-01-09",
        },
    ]


class TestBiosensingSpO2:
    """Tests for SpO2 endpoint."""

    @pytest.mark.asyncio
    async def test_get_spo2_success(
        self, httpx_mock: HTTPXMock, spo2_response: list[dict]
    ) -> None:
        """Test successful SpO2 data fetch."""
        httpx_mock.add_response(json=spo2_response)

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_spo2()

        assert len(results) == 1
        assert isinstance(results[0], SpO2Result)
        assert results[0].blood_oxygen_percent == 98
        assert results[0].spo2_class == "NORMAL"
        assert results[0].average_heart_rate_bpm == 65

    @pytest.mark.asyncio
    async def test_get_spo2_with_date_range(self, httpx_mock: HTTPXMock) -> None:
        """Test SpO2 with date range parameters."""
        httpx_mock.add_response(json=[])

        async with PolarFlow(access_token="test_token") as client:
            await client.biosensing.get_spo2(
                from_date="2024-01-01", to_date="2024-01-07"
            )

        request = httpx_mock.get_request()
        assert "from=2024-01-01" in str(request.url)
        assert "to=2024-01-07" in str(request.url)

    @pytest.mark.asyncio
    async def test_get_spo2_empty_response(self, httpx_mock: HTTPXMock) -> None:
        """Test SpO2 returns empty list on no data."""
        httpx_mock.add_response(json=[])

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_spo2()

        assert results == []

    @pytest.mark.asyncio
    async def test_spo2_computed_properties(self, spo2_response: list[dict]) -> None:
        """Test SpO2 model computed properties."""
        result = SpO2Result.model_validate(spo2_response[0])

        # Test datetime conversion
        assert result.test_datetime.year == 2024
        assert result.test_datetime.month == 1


class TestBiosensingECG:
    """Tests for ECG endpoint."""

    @pytest.mark.asyncio
    async def test_get_ecg_success(
        self, httpx_mock: HTTPXMock, ecg_response: list[dict]
    ) -> None:
        """Test successful ECG data fetch."""
        httpx_mock.add_response(json=ecg_response)

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_ecg()

        assert len(results) == 1
        assert isinstance(results[0], ECGResult)
        assert results[0].average_heart_rate_bpm == 68
        assert results[0].heart_rate_variability_level == "NORMAL"
        assert len(results[0].samples) == 3
        assert len(results[0].quality_measurements) == 2

    @pytest.mark.asyncio
    async def test_ecg_duration_calculation(self, ecg_response: list[dict]) -> None:
        """Test ECG duration computed property."""
        result = ECGResult.model_validate(ecg_response[0])

        # Duration should be max sample time / 1000
        assert result.duration_seconds == 0.008  # 8ms / 1000


class TestBiosensingTemperature:
    """Tests for temperature endpoints."""

    @pytest.mark.asyncio
    async def test_get_body_temperature(
        self, httpx_mock: HTTPXMock, body_temp_response: list[dict]
    ) -> None:
        """Test successful body temperature fetch."""
        httpx_mock.add_response(json=body_temp_response)

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_body_temperature()

        assert len(results) == 1
        assert isinstance(results[0], BodyTemperaturePeriod)
        assert results[0].sensor_location == "WRIST"
        assert len(results[0].samples) == 3

    @pytest.mark.asyncio
    async def test_body_temp_computed_properties(
        self, body_temp_response: list[dict]
    ) -> None:
        """Test body temperature computed properties."""
        result = BodyTemperaturePeriod.model_validate(body_temp_response[0])

        # Average of 36.2, 36.4, 36.1
        assert result.avg_temperature is not None
        assert 36.2 <= result.avg_temperature <= 36.3

        assert result.min_temperature == 36.1
        assert result.max_temperature == 36.4

    @pytest.mark.asyncio
    async def test_get_skin_temperature(
        self, httpx_mock: HTTPXMock, skin_temp_response: list[dict]
    ) -> None:
        """Test successful skin temperature fetch."""
        httpx_mock.add_response(json=skin_temp_response)

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_skin_temperature()

        assert len(results) == 2
        assert isinstance(results[0], SkinTemperature)
        assert results[0].sleep_time_skin_temperature_celsius == 35.8

    @pytest.mark.asyncio
    async def test_skin_temp_elevation_detection(
        self, skin_temp_response: list[dict]
    ) -> None:
        """Test skin temperature elevation detection."""
        normal = SkinTemperature.model_validate(skin_temp_response[0])
        elevated = SkinTemperature.model_validate(skin_temp_response[1])

        assert not normal.is_elevated  # 0.3C deviation
        assert elevated.is_elevated  # 1.0C deviation (>0.5)


class TestBiosensingErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_api_error_returns_empty_list(self, httpx_mock: HTTPXMock) -> None:
        """Test that API errors return empty list instead of crashing."""
        httpx_mock.add_response(status_code=500)

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_spo2()

        assert results == []

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of unexpected response format."""
        httpx_mock.add_response(json={"unexpected": "format"})

        async with PolarFlow(access_token="test_token") as client:
            results = await client.biosensing.get_spo2()

        assert results == []
