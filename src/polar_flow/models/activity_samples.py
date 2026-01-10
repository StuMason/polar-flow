"""Pydantic models for Activity Samples data.

Based on VERIFIED API response from GET /v3/users/activities/samples (2026-01-10)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StepSample(BaseModel):
    """Individual step sample."""

    model_config = ConfigDict(populate_by_name=True)

    steps: int = Field(description="Number of steps in this interval")
    timestamp: str = Field(description="Timestamp of this sample")


class StepData(BaseModel):
    """Step data for a day."""

    model_config = ConfigDict(populate_by_name=True)

    interval_ms: int = Field(
        alias="interval_ms",
        description="Sample interval in milliseconds (60000 = 1 minute)",
    )
    total_steps: int = Field(alias="total_steps", description="Total steps for the day")
    samples: list[StepSample] = Field(
        default_factory=list,
        description="Minute-by-minute step samples",
    )


class DailyActivitySamples(BaseModel):
    """Activity samples for a single day.

    Contains minute-by-minute step data.
    """

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(description="Date in YYYY-MM-DD format")
    steps: StepData = Field(description="Step data for the day")
