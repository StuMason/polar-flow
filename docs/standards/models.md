# Pydantic Model Standards

## Model Structure

**Use Pydantic 2.x with comprehensive field descriptions:**

```python
from pydantic import BaseModel, Field
from datetime import date, datetime

class SleepData(BaseModel):
    """Sleep tracking data for a single night.

    This model represents sleep data returned by the Polar AccessLink API,
    including sleep stages, quality metrics, and physiological measurements.
    """

    polar_user: str = Field(description="Polar user ID")
    date: date = Field(description="Date of sleep (the day user woke up)")
    sleep_start_time: datetime = Field(description="When sleep started")
    sleep_end_time: datetime = Field(description="When sleep ended")
    sleep_score: int = Field(ge=0, le=100, description="Overall sleep quality score")
    light_sleep: int = Field(description="Light sleep duration in seconds")
    deep_sleep: int = Field(description="Deep sleep duration in seconds")
    rem_sleep: int = Field(description="REM sleep duration in seconds")
    hrv_avg: float | None = Field(default=None, description="Average HRV in milliseconds")
```

## Field Validation

**Add validation rules using Field():**

```python
from pydantic import Field, field_validator

class SleepData(BaseModel):
    """Sleep data model."""

    sleep_score: int = Field(ge=0, le=100, description="Sleep score 0-100")
    heart_rate_avg: int = Field(gt=0, lt=300, description="Average heart rate in BPM")

    @field_validator("sleep_score")
    @classmethod
    def validate_sleep_score(cls, value: int) -> int:
        """Ensure sleep score is reasonable."""
        if value < 0 or value > 100:
            raise ValueError("Sleep score must be between 0 and 100")
        return value
```

## Computed Properties

**Add computed properties for derived values:**

```python
from pydantic import BaseModel, computed_field

class SleepData(BaseModel):
    """Sleep data with computed properties."""

    light_sleep: int  # seconds
    deep_sleep: int   # seconds
    rem_sleep: int    # seconds
    sleep_start_time: datetime
    sleep_end_time: datetime

    @computed_field
    @property
    def total_sleep_seconds(self) -> int:
        """Total sleep time excluding interruptions."""
        return self.light_sleep + self.deep_sleep + self.rem_sleep

    @computed_field
    @property
    def total_sleep_hours(self) -> float:
        """Total sleep time in hours."""
        return self.total_sleep_seconds / 3600

    @computed_field
    @property
    def sleep_efficiency(self) -> float:
        """Percentage of time in bed actually sleeping."""
        time_in_bed = (self.sleep_end_time - self.sleep_start_time).total_seconds()
        if time_in_bed <= 0:
            return 0.0
        return (self.total_sleep_seconds / time_in_bed) * 100
```

## Optional Fields

**Use None for optional fields with clear defaults:**

```python
class ExerciseData(BaseModel):
    """Exercise data model."""

    # Required fields
    exercise_id: str
    start_time: datetime
    duration: int

    # Optional fields with None default
    distance: float | None = None
    calories: int | None = None
    avg_heart_rate: int | None = None

    # Optional fields with specific defaults
    sport: str = "OTHER"
    has_route: bool = False
```

## Model Configuration

**Use model_config for Pydantic settings:**

```python
from pydantic import BaseModel, ConfigDict

class SleepData(BaseModel):
    """Sleep data model with configuration."""

    model_config = ConfigDict(
        # Allow validation from dict attributes
        from_attributes=True,
        # Be strict about extra fields
        extra="forbid",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate default values
        validate_default=True,
        # Validate assignments after model creation
        validate_assignment=True,
    )
```

## Nested Models

**Use nested models for complex structures:**

```python
class HeartRateZone(BaseModel):
    """Heart rate zone data."""

    zone_index: int = Field(ge=0, le=5)
    duration: int = Field(ge=0, description="Time in zone (seconds)")
    zone_name: str

class ExerciseData(BaseModel):
    """Exercise with heart rate zones."""

    exercise_id: str
    duration: int
    heart_rate_zones: list[HeartRateZone] = []

    @computed_field
    @property
    def total_zone_time(self) -> int:
        """Total time across all heart rate zones."""
        return sum(zone.duration for zone in self.heart_rate_zones)
```

## Datetime Handling

**Handle ISO 8601 datetime strings:**

```python
from datetime import datetime, date
from pydantic import BaseModel, field_validator

class SleepData(BaseModel):
    """Sleep data with datetime handling."""

    date: date
    sleep_start_time: datetime
    sleep_end_time: datetime

    @field_validator("sleep_start_time", "sleep_end_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | datetime) -> datetime:
        """Parse ISO 8601 datetime string."""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
```

## Model Methods

**Add helper methods for common operations:**

```python
class SleepData(BaseModel):
    """Sleep data with helper methods."""

    sleep_score: int
    light_sleep: int
    deep_sleep: int
    rem_sleep: int

    def get_sleep_quality(self) -> str:
        """Get human-readable sleep quality."""
        if self.sleep_score >= 85:
            return "Excellent"
        if self.sleep_score >= 70:
            return "Good"
        if self.sleep_score >= 50:
            return "Fair"
        return "Poor"

    def to_summary(self) -> dict[str, str]:
        """Get a summary dictionary for display."""
        return {
            "quality": self.get_sleep_quality(),
            "score": f"{self.sleep_score}/100",
            "total_hours": f"{self.total_sleep_hours:.1f}h",
        }
```

## List Models

**Create container models for list responses:**

```python
class SleepDataList(BaseModel):
    """Container for multiple sleep data records."""

    items: list[SleepData] = []
    total_count: int = 0

    @computed_field
    @property
    def average_score(self) -> float:
        """Calculate average sleep score."""
        if not self.items:
            return 0.0
        return sum(item.sleep_score for item in self.items) / len(self.items)
```

## Serialization

**Control JSON serialization:**

```python
class SleepData(BaseModel):
    """Sleep data with custom serialization."""

    model_config = ConfigDict(
        # Exclude None values from dict
        exclude_none=True,
        # Serialize datetime as ISO 8601
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
    )

    def to_json(self) -> str:
        """Export as JSON string."""
        return self.model_dump_json(exclude_none=True, indent=2)
```
