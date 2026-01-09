"""Activity endpoint for Polar AccessLink API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.activity import Activity

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class ActivityEndpoint:
    """Activity endpoint for daily activity data.

    Provides access to daily activity summaries, steps, and activity zones.
    Data is available for the last 28 days.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize activity endpoint.

        Args:
            client: PolarFlow client instance
        """
        self.client = client

    async def get(self, date: str) -> Activity:
        """Get activity summary for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Activity summary with samples

        Raises:
            NotFoundError: If no activity data exists for the date
            ValidationError: If date format is invalid
        """
        path = f"/v3/users/activities/{date}"
        response = await self.client._request("GET", path)
        return Activity.model_validate(response)

    async def list(
        self, from_date: str | None = None, to_date: str | None = None
    ) -> list[Activity]:
        """List activity summaries.

        Args:
            from_date: Start date in YYYY-MM-DD format (optional)
            to_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of activity summaries (max 28 days)

        Note:
            API returns data for last 28 days if no date range specified.
            Date range cannot exceed 28 days.
        """
        path = "/v3/users/activities"
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = await self.client._request("GET", path, params=params)

        # API returns array directly
        if isinstance(response, list):
            return [Activity.model_validate(activity) for activity in response]

        # Fallback for dict response
        activities_data = response.get("activities", [])
        return [Activity.model_validate(activity) for activity in activities_data]
