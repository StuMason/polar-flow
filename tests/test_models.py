"""Tests for Pydantic models."""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from polar_flow.models.sleep import SleepData


def test_sleep_data_basic_validation() -> None:
    """Test SleepData model validates correctly with all required fields."""
    data = {
        "polar_user": "12345678",
        "date": "2026-01-09",
        "sleep_start_time": "2026-01-08T22:00:00Z",
        "sleep_end_time": "2026-01-09T06:00:00Z",
        "device_id": "ABCD1234",
        "continuity": 3.5,
        "continuity_class": 3,
        "light_sleep": 14400,  # 4 hours
        "deep_sleep": 7200,  # 2 hours
        "rem_sleep": 3600,  # 1 hour
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
    }

    sleep = SleepData(**data)

    assert sleep.polar_user == "12345678"
    assert sleep.date == date(2026, 1, 9)
    assert sleep.sleep_score == 85
    assert sleep.light_sleep == 14400
    assert sleep.deep_sleep == 7200
    assert sleep.rem_sleep == 3600


def test_sleep_data_computed_total_sleep() -> None:
    """Test total_sleep_seconds and total_sleep_hours computed properties."""
    sleep = SleepData(
        polar_user="123",
        date="2026-01-09",
        sleep_start_time="2026-01-08T22:00:00Z",
        sleep_end_time="2026-01-09T06:00:00Z",
        device_id="DEV123",
        continuity=3.0,
        continuity_class=3,
        light_sleep=14400,  # 4 hours
        deep_sleep=7200,  # 2 hours
        rem_sleep=3600,  # 1 hour
        unrecognized_sleep_stage=0,
        sleep_score=85,
        total_interruption_duration=600,
        sleep_charge=80,
        sleep_goal=28800,
        sleep_rating=4,
        short_interruption_duration=300,
        long_interruption_duration=300,
        sleep_cycles=5,
        group_duration_score=85.0,
        group_solidity_score=80.0,
        group_regeneration_score=90.0,
    )

    # Total: 14400 + 7200 + 3600 = 25200 seconds = 7 hours
    assert sleep.total_sleep_seconds == 25200
    assert sleep.total_sleep_hours == 7.0


def test_sleep_data_computed_time_in_bed() -> None:
    """Test time_in_bed computed properties."""
    sleep = SleepData(
        polar_user="123",
        date="2026-01-09",
        sleep_start_time="2026-01-08T22:00:00Z",  # 10 PM
        sleep_end_time="2026-01-09T06:00:00Z",  # 6 AM (8 hours later)
        device_id="DEV123",
        continuity=3.0,
        continuity_class=3,
        light_sleep=14400,
        deep_sleep=7200,
        rem_sleep=3600,
        unrecognized_sleep_stage=0,
        sleep_score=85,
        total_interruption_duration=600,
        sleep_charge=80,
        sleep_goal=28800,
        sleep_rating=4,
        short_interruption_duration=300,
        long_interruption_duration=300,
        sleep_cycles=5,
        group_duration_score=85.0,
        group_solidity_score=80.0,
        group_regeneration_score=90.0,
    )

    # 8 hours = 28800 seconds
    assert sleep.time_in_bed_seconds == 28800
    assert sleep.time_in_bed_hours == 8.0


def test_sleep_data_sleep_efficiency() -> None:
    """Test sleep_efficiency computed property."""
    sleep = SleepData(
        polar_user="123",
        date="2026-01-09",
        sleep_start_time="2026-01-08T22:00:00Z",
        sleep_end_time="2026-01-09T06:00:00Z",  # 8 hours in bed
        device_id="DEV123",
        continuity=3.0,
        continuity_class=3,
        light_sleep=14400,  # 4 hours
        deep_sleep=7200,  # 2 hours
        rem_sleep=3600,  # 1 hour = 7 hours total sleep
        unrecognized_sleep_stage=0,
        sleep_score=85,
        total_interruption_duration=3600,  # 1 hour interruption
        sleep_charge=80,
        sleep_goal=28800,
        sleep_rating=4,
        short_interruption_duration=300,
        long_interruption_duration=300,
        sleep_cycles=5,
        group_duration_score=85.0,
        group_solidity_score=80.0,
        group_regeneration_score=90.0,
    )

    # 7 hours sleep / 8 hours in bed = 87.5%
    assert sleep.sleep_efficiency == 87.5


def test_sleep_data_get_sleep_quality() -> None:
    """Test get_sleep_quality() method returns correct quality labels."""
    base_data = {
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
    }

    # Excellent: >= 85
    sleep = SleepData(**{**base_data, "sleep_score": 95})
    assert sleep.get_sleep_quality() == "Excellent"

    sleep = SleepData(**{**base_data, "sleep_score": 85})
    assert sleep.get_sleep_quality() == "Excellent"

    # Good: >= 70
    sleep = SleepData(**{**base_data, "sleep_score": 75})
    assert sleep.get_sleep_quality() == "Good"

    sleep = SleepData(**{**base_data, "sleep_score": 70})
    assert sleep.get_sleep_quality() == "Good"

    # Fair: >= 50
    sleep = SleepData(**{**base_data, "sleep_score": 60})
    assert sleep.get_sleep_quality() == "Fair"

    sleep = SleepData(**{**base_data, "sleep_score": 50})
    assert sleep.get_sleep_quality() == "Fair"

    # Poor: < 50
    sleep = SleepData(**{**base_data, "sleep_score": 45})
    assert sleep.get_sleep_quality() == "Poor"

    sleep = SleepData(**{**base_data, "sleep_score": 1})
    assert sleep.get_sleep_quality() == "Poor"


def test_sleep_data_optional_fields() -> None:
    """Test that optional fields can be None."""
    data = {
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
    }

    sleep = SleepData(**data)

    # Optional fields should be None
    assert sleep.heart_rate_avg is None
    assert sleep.heart_rate_min is None
    assert sleep.heart_rate_max is None
    assert sleep.hrv_avg is None
    assert sleep.breathing_rate_avg is None
    assert sleep.hypnogram is None
    assert sleep.heart_rate_samples is None


def test_sleep_data_with_optional_fields() -> None:
    """Test SleepData with optional physiological measurements."""
    data = {
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
        "heart_rate_avg": 55,
        "heart_rate_min": 45,
        "heart_rate_max": 65,
        "hrv_avg": 45.5,
        "breathing_rate_avg": 14.5,
    }

    sleep = SleepData(**data)

    assert sleep.heart_rate_avg == 55
    assert sleep.heart_rate_min == 45
    assert sleep.heart_rate_max == 65
    assert sleep.hrv_avg == 45.5
    assert sleep.breathing_rate_avg == 14.5


def test_sleep_data_datetime_parsing() -> None:
    """Test that ISO 8601 datetime strings are parsed correctly."""
    data = {
        "polar_user": "123",
        "date": "2026-01-09",
        "sleep_start_time": "2026-01-08T22:00:00Z",
        "sleep_end_time": "2026-01-09T06:00:00+00:00",
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
    }

    sleep = SleepData(**data)

    assert isinstance(sleep.sleep_start_time, datetime)
    assert isinstance(sleep.sleep_end_time, datetime)


def test_sleep_data_validation_sleep_score_range() -> None:
    """Test that sleep_score validation enforces 1-100 range."""
    base_data = {
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
    }

    # Valid: 1-100
    sleep = SleepData(**{**base_data, "sleep_score": 1})
    assert sleep.sleep_score == 1

    sleep = SleepData(**{**base_data, "sleep_score": 100})
    assert sleep.sleep_score == 100

    # Invalid: < 1
    with pytest.raises(ValidationError):
        SleepData(**{**base_data, "sleep_score": 0})

    # Invalid: > 100
    with pytest.raises(ValidationError):
        SleepData(**{**base_data, "sleep_score": 101})
