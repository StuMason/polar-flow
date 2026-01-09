"""Tests for exercise models."""

import pytest
from pydantic import ValidationError

from polar_flow.models.exercise import (
    Exercise,
    ExerciseSample,
    ExerciseSamples,
    ExerciseZones,
    HeartRateZone,
)


class TestExercise:
    """Tests for Exercise model."""

    def test_basic_exercise(self) -> None:
        """Test basic exercise creation."""
        exercise = Exercise(
            id="12345",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Polar Vantage V2",
            device_id="1234ABCD",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=60,
            duration="PT1H30M",
            calories=450,
            distance=10000.0,
            heart_rate={"average": 145, "maximum": 180},
            training_load=85.5,
            sport="RUNNING",
            has_route=True,
            club_id=None,
            club_name=None,
            detailed_sport_info="ROAD_RUNNING",
            fat_percentage=35,
            carbohydrate_percentage=65,
            protein_percentage=0,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.id == "12345"
        assert exercise.sport == "RUNNING"
        assert exercise.calories == 450
        assert exercise.distance == 10000.0
        assert exercise.duration == "PT1H30M"

    def test_duration_seconds_simple(self) -> None:
        """Test duration parsing for simple format."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H30M45S",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.duration_seconds == 5445  # 1*3600 + 30*60 + 45

    def test_duration_seconds_hours_only(self) -> None:
        """Test duration parsing with only hours."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT2H",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.duration_seconds == 7200  # 2*3600

    def test_duration_seconds_minutes_only(self) -> None:
        """Test duration parsing with only minutes."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT45M",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.duration_seconds == 2700  # 45*60

    def test_duration_seconds_seconds_only(self) -> None:
        """Test duration parsing with only seconds."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT30S",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.duration_seconds == 30

    def test_duration_minutes(self) -> None:
        """Test duration in minutes conversion."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H30M",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.duration_minutes == 90.0

    def test_distance_km_with_meters(self) -> None:
        """Test distance conversion from meters to km."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H",
            calories=100,
            distance=5500.0,  # meters
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.distance_km == 5.5

    def test_distance_km_none(self) -> None:
        """Test distance_km when distance is None."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H",
            calories=100,
            distance=None,
            heart_rate={"average": 120, "maximum": 150},
            training_load=50.0,
            sport="SWIMMING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="SWIMMING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.distance_km is None

    def test_average_heart_rate(self) -> None:
        """Test average heart rate extraction."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H",
            calories=100,
            distance=None,
            heart_rate={"average": 145, "maximum": 180},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.average_heart_rate == 145

    def test_maximum_heart_rate(self) -> None:
        """Test maximum heart rate extraction."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H",
            calories=100,
            distance=None,
            heart_rate={"average": 145, "maximum": 180},
            training_load=50.0,
            sport="RUNNING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="RUNNING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.maximum_heart_rate == 180

    def test_heart_rate_none(self) -> None:
        """Test heart rate properties when heart_rate is None."""
        exercise = Exercise(
            id="1",
            upload_time="2026-01-09T10:00:00Z",
            polar_user="https://www.polaraccesslink.com/v3/users/1",
            device="Test",
            device_id="123",
            start_time="2026-01-09T08:00:00Z",
            start_time_utc_offset=0,
            duration="PT1H",
            calories=100,
            distance=None,
            heart_rate=None,
            training_load=50.0,
            sport="SWIMMING",
            has_route=False,
            club_id=None,
            club_name=None,
            detailed_sport_info="SWIMMING",
            fat_percentage=None,
            carbohydrate_percentage=None,
            protein_percentage=None,
            running_index=None,
            training_load_pro=None,
        )

        assert exercise.average_heart_rate is None
        assert exercise.maximum_heart_rate is None

    def test_validation_negative_calories(self) -> None:
        """Test validation fails for negative calories."""
        with pytest.raises(ValidationError) as exc_info:
            Exercise(
                id="1",
                upload_time="2026-01-09T10:00:00Z",
                polar_user="https://www.polaraccesslink.com/v3/users/1",
                device="Test",
                device_id="123",
                start_time="2026-01-09T08:00:00Z",
                start_time_utc_offset=0,
                duration="PT1H",
                calories=-100,  # Invalid
                distance=None,
                heart_rate=None,
                training_load=50.0,
                sport="RUNNING",
                has_route=False,
                club_id=None,
                club_name=None,
                detailed_sport_info="RUNNING",
                fat_percentage=None,
                carbohydrate_percentage=None,
                protein_percentage=None,
                running_index=None,
                training_load_pro=None,
            )

        assert "calories" in str(exc_info.value)


class TestExerciseSample:
    """Tests for ExerciseSample model."""

    def test_basic_sample(self) -> None:
        """Test basic sample creation."""
        sample = ExerciseSample(
            sample_type="HEARTRATE",
            recording_rate=5,
            values=[120, 125, 130, 135, 140],
        )

        assert sample.sample_type == "HEARTRATE"
        assert sample.recording_rate == 5
        assert len(sample.values) == 5
        assert sample.values[0] == 120

    def test_sample_with_string_values(self) -> None:
        """Test sample with string values."""
        sample = ExerciseSample(
            sample_type="SPEED",
            recording_rate=1,
            values=["5.5", "6.0", "6.5"],
        )

        assert sample.sample_type == "SPEED"
        assert len(sample.values) == 3


class TestExerciseSamples:
    """Tests for ExerciseSamples model."""

    def test_exercise_samples(self) -> None:
        """Test exercise samples container."""
        samples = ExerciseSamples(
            samples=[
                {
                    "sample-type": "HEARTRATE",
                    "recording-rate": 5,
                    "data": [120, 125, 130],
                },
                {
                    "sample-type": "SPEED",
                    "recording-rate": 1,
                    "data": ["5.5", "6.0"],
                },
            ]
        )

        assert len(samples.samples) == 2
        assert samples.samples[0].sample_type == "HEARTRATE"
        assert samples.samples[1].sample_type == "SPEED"

    def test_get_sample_by_type_found(self) -> None:
        """Test getting sample by type when it exists."""
        samples = ExerciseSamples(
            samples=[
                {
                    "sample-type": "HEARTRATE",
                    "recording-rate": 5,
                    "data": [120, 125, 130],
                },
                {
                    "sample-type": "SPEED",
                    "recording-rate": 1,
                    "data": ["5.5", "6.0"],
                },
            ]
        )

        hr_sample = samples.get_sample_by_type("HEARTRATE")
        assert hr_sample is not None
        assert hr_sample.sample_type == "HEARTRATE"
        assert len(hr_sample.values) == 3

    def test_get_sample_by_type_not_found(self) -> None:
        """Test getting sample by type when it doesn't exist."""
        samples = ExerciseSamples(
            samples=[
                {
                    "sample-type": "HEARTRATE",
                    "recording-rate": 5,
                    "data": [120, 125, 130],
                }
            ]
        )

        cadence_sample = samples.get_sample_by_type("CADENCE")
        assert cadence_sample is None

    def test_empty_samples(self) -> None:
        """Test empty samples container."""
        samples = ExerciseSamples(samples=[])
        assert len(samples.samples) == 0
        assert samples.get_sample_by_type("HEARTRATE") is None


class TestHeartRateZone:
    """Tests for HeartRateZone model."""

    def test_basic_zone(self) -> None:
        """Test basic heart rate zone creation."""
        zone = HeartRateZone(
            index=1,
            lower_limit=100,
            upper_limit=120,
            in_zone="PT10M30S",
        )

        assert zone.index == 1
        assert zone.lower_limit == 100
        assert zone.upper_limit == 120
        assert zone.in_zone == "PT10M30S"

    def test_in_zone_seconds(self) -> None:
        """Test in_zone duration parsing."""
        zone = HeartRateZone(
            index=2,
            lower_limit=120,
            upper_limit=140,
            in_zone="PT1H30M45S",
        )

        assert zone.in_zone_seconds == 5445  # 1*3600 + 30*60 + 45

    def test_in_zone_minutes(self) -> None:
        """Test in_zone minutes conversion."""
        zone = HeartRateZone(
            index=3,
            lower_limit=140,
            upper_limit=160,
            in_zone="PT45M",
        )

        assert zone.in_zone_minutes == 45.0

    def test_validation_invalid_index(self) -> None:
        """Test validation fails for invalid zone index."""
        with pytest.raises(ValidationError) as exc_info:
            HeartRateZone(
                index=0,  # Invalid, must be >= 1
                lower_limit=100,
                upper_limit=120,
                in_zone="PT10M",
            )

        assert "index" in str(exc_info.value)

    def test_validation_negative_limits(self) -> None:
        """Test validation fails for negative HR limits."""
        with pytest.raises(ValidationError) as exc_info:
            HeartRateZone(
                index=1,
                lower_limit=-10,  # Invalid
                upper_limit=120,
                in_zone="PT10M",
            )

        assert "lower_limit" in str(exc_info.value)


class TestExerciseZones:
    """Tests for ExerciseZones model."""

    def test_exercise_zones(self) -> None:
        """Test exercise zones container."""
        zones = ExerciseZones(
            zones=[
                {"index": 1, "lower-limit": 100, "upper-limit": 120, "in-zone": "PT5M"},
                {"index": 2, "lower-limit": 120, "upper-limit": 140, "in-zone": "PT10M"},
                {"index": 3, "lower-limit": 140, "upper-limit": 160, "in-zone": "PT15M"},
            ]
        )

        assert len(zones.zones) == 3
        assert zones.zones[0].index == 1
        assert zones.zones[1].index == 2
        assert zones.zones[2].index == 3

    def test_empty_zones(self) -> None:
        """Test empty zones container."""
        zones = ExerciseZones(zones=[])
        assert len(zones.zones) == 0

    def test_zones_ordered(self) -> None:
        """Test that zones maintain their order."""
        zones = ExerciseZones(
            zones=[
                {"index": 3, "lower-limit": 140, "upper-limit": 160, "in-zone": "PT15M"},
                {"index": 1, "lower-limit": 100, "upper-limit": 120, "in-zone": "PT5M"},
                {"index": 2, "lower-limit": 120, "upper-limit": 140, "in-zone": "PT10M"},
            ]
        )

        # Should maintain order as provided (not auto-sorted)
        assert zones.zones[0].index == 3
        assert zones.zones[1].index == 1
        assert zones.zones[2].index == 2
