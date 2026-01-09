"""Modern async Python client for Polar AccessLink API."""

from polar_flow.auth import OAuth2Handler, OAuth2Token
from polar_flow.client import PolarFlow
from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    PolarFlowError,
    RateLimitError,
    ValidationError,
)
from polar_flow.models.activity import Activity, ActivitySamples
from polar_flow.models.exercise import (
    Exercise,
    ExerciseSample,
    ExerciseSamples,
    ExerciseZones,
    HeartRateZone,
)
from polar_flow.models.physical_info import PhysicalInformation
from polar_flow.models.recharge import NightlyRecharge
from polar_flow.models.sleep import SleepData
from polar_flow.models.user import UserInfo

__version__ = "1.0.0"
__all__ = [
    "Activity",
    "ActivitySamples",
    "AuthenticationError",
    "Exercise",
    "ExerciseSample",
    "ExerciseSamples",
    "ExerciseZones",
    "HeartRateZone",
    "NightlyRecharge",
    "NotFoundError",
    "OAuth2Handler",
    "OAuth2Token",
    "PhysicalInformation",
    "PolarFlow",
    "PolarFlowError",
    "RateLimitError",
    "SleepData",
    "UserInfo",
    "ValidationError",
]
