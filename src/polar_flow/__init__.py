"""Modern async Python client for Polar AccessLink API."""

from polar_flow.auth import OAuth2Handler, OAuth2Token, load_token_from_file
from polar_flow.client import PolarFlow
from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    PolarFlowError,
    RateLimitError,
    ValidationError,
)
from polar_flow.models.activity import Activity, ActivitySamples
from polar_flow.models.activity_samples import DailyActivitySamples, StepData, StepSample
from polar_flow.models.biosensing import (
    BodyTemperaturePeriod,
    ECGQualityMeasurement,
    ECGResult,
    ECGSample,
    SkinTemperature,
    SpO2Result,
    TemperatureSample,
)
from polar_flow.models.cardio_load import CardioLoad, CardioLoadLevel
from polar_flow.models.continuous_hr import ContinuousHeartRate, HeartRateSample
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
from polar_flow.models.sleepwise_alertness import AlertnessHourlyData, SleepWiseAlertness
from polar_flow.models.sleepwise_bedtime import SleepWiseBedtime
from polar_flow.models.user import UserInfo

__version__ = "1.4.0"
__all__ = [
    "Activity",
    "ActivitySamples",
    "AlertnessHourlyData",
    "AuthenticationError",
    "BodyTemperaturePeriod",
    "CardioLoad",
    "CardioLoadLevel",
    "ContinuousHeartRate",
    "DailyActivitySamples",
    "ECGQualityMeasurement",
    "ECGResult",
    "ECGSample",
    "Exercise",
    "ExerciseSample",
    "ExerciseSamples",
    "ExerciseZones",
    "HeartRateSample",
    "HeartRateZone",
    "NightlyRecharge",
    "NotFoundError",
    "OAuth2Handler",
    "OAuth2Token",
    "PhysicalInformation",
    "PolarFlow",
    "PolarFlowError",
    "RateLimitError",
    "SkinTemperature",
    "SleepData",
    "SleepWiseAlertness",
    "SleepWiseBedtime",
    "SpO2Result",
    "StepData",
    "StepSample",
    "TemperatureSample",
    "UserInfo",
    "ValidationError",
    "load_token_from_file",
]
