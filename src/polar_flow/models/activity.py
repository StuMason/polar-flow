"""Pydantic models for activity data."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class StepSample(BaseModel):
    """Single step sample with timestamp."""

    model_config = ConfigDict(populate_by_name=True)

    steps: int = Field(description="Number of steps in this sample")
    timestamp: dt.datetime = Field(description="Sample timestamp")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class StepsSamples(BaseModel):
    """Steps samples data."""

    model_config = ConfigDict(populate_by_name=True)

    interval_ms: int = Field(alias="interval-ms", description="Sampling interval in milliseconds")
    total_steps: int = Field(alias="total-steps", description="Total steps for the day")
    samples: list[StepSample] = Field(description="Individual step samples")


class ActivityZoneSample(BaseModel):
    """Activity zone classification sample."""

    model_config = ConfigDict(populate_by_name=True)

    zone: Literal["SEDENTARY", "LIGHT", "SLEEP", "MODERATE", "VIGOROUS"] = Field(
        description="Activity intensity zone"
    )
    timestamp: dt.datetime = Field(description="Sample timestamp")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class ActivityZones(BaseModel):
    """Activity zones data."""

    samples: list[ActivityZoneSample] = Field(description="Activity zone samples")


class InactivityStamp(BaseModel):
    """Inactivity alert timestamp."""

    stamp: dt.datetime = Field(description="Inactivity alert timestamp")

    @field_validator("stamp", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class ActivitySamples(BaseModel):
    """Activity samples for a specific date."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(description="Date in YYYY-MM-DD format")
    steps: StepsSamples | None = Field(default=None, description="Steps samples data")
    activity_zones: ActivityZones | None = Field(
        default=None, alias="activity-zones", description="Activity zones data"
    )
    inactivity_stamps: list[InactivityStamp] | None = Field(
        default=None, alias="inactivity-stamps", description="Inactivity alert timestamps"
    )


class Activity(BaseModel):
    """Daily activity summary with optional samples.

    Represents a full day of activity data from a Polar device.
    """

    model_config = ConfigDict(populate_by_name=True)

    start_time: dt.datetime = Field(alias="start-time", description="Activity period start time")
    end_time: dt.datetime = Field(alias="end-time", description="Activity period end time")
    active_duration: str = Field(
        alias="active-duration", description="Active time in ISO 8601 duration format"
    )
    inactive_duration: str = Field(
        alias="inactive-duration", description="Inactive time in ISO 8601 duration format"
    )
    daily_activity: float = Field(alias="daily-activity", description="Daily activity score", ge=0)
    calories: int = Field(description="Total calories burned", ge=0)
    active_calories: int = Field(
        alias="active-calories", description="Active calories burned", ge=0
    )
    steps: int = Field(description="Total steps taken", ge=0)
    inactivity_alert_count: int = Field(
        alias="inactivity-alert-count", description="Number of inactivity alerts", ge=0
    )
    distance_from_steps: float = Field(
        alias="distance-from-steps", description="Distance in meters from steps", ge=0
    )
    samples: ActivitySamples | None = Field(
        default=None, description="Detailed activity samples (if requested)"
    )

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_duration_seconds(self) -> int:
        """Parse ISO 8601 active duration to seconds.

        Returns:
            Active duration in seconds
        """
        import re

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
        match = re.match(pattern, self.active_duration)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = float(match.group(3) or 0)

        return int(hours * 3600 + minutes * 60 + seconds)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_duration_minutes(self) -> float:
        """Active duration in minutes.

        Returns:
            Active duration in minutes (rounded to 1 decimal place)
        """
        return round(self.active_duration_seconds / 60, 1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def inactive_duration_seconds(self) -> int:
        """Parse ISO 8601 inactive duration to seconds.

        Returns:
            Inactive duration in seconds
        """
        import re

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
        match = re.match(pattern, self.inactive_duration)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = float(match.group(3) or 0)

        return int(hours * 3600 + minutes * 60 + seconds)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def inactive_duration_minutes(self) -> float:
        """Inactive duration in minutes.

        Returns:
            Inactive duration in minutes (rounded to 1 decimal place)
        """
        return round(self.inactive_duration_seconds / 60, 1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def distance_km(self) -> float:
        """Distance in kilometers.

        Returns:
            Distance in km (rounded to 2 decimal places)
        """
        return round(self.distance_from_steps / 1000, 2)
