"""Tests for exercises endpoint."""

import pytest
from pytest_httpx import HTTPXMock

from polar_flow.client import PolarFlow
from polar_flow.exceptions import AuthenticationError, NotFoundError, PolarFlowError


@pytest.mark.asyncio
class TestExercisesEndpoint:
    """Tests for exercises endpoint."""

    async def test_list_exercises(self, httpx_mock: HTTPXMock) -> None:
        """Test listing all exercises."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises",
            json=[
                {
                    "id": "123",
                    "upload-time": "2026-01-09T10:00:00Z",
                    "polar-user": "https://www.polaraccesslink.com/v3/users/1",
                    "device": "Polar Vantage V2",
                    "device-id": "ABC123",
                    "start-time": "2026-01-09T08:00:00Z",
                    "start-time-utc-offset": 60,
                    "duration": "PT1H",
                    "calories": 400,
                    "distance": 10000.0,
                    "heart-rate": {"average": 140, "maximum": 175},
                    "training-load": 80.0,
                    "sport": "RUNNING",
                    "has-route": True,
                    "club-id": None,
                    "club-name": None,
                    "detailed-sport-info": "ROAD_RUNNING",
                    "fat-percentage": 40,
                    "carbohydrate-percentage": 60,
                    "protein-percentage": 0,
                    "running-index": None,
                    "training-load-pro": None,
                },
                {
                    "id": "456",
                    "upload-time": "2026-01-08T18:00:00Z",
                    "polar-user": "https://www.polaraccesslink.com/v3/users/1",
                    "device": "Polar H10",
                    "device-id": "DEF456",
                    "start-time": "2026-01-08T17:00:00Z",
                    "start-time-utc-offset": 60,
                    "duration": "PT45M",
                    "calories": 300,
                    "distance": None,
                    "heart-rate": {"average": 130, "maximum": 160},
                    "training-load": 60.0,
                    "sport": "CYCLING",
                    "has-route": False,
                    "club-id": None,
                    "club-name": None,
                    "detailed-sport-info": "INDOOR_CYCLING",
                    "fat-percentage": None,
                    "carbohydrate-percentage": None,
                    "protein-percentage": None,
                    "running-index": None,
                    "training-load-pro": None,
                },
            ],
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            exercises = await client.exercises.list()

        assert len(exercises) == 2
        assert exercises[0].id == "123"
        assert exercises[0].sport == "RUNNING"
        assert exercises[0].duration_minutes == 60.0
        assert exercises[1].id == "456"
        assert exercises[1].sport == "CYCLING"

    async def test_list_exercises_empty(self, httpx_mock: HTTPXMock) -> None:
        """Test listing exercises when none available."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises",
            json=[],
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            exercises = await client.exercises.list()

        assert len(exercises) == 0

    async def test_get_exercise(self, httpx_mock: HTTPXMock) -> None:
        """Test getting a single exercise."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123",
            json={
                "id": "123",
                "upload-time": "2026-01-09T10:00:00Z",
                "polar-user": "https://www.polaraccesslink.com/v3/users/1",
                "device": "Polar Vantage V2",
                "device-id": "ABC123",
                "start-time": "2026-01-09T08:00:00Z",
                "start-time-utc-offset": 60,
                "duration": "PT1H30M",
                "calories": 450,
                "distance": 12000.0,
                "heart-rate": {"average": 145, "maximum": 180},
                "training-load": 85.0,
                "sport": "RUNNING",
                "has-route": True,
                "club-id": None,
                "club-name": None,
                "detailed-sport-info": "TRAIL_RUNNING",
                "fat-percentage": 35,
                "carbohydrate-percentage": 65,
                "protein-percentage": 0,
                "running-index": 55,
                "training-load-pro": None,
            },
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            exercise = await client.exercises.get(exercise_id="123")

        assert exercise.id == "123"
        assert exercise.sport == "RUNNING"
        assert exercise.calories == 450
        assert exercise.distance_km == 12.0
        assert exercise.duration_minutes == 90.0
        assert exercise.average_heart_rate == 145

    async def test_get_exercise_not_found(self, httpx_mock: HTTPXMock) -> None:
        """Test getting non-existent exercise."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/999",
            status_code=404,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(NotFoundError):
                await client.exercises.get(exercise_id="999")

    async def test_get_samples(self, httpx_mock: HTTPXMock) -> None:
        """Test getting exercise samples."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/samples",
            json={
                "samples": [
                    {
                        "sample-type": "HEARTRATE",
                        "recording-rate": 5,
                        "data": [120, 125, 130, 135, 140, 145],
                    },
                    {
                        "sample-type": "SPEED",
                        "recording-rate": 1,
                        "data": ["5.5", "6.0", "6.5", "7.0"],
                    },
                    {
                        "sample-type": "CADENCE",
                        "recording-rate": 1,
                        "data": [85, 87, 88, 90],
                    },
                ]
            },
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            samples = await client.exercises.get_samples(exercise_id="123")

        assert len(samples.samples) == 3

        hr_sample = samples.get_sample_by_type("HEARTRATE")
        assert hr_sample is not None
        assert hr_sample.recording_rate == 5
        assert len(hr_sample.values) == 6

        speed_sample = samples.get_sample_by_type("SPEED")
        assert speed_sample is not None
        assert len(speed_sample.values) == 4

    async def test_get_samples_empty(self, httpx_mock: HTTPXMock) -> None:
        """Test getting samples when none available."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/samples",
            json={"samples": []},
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            samples = await client.exercises.get_samples(exercise_id="123")

        assert len(samples.samples) == 0

    async def test_get_zones(self, httpx_mock: HTTPXMock) -> None:
        """Test getting heart rate zones."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/zones",
            json={
                "zone": [
                    {"index": 1, "lower-limit": 100, "upper-limit": 120, "in-zone": "PT5M"},
                    {"index": 2, "lower-limit": 120, "upper-limit": 140, "in-zone": "PT15M"},
                    {"index": 3, "lower-limit": 140, "upper-limit": 160, "in-zone": "PT20M"},
                    {"index": 4, "lower-limit": 160, "upper-limit": 180, "in-zone": "PT10M"},
                ]
            },
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            zones = await client.exercises.get_zones(exercise_id="123")

        assert len(zones.zones) == 4
        assert zones.zones[0].index == 1
        assert zones.zones[0].in_zone_minutes == 5.0
        assert zones.zones[2].index == 3
        assert zones.zones[2].in_zone_minutes == 20.0

    async def test_get_zones_empty(self, httpx_mock: HTTPXMock) -> None:
        """Test getting zones when none available."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/zones",
            json={"zone": []},
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            zones = await client.exercises.get_zones(exercise_id="123")

        assert len(zones.zones) == 0

    async def test_export_tcx(self, httpx_mock: HTTPXMock) -> None:
        """Test exporting exercise as TCX."""
        tcx_content = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase>
  <Activities>
    <Activity Sport="Running">
      <Id>2026-01-09T08:00:00Z</Id>
      <Lap>
        <TotalTimeSeconds>3600</TotalTimeSeconds>
        <DistanceMeters>10000</DistanceMeters>
        <Calories>400</Calories>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""

        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/tcx",
            text=tcx_content,
            headers={"Content-Type": "application/xml"},
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            tcx = await client.exercises.export_tcx(exercise_id="123")

        assert "TrainingCenterDatabase" in tcx
        assert "Running" in tcx
        assert "10000" in tcx

    async def test_export_tcx_not_found(self, httpx_mock: HTTPXMock) -> None:
        """Test exporting non-existent exercise as TCX."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/999/tcx",
            status_code=404,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(NotFoundError) as exc_info:
                await client.exercises.export_tcx(exercise_id="999")

            assert "999" in str(exc_info.value)

    async def test_export_tcx_auth_error(self, httpx_mock: HTTPXMock) -> None:
        """Test TCX export with invalid token."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/tcx",
            status_code=401,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(AuthenticationError):
                await client.exercises.export_tcx(exercise_id="123")

    async def test_export_gpx(self, httpx_mock: HTTPXMock) -> None:
        """Test exporting exercise as GPX."""
        gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <metadata>
    <time>2026-01-09T08:00:00Z</time>
  </metadata>
  <trk>
    <name>Running</name>
    <trkseg>
      <trkpt lat="51.5074" lon="-0.1278">
        <ele>10</ele>
        <time>2026-01-09T08:00:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/gpx",
            text=gpx_content,
            headers={"Content-Type": "application/xml"},
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            gpx = await client.exercises.export_gpx(exercise_id="123")

        assert "<?xml" in gpx
        assert "<gpx" in gpx
        assert "51.5074" in gpx

    async def test_export_gpx_not_found(self, httpx_mock: HTTPXMock) -> None:
        """Test exporting non-existent exercise as GPX."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/999/gpx",
            status_code=404,
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(NotFoundError) as exc_info:
                await client.exercises.export_gpx(exercise_id="999")

            assert "999" in str(exc_info.value)

    async def test_export_gpx_api_error(self, httpx_mock: HTTPXMock) -> None:
        """Test GPX export with API error."""
        httpx_mock.add_response(
            url="https://www.polaraccesslink.com/v3/exercises/123/gpx",
            status_code=500,
            text="Internal Server Error",
        )

        async with PolarFlow(access_token="test_token_1234567890") as client:
            with pytest.raises(PolarFlowError) as exc_info:
                await client.exercises.export_gpx(exercise_id="123")

            assert "500" in str(exc_info.value)
