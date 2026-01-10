"""Pydantic models for SleepWise Circadian Bedtime data.

Based on VERIFIED API response from GET /v3/users/sleepwise/circadian-bedtime (2026-01-10)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SleepWiseBedtime(BaseModel):
    """SleepWise Circadian Bedtime recommendation.

    Provides optimal sleep timing predictions.
    """

    model_config = ConfigDict(populate_by_name=True)

    validity: str = Field(description="Validity of this prediction")
    quality: str = Field(
        description="Quality assessment (e.g., CIRCADIAN_BEDTIME_QUALITY_COMPROMISED)",
    )
    result_type: str = Field(
        alias="result_type",
        description="Type (e.g., CIRCADIAN_BEDTIME_TYPE_HISTORY or CIRCADIAN_BEDTIME_TYPE_PREDICTION)",
    )
    period_start_time: str = Field(
        alias="period_start_time",
        description="Start of sleep period",
    )
    period_end_time: str = Field(
        alias="period_end_time",
        description="End of sleep period",
    )
    preferred_sleep_period_start_time: str = Field(
        alias="preferred_sleep_period_start_time",
        description="Recommended time to start sleep",
    )
    preferred_sleep_period_end_time: str = Field(
        alias="preferred_sleep_period_end_time",
        description="Recommended time to end sleep",
    )
    sleep_gate_start_time: str = Field(
        alias="sleep_gate_start_time",
        description="Start of optimal sleep window",
    )
    sleep_gate_end_time: str = Field(
        alias="sleep_gate_end_time",
        description="End of optimal sleep window",
    )
    sleep_timezone_offset_minutes: int = Field(
        alias="sleep_timezone_offset_minutes",
        description="Timezone offset in minutes",
    )
