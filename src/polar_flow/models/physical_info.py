"""Pydantic models for physical information data."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserPhysicalInfo(BaseModel):
    """User's current physical information.

    Returned by the non-transactional ``GET /v3/users/physical-info``
    endpoint (added to AccessLink 13.01.2026). Uses snake_case keys,
    unlike the deprecated transaction-based entities.
    """

    model_config = ConfigDict(populate_by_name=True)

    weight: float | None = Field(default=None, description="Weight in kg", gt=0)
    height: float | None = Field(default=None, description="Height in cm", gt=0)
    created: dt.datetime | None = Field(default=None, description="Record creation timestamp")
    modified: dt.datetime | None = Field(default=None, description="Last modification timestamp")
    birthday: dt.date | None = Field(default=None, description="Date of birth")
    gender: str | None = Field(default=None, description="Gender (MALE/FEMALE)")
    maximum_heart_rate: int | None = Field(default=None, description="Max heart rate in bpm", gt=0)
    resting_heart_rate: int | None = Field(
        default=None, description="Resting heart rate in bpm", gt=0
    )
    aerobic_threshold: int | None = Field(
        default=None, description="Aerobic threshold in bpm", gt=0
    )
    anaerobic_threshold: int | None = Field(
        default=None, description="Anaerobic threshold in bpm", gt=0
    )
    vo2_max: int | None = Field(default=None, description="VO2 max ml/kg/min", gt=0)
    weight_source: str | None = Field(default=None, description="Source of weight measurement")
    training_background: str | None = Field(
        default=None, description="Training background (e.g. OCCASIONAL, REGULAR, PRO)"
    )
    typical_day: str | None = Field(
        default=None, description="Typical daily activity level (e.g. MOSTLY_SITTING)"
    )
    sleep_goal: str | None = Field(
        default=None, description="Sleep goal as ISO 8601 duration (e.g. PT8H)"
    )

    @field_validator("created", "modified", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime | None) -> dt.datetime | None:
        """Parse ISO 8601 datetime string."""
        if value is None or isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class PhysicalInfoTransaction(BaseModel):
    """Physical information transaction metadata.

    .. deprecated:: 1.5.0
        The transactional physical-info flow was deprecated by Polar
        (13.01.2026 changelog). Use ``client.physical_info.get()`` instead.
    """

    model_config = ConfigDict(populate_by_name=True)

    transaction_id: int = Field(alias="transaction-id", description="Transaction ID")
    resource_uri: str = Field(alias="resource-uri", description="Resource URI for the transaction")


class PhysicalInformation(BaseModel):
    """Physical information entity with body metrics and fitness levels.

    .. deprecated:: 1.5.0
        Returned by the transaction-based flow, which Polar deprecated
        (13.01.2026 changelog). Use ``client.physical_info.get()`` and
        :class:`UserPhysicalInfo` instead.
    """

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
