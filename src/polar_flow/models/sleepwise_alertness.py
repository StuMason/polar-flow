"""Pydantic models for SleepWise Alertness data.

Based on VERIFIED API response from GET /v3/users/sleepwise/alertness (2026-01-10)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AlertnessHourlyData(BaseModel):
    """Hourly alertness level data."""

    model_config = ConfigDict(populate_by_name=True)

    validity: str = Field(description="Validity of this data point")
    alertness_level: str = Field(
        alias="alertness_level",
        description="Alertness level (ALERTNESS_LEVEL_MINIMAL, ALERTNESS_LEVEL_VERY_LOW, etc.)",
    )
    start_time: str = Field(alias="start_time", description="Start time of this hour")
    end_time: str = Field(alias="end_time", description="End time of this hour")


class SleepWiseAlertness(BaseModel):
    """SleepWise Alertness prediction data.

    Provides alertness predictions based on sleep patterns.
    """

    model_config = ConfigDict(populate_by_name=True)

    grade: float = Field(description="Alertness grade")
    grade_validity_seconds: int = Field(
        alias="grade_validity_seconds",
        description="How long the grade is valid for in seconds",
    )
    grade_type: str = Field(
        alias="grade_type",
        description="Type of grade (e.g., GRADE_TYPE_PRIMARY)",
    )
    grade_classification: str = Field(
        alias="grade_classification",
        description="Classification (e.g., GRADE_CLASSIFICATION_WEAK)",
    )
    validity: str = Field(description="Overall validity")
    sleep_inertia: str = Field(
        alias="sleep_inertia",
        description="Sleep inertia level (e.g., SLEEP_INERTIA_MODERATE)",
    )
    sleep_type: str = Field(
        alias="sleep_type",
        description="Type of sleep (e.g., SLEEP_TYPE_PRIMARY)",
    )
    result_type: str = Field(
        alias="result_type",
        description="Result type (e.g., ALERTNESS_TYPE_HISTORY)",
    )
    period_start_time: str = Field(
        alias="period_start_time",
        description="Start of alertness period",
    )
    period_end_time: str = Field(
        alias="period_end_time",
        description="End of alertness period",
    )
    sleep_period_start_time: str = Field(
        alias="sleep_period_start_time",
        description="When sleep started",
    )
    sleep_period_end_time: str = Field(
        alias="sleep_period_end_time",
        description="When sleep ended",
    )
    sleep_timezone_offset_minutes: int = Field(
        alias="sleep_timezone_offset_minutes",
        description="Timezone offset in minutes",
    )
    hourly_data: list[AlertnessHourlyData] = Field(
        alias="hourly_data",
        default_factory=list,
        description="Hourly alertness predictions",
    )
