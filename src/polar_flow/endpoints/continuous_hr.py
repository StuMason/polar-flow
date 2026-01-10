"""Continuous Heart Rate endpoint for Polar AccessLink API.

Based on VERIFIED API testing of GET /v3/users/continuous-heart-rate/{date}
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from polar_flow.models.continuous_hr import ContinuousHeartRate

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class ContinuousHREndpoint:
    """Continuous Heart Rate endpoint for all-day heart rate data.

    Provides access to heart rate samples at ~5 minute intervals throughout the day.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize Continuous HR endpoint."""
        self.client = client

    async def get(self, target_date: str | date | None = None) -> ContinuousHeartRate | None:
        """Get continuous heart rate data for a specific date.

        Args:
            target_date: Date to get data for (YYYY-MM-DD or date object). Defaults to today.

        Returns:
            Continuous heart rate data, or None if not available

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                hr = await client.continuous_hr.get()
                if hr:
                    print(f"Samples: {len(hr.heart_rate_samples)}")
            ```
        """
        if target_date is None:
            target_date = date.today()
        date_str = target_date if isinstance(target_date, str) else target_date.isoformat()

        path = f"/v3/users/continuous-heart-rate/{date_str}"
        try:
            response = await self.client._request("GET", path)
            return ContinuousHeartRate.model_validate(response)
        except Exception:
            return None
