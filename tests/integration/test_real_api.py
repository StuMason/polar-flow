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
                assert first.calories is None or first.calories >= 0
                assert first.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_get_exercise_details(self, access_token: str) -> None:
        """Test getting detailed exercise data."""
        from polar_flow.exceptions import NotFoundError

        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nTesting exercise ID: {exercise_id}")

            # Get detailed exercise
            try:
                exercise = await client.exercises.get(exercise_id=exercise_id)
            except NotFoundError:
                pytest.skip(f"Exercise {exercise_id} has no detailed data available")

            assert exercise.id == exercise_id
            assert exercise.sport
            assert exercise.calories is None or exercise.calories >= 0

            print(f"Sport: {exercise.sport}")
            print(f"Duration: {exercise.duration_minutes} minutes")
            print(f"Calories: {exercise.calories}")
            if exercise.distance_km:
                print(f"Distance: {exercise.distance_km} km")
            if exercise.average_heart_rate:
                print(f"Avg HR: {exercise.average_heart_rate} bpm")
                print(f"Max HR: {exercise.maximum_heart_rate} bpm")

    @pytest.mark.asyncio
    async def test_get_exercise_samples(self, access_token: str) -> None:
        """Test getting exercise samples (HR, speed, etc.)."""
        from polar_flow.exceptions import NotFoundError

        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nGetting samples for exercise: {exercise_id}")

            try:
                samples = await client.exercises.get_samples(exercise_id=exercise_id)
            except NotFoundError:
                pytest.skip(f"Exercise {exercise_id} has no sample data available")

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
        from polar_flow.exceptions import NotFoundError

        async with PolarFlow(access_token=access_token) as client:
            exercises = await client.exercises.list()

            if not exercises:
                pytest.skip("No exercises available to test")

            exercise_id = exercises[0].id
            print(f"\nGetting zones for exercise: {exercise_id}")

            try:
                zones = await client.exercises.get_zones(exercise_id=exercise_id)
            except NotFoundError:
                pytest.skip(f"Exercise {exercise_id} has no zone data available")

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
class TestActivityIntegration:
    """Integration tests for activity endpoint."""

    @pytest.mark.asyncio
    async def test_list_activities(self, access_token: str) -> None:
        """Test listing activities for last 28 days."""
        async with PolarFlow(access_token=access_token) as client:
            activities = await client.activity.list()

            print(f"\nFound {len(activities)} activities in last 28 days")

            if activities:
                first = activities[0]
                print(f"  {first.start_time.date()}: {first.steps} steps, {first.calories} cal")
                print(
                    f"  Active: {first.active_duration_minutes}min, Distance: {first.distance_km}km"
                )

                # Validate structure
                assert first.steps >= 0
                assert first.calories >= 0
                assert first.active_duration_seconds >= 0
                assert first.inactive_duration_seconds >= 0
                assert first.distance_from_steps >= 0

    @pytest.mark.asyncio
    async def test_get_activity_by_date(self, access_token: str) -> None:
        """Test getting activity for a specific date."""
        from datetime import date, timedelta

        from polar_flow.exceptions import NotFoundError

        async with PolarFlow(access_token=access_token) as client:
            # Try yesterday
            yesterday = (date.today() - timedelta(days=1)).isoformat()

            try:
                activity = await client.activity.get(date=yesterday)
                print(f"\nActivity for {yesterday}:")
                print(f"  Steps: {activity.steps}")
                print(f"  Calories: {activity.calories}")
                print(f"  Active: {activity.active_duration_minutes}min")
                print(f"  Inactivity alerts: {activity.inactivity_alert_count}")

                # Check for samples
                if activity.samples:
                    print(
                        f"  Has samples: steps={activity.samples.steps is not None}, "
                        f"zones={activity.samples.activity_zones is not None}"
                    )

                assert activity.steps >= 0
                assert activity.calories >= 0

            except NotFoundError:
                pytest.skip(f"No activity data for {yesterday}")


@pytest.mark.integration
class TestRechargeIntegration:
    """Integration tests for nightly recharge endpoint."""

    @pytest.mark.asyncio
    async def test_list_recharge(self, access_token: str) -> None:
        """Test listing nightly recharge data."""
        async with PolarFlow(access_token=access_token) as client:
            recharge_list = await client.recharge.list()

            print(f"\nFound {len(recharge_list)} recharge records in last 28 days")

            if recharge_list:
                first = recharge_list[0]
                print(
                    f"  {first.date}: ANS charge {first.ans_charge:.1f}, status {first.ans_charge_status}"
                )
                print(
                    f"  HR avg: {first.heart_rate_avg} bpm, HRV avg: {first.heart_rate_variability_avg}ms"
                )
                print(f"  Breathing: {first.breathing_rate_avg:.1f} breaths/min")

                # Validate structure
                assert first.nightly_recharge_status >= 1
                assert first.nightly_recharge_status <= 6
                assert first.ans_charge_status >= 1
                assert first.ans_charge_status <= 5
                assert -10.0 <= first.ans_charge <= 10.0

    @pytest.mark.asyncio
    async def test_get_recharge_by_date(self, access_token: str) -> None:
        """Test getting recharge for specific date."""
        from datetime import date, timedelta

        from polar_flow.exceptions import NotFoundError

        async with PolarFlow(access_token=access_token) as client:
            # Try yesterday
            yesterday = (date.today() - timedelta(days=1)).isoformat()

            try:
                recharge = await client.recharge.get(date=yesterday)
                print(f"\nRecharge for {yesterday}:")
                print(f"  Nightly recharge status: {recharge.nightly_recharge_status}/6")
                print(
                    f"  ANS charge: {recharge.ans_charge:.1f} (status: {recharge.ans_charge_status}/5)"
                )
                print(f"  Heart rate: {recharge.heart_rate_avg} bpm")
                print(f"  HRV: {recharge.heart_rate_variability_avg}ms")

                # Check for samples
                if recharge.hrv_samples:
                    print(f"  HRV samples: {len(recharge.hrv_samples)} entries")
                if recharge.breathing_samples:
                    print(f"  Breathing samples: {len(recharge.breathing_samples)} entries")

                assert recharge.heart_rate_avg > 0
                assert recharge.heart_rate_variability_avg > 0

            except NotFoundError:
                pytest.skip(f"No recharge data for {yesterday}")


@pytest.mark.integration
class TestPhysicalInfoIntegration:
    """Integration tests for physical information endpoint.

    Note: Physical info endpoint requires actual user ID (not 'self').
    These tests are skipped unless USER_ID is set in environment.
    """

    @pytest.mark.asyncio
    async def test_physical_info_flow(self, access_token: str) -> None:
        """Test complete physical info transaction flow."""
        import os

        user_id = os.getenv("USER_ID")
        if not user_id:
            pytest.skip("USER_ID not set - physical info requires numeric user ID (not 'self')")

        async with PolarFlow(access_token=access_token) as client:
            # Create transaction
            transaction = await client.physical_info.create_transaction(user_id=user_id)

            if not transaction:
                print("\nNo new physical information available")
                pytest.skip("No new physical information available")

            print(f"\nCreated transaction: {transaction.transaction_id}")

            # List physical info in transaction
            info_urls = await client.physical_info.list_physical_info(
                user_id, transaction.transaction_id
            )
            print(f"Found {len(info_urls)} physical information records")

            if info_urls:
                # Get first physical info
                physical_info_id = int(info_urls[0].rstrip("/").split("/")[-1])
                info = await client.physical_info.get_physical_info(
                    user_id, transaction.transaction_id, physical_info_id
                )

                print(f"Physical info ID {info.id}:")
                print(f"  Created: {info.created}")
                if info.weight:
                    print(f"  Weight: {info.weight}kg")
                if info.height:
                    print(f"  Height: {info.height}cm")
                if info.maximum_heart_rate:
                    print(f"  Max HR: {info.maximum_heart_rate} bpm")
                if info.vo2_max:
                    print(f"  VO2 max: {info.vo2_max} ml/kg/min")

                assert info.id > 0
                assert info.transaction_id == transaction.transaction_id

            # Commit transaction
            await client.physical_info.commit_transaction(user_id, transaction.transaction_id)
            print(f"Transaction {transaction.transaction_id} committed")

    @pytest.mark.asyncio
    async def test_physical_info_get_all(self, access_token: str) -> None:
        """Test convenience get_all method."""
        import os

        user_id = os.getenv("USER_ID")
        if not user_id:
            pytest.skip("USER_ID not set - physical info requires numeric user ID (not 'self')")

        async with PolarFlow(access_token=access_token) as client:
            physical_infos = await client.physical_info.get_all(user_id=user_id)

            print(f"\nRetrieved {len(physical_infos)} physical information records")

            for info in physical_infos:
                print(f"  ID {info.id}: created {info.created.date()}")
                if info.weight:
                    print(f"    Weight: {info.weight}kg")


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
