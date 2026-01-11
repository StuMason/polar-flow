"""Biosensing models for Polar Elixir features.

SpO2, ECG, and Temperature data from compatible Polar devices.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# SpO2 Models


class SpO2Result(BaseModel):
    """Single SpO2 test result."""

    source_device_id: str = Field(description="Device that recorded the measurement")
    test_time: int = Field(description="Unix timestamp (milliseconds)")
    time_zone_offset: int = Field(description="Timezone offset in minutes")
    test_status: str = Field(description="Test completion status")
    blood_oxygen_percent: int = Field(ge=0, le=100, description="SpO2 percentage")
    spo2_class: str = Field(description="Classification (NORMAL, LOW, etc.)")
    spo2_value_deviation_from_baseline: str = Field(
        description="Deviation from user's baseline"
    )
    spo2_quality_average_percent: float = Field(
        description="Signal quality percentage"
    )
    average_heart_rate_bpm: int = Field(description="Average HR during test")
    heart_rate_variability_ms: float = Field(description="HRV in milliseconds")
    spo2_hrv_deviation_from_baseline: str = Field(
        description="HRV deviation from baseline"
    )
    altitude_meters: float | None = Field(default=None, description="Altitude if available")

    @property
    def test_datetime(self) -> datetime:
        """Convert test_time to datetime."""
        return datetime.fromtimestamp(self.test_time / 1000)


# ECG Models


class ECGSample(BaseModel):
    """Single ECG waveform sample."""

    recording_time_delta_ms: int = Field(description="Time offset from test start (ms)")
    amplitude_mv: float = Field(description="ECG amplitude in millivolts")


class ECGQualityMeasurement(BaseModel):
    """ECG signal quality at a point in time."""

    recording_time_delta_ms: int = Field(description="Time offset from test start (ms)")
    quality_level: str = Field(description="Signal quality level")


class ECGResult(BaseModel):
    """Single ECG test result with waveform data."""

    source_device_id: str = Field(description="Device that recorded the measurement")
    test_time: int = Field(description="Unix timestamp (milliseconds)")
    time_zone_offset: int = Field(description="Timezone offset in minutes")
    average_heart_rate_bpm: int = Field(description="Average HR during test")
    heart_rate_variability_ms: float = Field(description="HRV in milliseconds (RMSSD)")
    heart_rate_variability_level: str = Field(
        description="HRV classification (LOW, NORMAL, HIGH)"
    )
    rri_ms: float = Field(description="R-R interval in milliseconds")
    pulse_transit_time_systolic_ms: float | None = Field(
        default=None, description="PTT systolic"
    )
    pulse_transit_time_diastolic_ms: float | None = Field(
        default=None, description="PTT diastolic"
    )
    pulse_transit_time_quality_index: float | None = Field(
        default=None, description="PTT quality index"
    )
    samples: list[ECGSample] = Field(default_factory=list, description="ECG waveform samples")
    quality_measurements: list[ECGQualityMeasurement] = Field(
        default_factory=list, description="Signal quality over time"
    )

    @property
    def test_datetime(self) -> datetime:
        """Convert test_time to datetime."""
        return datetime.fromtimestamp(self.test_time / 1000)

    @property
    def duration_seconds(self) -> float:
        """Calculate test duration from samples."""
        if not self.samples:
            return 0.0
        return max(s.recording_time_delta_ms for s in self.samples) / 1000


# Temperature Models


class TemperatureSample(BaseModel):
    """Single temperature measurement sample."""

    temperature_celsius: float = Field(description="Temperature in Celsius")
    recording_time_delta_milliseconds: int = Field(
        description="Time offset from period start (ms)"
    )


class BodyTemperaturePeriod(BaseModel):
    """Body temperature measurement period with samples."""

    source_device_id: str = Field(description="Device that recorded the measurement")
    measurement_type: str = Field(description="Type of measurement")
    sensor_location: str = Field(description="Where sensor was placed")
    start_time: str = Field(description="ISO 8601 period start time")
    end_time: str = Field(description="ISO 8601 period end time")
    modified_time: str = Field(description="ISO 8601 last modification time")
    samples: list[TemperatureSample] = Field(
        default_factory=list, description="Temperature samples"
    )

    @property
    def start_datetime(self) -> datetime:
        """Parse start_time to datetime."""
        return datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))

    @property
    def end_datetime(self) -> datetime:
        """Parse end_time to datetime."""
        return datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))

    @property
    def avg_temperature(self) -> float | None:
        """Calculate average temperature from samples."""
        if not self.samples:
            return None
        return sum(s.temperature_celsius for s in self.samples) / len(self.samples)

    @property
    def min_temperature(self) -> float | None:
        """Get minimum temperature from samples."""
        if not self.samples:
            return None
        return min(s.temperature_celsius for s in self.samples)

    @property
    def max_temperature(self) -> float | None:
        """Get maximum temperature from samples."""
        if not self.samples:
            return None
        return max(s.temperature_celsius for s in self.samples)


class SkinTemperature(BaseModel):
    """Sleep skin temperature with baseline deviation."""

    sleep_time_skin_temperature_celsius: float = Field(
        description="Skin temperature during sleep"
    )
    deviation_from_baseline_celsius: float = Field(
        description="Deviation from user's baseline"
    )
    sleep_date: str = Field(description="Date of sleep (YYYY-MM-DD)")

    @property
    def is_elevated(self) -> bool:
        """Check if temperature is elevated (>0.5C above baseline)."""
        return self.deviation_from_baseline_celsius > 0.5

    @property
    def is_low(self) -> bool:
        """Check if temperature is low (<-0.5C below baseline)."""
        return self.deviation_from_baseline_celsius < -0.5
