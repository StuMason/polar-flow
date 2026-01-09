"""Pydantic models for nightly recharge data."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NightlyRecharge(BaseModel):
    """Nightly recharge recovery data.

    Represents autonomic nervous system (ANS) recovery and sleep quality metrics.
    """

    model_config = ConfigDict(populate_by_name=True)

    polar_user: str = Field(alias="polar-user", description="Polar user ID")
    date: str = Field(description="Recovery date in YYYY-MM-DD format")
    heart_rate_avg: int = Field(
        alias="heart-rate-avg",
        description="Average heart rate during 4-hour recovery period (bpm)",
        ge=0,
    )
    beat_to_beat_avg: int = Field(
        alias="beat-to-beat-avg",
        description="Average milliseconds between heartbeats",
        ge=0,
    )
    heart_rate_variability_avg: int = Field(
        alias="heart-rate-variability-avg",
        description="RMSSD heart rate variability (ms)",
        ge=0,
    )
    breathing_rate_avg: float = Field(
        alias="breathing-rate-avg",
        description="Average breathing rate (breaths per minute)",
        ge=0,
    )
    nightly_recharge_status: int = Field(
        alias="nightly-recharge-status",
        description="Recovery status scale 1-6 (1=compromised, 6=excellent)",
        ge=1,
        le=6,
    )
    ans_charge: float = Field(
        alias="ans-charge",
        description="Autonomic nervous system charge (-10.0 to +10.0)",
        ge=-10.0,
        le=10.0,
    )
    ans_charge_status: int = Field(
        alias="ans-charge-status",
        description="ANS charge status scale 1-5",
        ge=1,
        le=5,
    )
    hrv_samples: dict[str, int] | None = Field(
        default=None,
        alias="hrv-samples",
        description="5-minute HRV averages (timestamp: milliseconds)",
    )
    breathing_samples: dict[str, float] | None = Field(
        default=None,
        alias="breathing-samples",
        description="5-minute breathing rate averages (timestamp: breaths/min)",
    )
