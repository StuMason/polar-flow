"""Pydantic models for Continuous Heart Rate data.

Based on VERIFIED API response from GET /v3/users/continuous-heart-rate/{date} (2026-01-10)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HeartRateSample(BaseModel):
    """Individual heart rate sample."""

    model_config = ConfigDict(populate_by_name=True)

    heart_rate: int = Field(alias="heart_rate", description="Heart rate in BPM")
    sample_time: str = Field(
        alias="sample_time",
        description="Time of sample (HH:MM:SS format)",
    )


class ContinuousHeartRate(BaseModel):
    """Continuous heart rate data for a day.

    Contains 5-minute interval heart rate samples throughout the day.
    """

    model_config = ConfigDict(populate_by_name=True)

    polar_user: str = Field(alias="polar_user", description="Polar user URL")
    date: str = Field(description="Date in YYYY-MM-DD format")
    heart_rate_samples: list[HeartRateSample] = Field(
        alias="heart_rate_samples",
        default_factory=list,
        description="Heart rate samples throughout the day",
    )
