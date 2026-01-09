"""Pydantic models for sleep data."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field, computed_field, field_validator


class SleepData(BaseModel):
    """Sleep tracking data for a single night.

    This model represents sleep data returned by the Polar AccessLink API,
    including sleep stages, quality metrics, and physiological measurements.
    """

    polar_user: str = Field(description="Polar user ID")
    date: dt.date = Field(description="Date of sleep (the day user woke up)")
    sleep_start_time: dt.datetime = Field(description="When sleep started")
    sleep_end_time: dt.datetime = Field(description="When sleep ended")
    device_id: str = Field(description="Device ID that recorded the sleep")
    continuity: float = Field(description="Sleep continuity score (1.0-5.0)", ge=1.0, le=5.0)
    continuity_class: int = Field(description="Sleep continuity classification (1-5)", ge=1, le=5)
    light_sleep: int = Field(description="Light sleep duration in seconds", ge=0)
    deep_sleep: int = Field(description="Deep sleep duration in seconds", ge=0)
    rem_sleep: int = Field(description="REM sleep duration in seconds", ge=0)
    unrecognized_sleep_stage: int = Field(
        description="Unrecognized sleep stage duration in seconds", ge=0
    )
    sleep_score: int = Field(description="Overall sleep quality score (1-100)", ge=1, le=100)
    total_interruption_duration: int = Field(
        description="Total interruption duration in seconds", ge=0
    )
    sleep_charge: int = Field(description="Sleep charge score (1-100)", ge=1, le=100)
    sleep_goal: int = Field(description="Sleep goal in seconds", ge=0)
    sleep_rating: int = Field(description="User's subjective sleep rating (1-5)", ge=1, le=5)
    short_interruption_duration: int = Field(
        description="Short interruption duration in seconds", ge=0
    )
    long_interruption_duration: int = Field(
        description="Long interruption duration in seconds", ge=0
    )
    sleep_cycles: int = Field(description="Number of sleep cycles", ge=0)
    group_duration_score: float = Field(description="Group duration score", ge=0.0, le=100.0)
    group_solidity_score: float = Field(description="Group solidity score", ge=0.0, le=100.0)
    group_regeneration_score: float = Field(
        description="Group regeneration score", ge=0.0, le=100.0
    )

    # Optional fields (may not be present for all users/devices)
    heart_rate_avg: int | None = Field(
        default=None, description="Average heart rate during sleep in BPM"
    )
    heart_rate_min: int | None = Field(
        default=None, description="Minimum heart rate during sleep in BPM"
    )
    heart_rate_max: int | None = Field(
        default=None, description="Maximum heart rate during sleep in BPM"
    )
    hrv_avg: float | None = Field(default=None, description="Average HRV in milliseconds")
    breathing_rate_avg: float | None = Field(
        default=None, description="Average breathing rate in breaths per minute"
    )
    hypnogram: dict[str, int] | None = Field(
        default=None, description="Hypnogram data (time → sleep stage mapping)"
    )
    heart_rate_samples: dict[str, int] | None = Field(
        default=None, description="Heart rate samples (time → BPM mapping)"
    )

    @field_validator("sleep_start_time", "sleep_end_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string to datetime object.

        Args:
            value: ISO 8601 datetime string or datetime object

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If datetime string is invalid
        """
        if isinstance(value, dt.datetime):
            return value
        # Handle both Z and +00:00 timezone formats
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_sleep_seconds(self) -> int:
        """Total sleep time excluding interruptions.

        Returns:
            Total sleep duration in seconds
        """
        return self.light_sleep + self.deep_sleep + self.rem_sleep

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_sleep_hours(self) -> float:
        """Total sleep time in hours.

        Returns:
            Total sleep duration in hours (rounded to 2 decimal places)
        """
        return round(self.total_sleep_seconds / 3600, 2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def time_in_bed_seconds(self) -> int:
        """Total time in bed from sleep start to sleep end.

        Returns:
            Time in bed in seconds
        """
        return int((self.sleep_end_time - self.sleep_start_time).total_seconds())

    @computed_field  # type: ignore[prop-decorator]
    @property
    def time_in_bed_hours(self) -> float:
        """Total time in bed in hours.

        Returns:
            Time in bed in hours (rounded to 2 decimal places)
        """
        return round(self.time_in_bed_seconds / 3600, 2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sleep_efficiency(self) -> float:
        """Percentage of time in bed actually sleeping.

        Returns:
            Sleep efficiency as a percentage (0-100)
        """
        if self.time_in_bed_seconds <= 0:
            return 0.0
        return round((self.total_sleep_seconds / self.time_in_bed_seconds) * 100, 2)

    def get_sleep_quality(self) -> str:
        """Get human-readable sleep quality based on sleep score.

        Returns:
            Sleep quality description: Excellent, Good, Fair, or Poor
        """
        if self.sleep_score >= 85:
            return "Excellent"
        if self.sleep_score >= 70:
            return "Good"
        if self.sleep_score >= 50:
            return "Fair"
        return "Poor"
