"""Cardio load endpoint for Polar AccessLink API.

Based on VERIFIED API testing of GET /v3/users/cardio-load
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.cardio_load import CardioLoad

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class CardioLoadEndpoint:
    """Cardio load endpoint for training load and recovery data.

    Provides access to cardio load metrics including strain and tolerance.
    Data is available for the last 28 days.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize cardio load endpoint.

        Args:
            client: PolarFlow client instance
        """
        self.client = client

    async def list(self) -> list[CardioLoad]:
        """List cardio load data for the last 28 days.

        Returns:
            List of cardio load data

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                cardio = await client.cardio_load.list()
                for day in cardio:
                    print(f"{day.date}: strain={day.strain}, tolerance={day.tolerance}")
            ```
        """
        path = "/v3/users/cardio-load"
        response = await self.client._request("GET", path)

        # API returns a list directly
        if isinstance(response, list):
            return [CardioLoad.model_validate(item) for item in response]

        return []
