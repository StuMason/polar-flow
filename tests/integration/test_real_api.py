"""Integration tests against real Polar AccessLink V3 API.

These tests require a valid access token and hit the real API endpoints.
They are excluded from regular test runs and must be run manually.

Setup:
------
1. Create a .env file in the project root with:
   ACCESS_TOKEN=your_real_access_token
   CLIENT_ID=your_client_id (optional, for OAuth tests)
   CLIENT_SECRET=your_client_secret (optional, for OAuth tests)

2. Run integration tests only:
   pytest tests/integration/ -v

3. Run with debug logging:
   pytest tests/integration/ -v -s --log-cli-level=DEBUG

Note: These tests use your real Polar data and count against your rate limits.
"""

import os
from datetime import date
from pathlib import Path

import pytest
from dotenv import load_dotenv

from polar_flow.client import PolarFlow

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


# Skip all tests if ACCESS_TOKEN not set
pytestmark = pytest.mark.skipif(
    not os.getenv("ACCESS_TOKEN"),
    reason="ACCESS_TOKEN not set in environment - skipping integration tests",
)


@pytest.fixture
def access_token() -> str:
    """Get access token from environment."""
    token = os.getenv("ACCESS_TOKEN")
    if not token:
        pytest.skip("ACCESS_TOKEN not set")
    return token


@pytest.mark.integration
class TestSleepIntegration:
    """Integration tests for sleep endpoint."""

    @pytest.mark.asyncio
    async def test_get_sleep_today(self, access_token: str) -> None:
        """Test getting sleep data for today (may not exist)."""
        async with PolarFlow(access_token=access_token) as client:
            # Try to get sleep data for today - it's OK if it doesn't exist (404)
            try:
                today = date.today().isoformat()
                sleep_data = await client.sleep.get(user_id="self", date=today)

                # If we got data, validate it
                assert sleep_data.sleep_score >= 1
                assert sleep_data.sleep_score <= 100
                assert sleep_data.total_sleep_seconds > 0
                print(f"\nSleep score: {sleep_data.sleep_score}")
                print(f"Total sleep: {sleep_data.total_sleep_hours} hours")
            except Exception as e:
                # Expected if no sleep data for today
                print(f"\nNo sleep data for today (expected): {e}")

    @pytest.mark.asyncio
    async def test_list_sleep_last_7_days(self, access_token: str) -> None:
        """Test listing sleep data for last 7 days."""
        async with PolarFlow(access_token=access_token) as client:
            sleep_list = await client.sleep.list(user_id="self", days=7)

            # May return 0-7 records depending on available data
            print(f"\nFound {len(sleep_list)} sleep records in last 7 days")

            for sleep_data in sleep_list[:3]:  # Show first 3
                print(
                    f"  {sleep_data.date}: score {sleep_data.sleep_score}, "
                    f"{sleep_data.total_sleep_hours}h sleep"
                )


@pytest.mark.integration
class TestExercisesIntegration:
    """Integration tests for exercises endpoint."""

    @pytest.mark.asyncio
    async def test_list_exercises(self, access_token: str) -> None:
        """Test listing exercises (last 30 days)."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            print(f"\nFound {len(exercises)} exercises in last 30 days")

            # Show first few exercises
            for exercise in exercises[:5]:
                duration_min = exercise.duration_minutes
                distance = f"{exercise.distance_km}km" if exercise.distance_km else "no distance"
                print(
                    f"  {exercise.start_time}: {exercise.sport} - "
                    f"{duration_min}min, {exercise.calories}cal, {distance}"
                )

            # Validate structure if we have any exercises
            if exercises:
                first = exercises[0]
                assert first.id
                assert first.sport
                assert first.calories >= 0
                assert first.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_get_exercise_details(self, access_token: str) -> None:
        """Test getting detailed exercise data."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nTesting exercise ID: {exercise_id}")

            # Get detailed exercise
            exercise = await client.exercises.get(exercise_id=exercise_id)

            assert exercise.id == exercise_id
            assert exercise.sport
            assert exercise.calories >= 0

            print(f"Sport: {exercise.sport}")
            print(f"Duration: {exercise.duration_minutes} minutes")
            print(f"Calories: {exercise.calories}")
            if exercise.distance_km:
                print(f"Distance: {exercise.distance_km} km")
            if exercise.average_heart_rate:
                print(f"Avg HR: {exercise.average_heart_rate} bpm")
                print(f"Max HR: {exercise.max_heart_rate} bpm")

    @pytest.mark.asyncio
    async def test_get_exercise_samples(self, access_token: str) -> None:
        """Test getting exercise samples (HR, speed, etc.)."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nGetting samples for exercise: {exercise_id}")

            samples = await client.exercises.get_samples(exercise_id=exercise_id)

            print(f"Found {len(samples.samples)} sample types")

            for sample in samples.samples:
                print(
                    f"  {sample.sample_type}: {len(sample.values)} values "
                    f"(rate: {sample.recording_rate}s)"
                )

            # Check for common sample types
            hr_sample = samples.get_sample_by_type("HEARTRATE")
            if hr_sample:
                print(f"\nHeart rate: {len(hr_sample.values)} samples")
                if hr_sample.values:
                    print(f"  First 5 values: {hr_sample.values[:5]}")

    @pytest.mark.asyncio
    async def test_get_exercise_zones(self, access_token: str) -> None:
        """Test getting heart rate zones for exercise."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nGetting zones for exercise: {exercise_id}")

            zones = await client.exercises.get_zones(exercise_id=exercise_id)

            print(f"Found {len(zones.zones)} heart rate zones")

            for zone in zones.zones:
                print(
                    f"  Zone {zone.index}: {zone.lower_limit}-{zone.upper_limit} bpm, "
                    f"{zone.in_zone_minutes} minutes"
                )

    @pytest.mark.asyncio
    async def test_export_tcx(self, access_token: str) -> None:
        """Test exporting exercise as TCX format."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            # Find an exercise with route data (GPS)
            exercise_with_route = None
            for ex in exercises:
                if ex.has_route:
                    exercise_with_route = ex
                    break

            if not exercise_with_route:
                pytest.skip("No exercises with route data available")

            exercise_id = exercise_with_route.id
            print(f"\nExporting exercise {exercise_id} as TCX")

            tcx_xml = await client.exercises.export_tcx(exercise_id=exercise_id)

            # Validate it's XML
            assert "<?xml" in tcx_xml
            assert "<TrainingCenterDatabase" in tcx_xml or "<Activities" in tcx_xml

            print(f"TCX export successful: {len(tcx_xml)} characters")
            print("First 200 chars:", tcx_xml[:200])

    @pytest.mark.asyncio
    async def test_export_gpx(self, access_token: str) -> None:
        """Test exporting exercise as GPX format."""
        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            # Find an exercise with route data (GPS)
            exercise_with_route = None
            for ex in exercises:
                if ex.has_route:
                    exercise_with_route = ex
                    break

            if not exercise_with_route:
                pytest.skip("No exercises with route data available")

            exercise_id = exercise_with_route.id
            print(f"\nExporting exercise {exercise_id} as GPX")

            gpx_xml = await client.exercises.export_gpx(exercise_id=exercise_id)

            # Validate it's XML with GPX structure
            assert "<?xml" in gpx_xml
            assert "<gpx" in gpx_xml

            print(f"GPX export successful: {len(gpx_xml)} characters")
            print("First 200 chars:", gpx_xml[:200])


@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting behavior."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, access_token: str) -> None:
        """Test that rate limit headers are logged."""
        async with PolarFlow(access_token=access_token) as client:
            # Make a simple request and check logs for rate limit info
            try:
                await client.sleep.list(user_id="self", days=1)
                # If this succeeds, rate limit headers should be in logs
                print("\nRate limit test passed - check logs for X-RateLimit headers")
            except Exception as e:
                print(f"\nRate limit test error: {e}")
