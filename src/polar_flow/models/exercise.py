"""Pydantic models for exercise data."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class Exercise(BaseModel):
    """Exercise (training session) data.

    Represents a single training session/workout from a Polar device.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Unique exercise identifier")
    upload_time: dt.datetime = Field(
        alias="upload-time", description="When the exercise was uploaded"
    )
    polar_user: str = Field(alias="polar-user", description="Polar user ID")
    device: str = Field(description="Device name/identifier")
    device_id: str | None = Field(
        default=None, alias="device-id", description="Unique device identifier"
    )
    start_time: dt.datetime = Field(alias="start-time", description="Exercise start time")
    start_time_utc_offset: int = Field(
        alias="start-time-utc-offset", description="UTC offset in minutes"
    )
    duration: str = Field(description="Exercise duration in ISO 8601 format (PT2H30M)")
    calories: int | None = Field(default=None, description="Total calories burned", ge=0)
    distance: float | None = Field(default=None, description="Total distance in meters")
    heart_rate: dict[str, int] | None = Field(
        default=None, alias="heart-rate", description="Heart rate statistics (average, maximum)"
    )
    training_load: float | None = Field(
        default=None, alias="training-load", description="Training load value", ge=0
    )
    sport: str = Field(description="Sport type (e.g., 'RUNNING', 'CYCLING')")
    has_route: bool = Field(
        default=False, alias="has-route", description="Whether exercise includes GPS route data"
    )
    club_id: int | None = Field(default=None, alias="club-id", description="Club ID if shared")
    club_name: str | None = Field(
        default=None, alias="club-name", description="Club name if shared"
    )
    detailed_sport_info: str | None = Field(
        default=None, alias="detailed-sport-info", description="Detailed sport information"
    )
    fat_percentage: int | None = Field(
        default=None, alias="fat-percentage", description="Fat percentage of calories", ge=0, le=100
    )
    carbohydrate_percentage: int | None = Field(
        default=None,
        alias="carbohydrate-percentage",
        description="Carbohydrate percentage of calories",
        ge=0,
        le=100,
    )
    protein_percentage: int | None = Field(
        default=None,
        alias="protein-percentage",
        description="Protein percentage of calories",
        ge=0,
        le=100,
    )
    running_index: int | None = Field(
        default=None, alias="running-index", description="Running performance index"
    )
    training_load_pro: dict[str, float | str] | None = Field(
        default=None,
        alias="training-load-pro",
        description="Training Load Pro data (cardio, muscle, perceived). Values can be floats or strings like 'NOT_AVAILABLE'.",
    )

    @field_validator("upload_time", "start_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_seconds(self) -> int:
        """Parse ISO 8601 duration to seconds.

        Returns:
            Duration in seconds
        """
        # Parse ISO 8601 duration format PT2H30M15S
        import re

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
        match = re.match(pattern, self.duration)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = float(match.group(3) or 0)

        return int(hours * 3600 + minutes * 60 + seconds)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_minutes(self) -> float:
        """Exercise duration in minutes.

        Returns:
            Duration in minutes (rounded to 1 decimal place)
        """
        return round(self.duration_seconds / 60, 1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def distance_km(self) -> float | None:
        """Distance in kilometers.

        Returns:
            Distance in km (rounded to 2 decimal places) or None
        """
        if self.distance is None:
            return None
        return round(self.distance / 1000, 2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def average_heart_rate(self) -> int | None:
        """Average heart rate in BPM.

        Returns:
            Average HR or None
        """
        if self.heart_rate:
            return self.heart_rate.get("average")
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def maximum_heart_rate(self) -> int | None:
        """Maximum heart rate in BPM.

        Returns:
            Maximum HR or None
        """
        if self.heart_rate:
            return self.heart_rate.get("maximum")
        return None


class ExerciseSample(BaseModel):
    """Single sample point from exercise."""

    model_config = ConfigDict(populate_by_name=True)

    sample_type: str = Field(
        alias="sample-type", description="Type of sample (e.g., 'HEARTRATE', 'SPEED')"
    )
    recording_rate: int = Field(
        alias="recording-rate", description="Sample recording rate in seconds"
    )
    values: list[float | str] = Field(alias="data", description="Sample values")

    @field_validator("values", mode="before")
    @classmethod
    def convert_values(cls, value: list[float | str] | str) -> list[float | str]:
        """Convert values to list if needed.

        Args:
            value: Values as list or comma-separated string

        Returns:
            List of values
        """
        if isinstance(value, str):
            return [float(x) for x in value.split(",") if x.strip()]
        return value


class ExerciseSamples(BaseModel):
    """Exercise samples data (HR, speed, cadence, etc.)."""

    samples: list[ExerciseSample] = []

    def get_sample_by_type(self, sample_type: str) -> ExerciseSample | None:
        """Get sample by type.

        Args:
            sample_type: Sample type to find (e.g., 'HEARTRATE')

        Returns:
            Sample or None if not found
        """
        for sample in self.samples:
            if sample.sample_type.upper() == sample_type.upper():
                return sample
        return None


class HeartRateZone(BaseModel):
    """Heart rate zone data for exercise."""

    model_config = ConfigDict(populate_by_name=True)

    index: int = Field(description="Zone index (1-5)", ge=1, le=5)
    lower_limit: int = Field(alias="lower-limit", description="Lower HR limit in BPM", ge=0)
    upper_limit: int = Field(alias="upper-limit", description="Upper HR limit in BPM", ge=0)
    in_zone: str = Field(alias="in-zone", description="Time in zone (ISO 8601 duration)")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def in_zone_seconds(self) -> int:
        """Parse time in zone to seconds.

        Returns:
            Time in zone in seconds
        """
        import re

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?"
        match = re.match(pattern, self.in_zone)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = float(match.group(3) or 0)

        return int(hours * 3600 + minutes * 60 + seconds)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def in_zone_minutes(self) -> float:
        """Time in zone in minutes.

        Returns:
            Time in minutes (rounded to 1 decimal place)
        """
        return round(self.in_zone_seconds / 60, 1)


class ExerciseZones(BaseModel):
    """Heart rate zones for exercise."""

    zones: list[HeartRateZone] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_time_seconds(self) -> int:
        """Total time across all zones.

        Returns:
            Total time in seconds
        """
        return sum(zone.in_zone_seconds for zone in self.zones)
