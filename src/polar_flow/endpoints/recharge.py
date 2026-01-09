"""Nightly recharge endpoint for Polar AccessLink API."""

from __future__ import annotations

from datetime import date
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

    async def list(self, *, since: str | None = None) -> list[NightlyRecharge]:
        """List nightly recharge data for the last 28 days.

        Args:
            since: Filter results to only include data since this date (YYYY-MM-DD).
                   If not specified, returns all available data (max 28 days).

        Returns:
            List of nightly recharge data

        Raises:
            ValueError: If since date format is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                # Get all available recharge data (last 28 days)
                recharge = await client.recharge.list()

                # Get recharge data since specific date
                recharge = await client.recharge.list(since="2026-01-01")

                for r in recharge:
                    print(f"{r.date}: ANS charge {r.ans_charge}")
            ```
        """
        path = "/v3/users/nightly-recharge"
        response = await self.client._request("GET", path)

        # API returns array directly
        if isinstance(response, list):
            results = [NightlyRecharge.model_validate(recharge) for recharge in response]
        else:
            # Fallback for dict response
            recharge_data = response.get("recharge", [])
            results = [NightlyRecharge.model_validate(recharge) for recharge in recharge_data]

        # Filter by since date if provided
        if since is not None:
            try:
                since_date = date.fromisoformat(since)
            except ValueError as e:
                raise ValueError(f"Invalid date format for 'since': {since}. Use YYYY-MM-DD") from e

            results = [r for r in results if date.fromisoformat(r.date) >= since_date]

        return results
