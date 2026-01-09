"""Pydantic models for user data."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExtraInfo(BaseModel):
    """Extra user information field."""

    model_config = ConfigDict(populate_by_name=True)

    value: str = Field(description="Field value")
    index: int = Field(description="Field index", ge=0)
    name: str = Field(description="Field name")


class UserInfo(BaseModel):
    """User information and profile data."""

    model_config = ConfigDict(populate_by_name=True)

    polar_user_id: int = Field(alias="polar-user-id", description="Polar user ID")
    member_id: str = Field(alias="member-id", description="Partner's custom identifier for user")
    registration_date: dt.datetime = Field(
        alias="registration-date", description="Registration timestamp"
    )
    first_name: str | None = Field(default=None, alias="first-name", description="First name")
    last_name: str | None = Field(default=None, alias="last-name", description="Last name")
    birthdate: str | None = Field(default=None, description="Birth date in YYYY-MM-DD format")
    gender: Literal["MALE", "FEMALE"] | None = Field(default=None, description="Gender")
    weight: float | None = Field(default=None, description="Weight in kg", gt=0)
    height: float | None = Field(default=None, description="Height in cm", gt=0)
    extra_info: list[ExtraInfo] | None = Field(
        default=None, alias="extra-info", description="Additional custom fields"
    )

    @field_validator("registration_date", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | dt.datetime) -> dt.datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, dt.datetime):
            return value
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


class UserRegistrationRequest(BaseModel):
    """User registration request."""

    model_config = ConfigDict(populate_by_name=True)

    member_id: str = Field(
        alias="member-id", description="Partner's custom identifier for user (unique)"
    )
