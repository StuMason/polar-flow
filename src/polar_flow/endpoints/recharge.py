"""Nightly recharge endpoint for Polar AccessLink API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.recharge import NightlyRecharge

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class RechargeEndpoint:
    """Nightly recharge endpoint for recovery data.

    Provides access to ANS (Autonomic Nervous System) charge and recovery metrics.
    Data is available for the last 28 days.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize recharge endpoint.

        Args:
            client: PolarFlow client instance
        """
        self.client = client

    async def get(self, date: str) -> NightlyRecharge:
        """Get nightly recharge data for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Nightly recharge recovery data

        Raises:
            NotFoundError: If no recharge data exists for the date
            ValidationError: If date format is invalid
        """
        path = f"/v3/users/nightly-recharge/{date}"
        response = await self.client._request("GET", path)
        return NightlyRecharge.model_validate(response)

    async def list(self) -> list[NightlyRecharge]:
        """List nightly recharge data for the last 28 days.

        Returns:
            List of nightly recharge data (max 28 days)
        """
        path = "/v3/users/nightly-recharge"
        response = await self.client._request("GET", path)

        # API returns array directly
        if isinstance(response, list):
            return [NightlyRecharge.model_validate(recharge) for recharge in response]

        # Fallback for dict response
        recharge_data = response.get("recharge", [])
        return [NightlyRecharge.model_validate(recharge) for recharge in recharge_data]
