"""SleepWise endpoints for Polar AccessLink API.

Based on VERIFIED API testing of:
- GET /v3/users/sleepwise/alertness
- GET /v3/users/sleepwise/circadian-bedtime
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.sleepwise_alertness import SleepWiseAlertness
from polar_flow.models.sleepwise_bedtime import SleepWiseBedtime

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class SleepWiseEndpoint:
    """SleepWise endpoint for alertness and bedtime predictions.

    Provides access to SleepWise features including:
    - Alertness predictions based on sleep patterns
    - Circadian bedtime recommendations
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize SleepWise endpoint."""
        self.client = client

    async def get_alertness(self) -> list[SleepWiseAlertness]:
        """Get alertness predictions.

        Returns:
            List of alertness predictions with hourly data

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                alertness = await client.sleepwise.get_alertness()
                for a in alertness:
                    print(f"Grade: {a.grade}, Type: {a.grade_type}")
            ```
        """
        path = "/v3/users/sleepwise/alertness"
        response = await self.client._request("GET", path)

        if isinstance(response, list):
            return [SleepWiseAlertness.model_validate(item) for item in response]

        return []

    async def get_bedtime(self) -> list[SleepWiseBedtime]:
        """Get circadian bedtime recommendations.

        Returns:
            List of bedtime recommendations

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                bedtimes = await client.sleepwise.get_bedtime()
                for b in bedtimes:
                    print(f"Sleep gate: {b.sleep_gate_start_time} - {b.sleep_gate_end_time}")
            ```
        """
        path = "/v3/users/sleepwise/circadian-bedtime"
        response = await self.client._request("GET", path)

        if isinstance(response, list):
            return [SleepWiseBedtime.model_validate(item) for item in response]

        return []
