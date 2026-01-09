"""Pydantic models for physical information data."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PhysicalInfoTransaction(BaseModel):
    """Physical information transaction metadata."""

    model_config = ConfigDict(populate_by_name=True)

    transaction_id: int = Field(alias="transaction-id", description="Transaction ID")
    resource_uri: str = Field(alias="resource-uri", description="Resource URI for the transaction")


class PhysicalInformation(BaseModel):
    """Physical information entity with body metrics and fitness levels."""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(description="Physical information record ID")
    transaction_id: int = Field(alias="transaction-id", description="Associated transaction ID")
    created: dt.datetime = Field(description="Record creation timestamp")
    polar_user: str = Field(alias="polar-user", description="Link to user")
    weight: float | None = Field(default=None, description="Weight in kg", gt=0)
    height: float | None = Field(default=None, description="Height in cm", gt=0)
    maximum_heart_rate: int | None = Field(
        default=None, alias="maximum-heart-rate", description="Max heart rate in bpm", gt=0
    )
    resting_heart_rate: int | None = Field(
        default=None, alias="resting-heart-rate", description="Resting heart rate in bpm", gt=0
    )
    aerobic_threshold: int | None = Field(
        default=None, alias="aerobic-threshold", description="Aerobic threshold in bpm", gt=0
    )
    anaerobic_threshold: int | None = Field(
        default=None, alias="anaerobic-threshold", description="Anaerobic threshold in bpm", gt=0
    )
    vo2_max: int | None = Field(
        default=None, alias="vo2-max", description="VO2 max ml/kg/min", gt=0
    )
    weight_source: str | None = Field(
        default=None, alias="weight-source", description="Source of weight measurement"
    )

    @field_validator("created", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
