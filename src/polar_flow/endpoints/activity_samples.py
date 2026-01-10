"""Activity Samples endpoint for Polar AccessLink API.

Based on VERIFIED API testing of GET /v3/users/activities/samples
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from polar_flow.models.activity_samples import DailyActivitySamples

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class ActivitySamplesEndpoint:
    """Activity Samples endpoint for minute-by-minute activity data.

    Provides access to detailed step samples at 1-minute intervals.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize Activity Samples endpoint."""
        self.client = client

    async def list(
        self,
        *,
        from_date: str | date | None = None,
        to_date: str | date | None = None,
        days: int = 7,
    ) -> list[DailyActivitySamples]:
        """Get activity samples for a date range.

        Args:
            from_date: Start date (YYYY-MM-DD or date object)
            to_date: End date (YYYY-MM-DD or date object). Defaults to today.
            days: Number of days if from_date not specified. Defaults to 7.

        Returns:
            List of daily activity samples with minute-by-minute step data

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                samples = await client.activity_samples.list(days=3)
                for day in samples:
                    print(f"{day.date}: {day.steps.total_steps} total steps")
            ```
        """
        # Determine date range
        end = date.today() if to_date is None else (
            date.fromisoformat(to_date) if isinstance(to_date, str) else to_date
        )
        start = end - timedelta(days=days - 1) if from_date is None else (
            date.fromisoformat(from_date) if isinstance(from_date, str) else from_date
        )

        path = f"/v3/users/activities/samples?from={start}&to={end}"
        response = await self.client._request("GET", path)

        if isinstance(response, list):
            return [DailyActivitySamples.model_validate(item) for item in response]

        return []
