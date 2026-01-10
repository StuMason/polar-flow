"""Pydantic models for cardio load data.

Based on VERIFIED API response from GET /v3/users/cardio-load:
{
  "cardio_load_level": {
    "very_low": 0.0,
    "low": 0.0,
    "medium": 0.0,
    "high": 0.0,
    "very_high": 0.0
  },
  "date": "2025-12-14",
  "cardio_load_status": "LOAD_STATUS_NOT_AVAILABLE",
  "cardio_load_ratio": -1.0,
  "cardio_load": -1.0,
  "strain": 0.0,
  "tolerance": -1.0
}
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CardioLoadLevel(BaseModel):
    """Cardio load distribution across intensity levels."""

    model_config = ConfigDict(populate_by_name=True)

    very_low: float = Field(default=0.0, alias="very_low", description="Very low intensity load")
    low: float = Field(default=0.0, description="Low intensity load")
    medium: float = Field(default=0.0, description="Medium intensity load")
    high: float = Field(default=0.0, description="High intensity load")
    very_high: float = Field(default=0.0, alias="very_high", description="Very high intensity load")


class CardioLoad(BaseModel):
    """Cardio load data for a single day.

    Represents training load and recovery metrics.
    """

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(description="Date in YYYY-MM-DD format")
    cardio_load: float = Field(
        alias="cardio_load",
        description="Overall cardio load value (-1.0 if not available)",
    )
    cardio_load_status: str = Field(
        alias="cardio_load_status",
        description="Load status (e.g., LOAD_STATUS_NOT_AVAILABLE)",
    )
    cardio_load_ratio: float = Field(
        alias="cardio_load_ratio",
        description="Load ratio (-1.0 if not available)",
    )
    strain: float = Field(description="Training strain value")
    tolerance: float = Field(description="Training tolerance value (-1.0 if not available)")
    cardio_load_level: CardioLoadLevel = Field(
        alias="cardio_load_level",
        description="Load distribution across intensity levels",
    )
