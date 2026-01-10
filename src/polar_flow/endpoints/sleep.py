"""Sleep endpoint for Polar AccessLink API."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

from pydantic import BaseModel

from polar_flow.models.sleep import SleepData

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class SleepListResponse(BaseModel):
    """Response model for sleep list endpoint."""

    nights: list[SleepData]


class SleepEndpoint:
    """Sleep data endpoint handler.

    This class provides methods for accessing sleep tracking data from
    the Polar AccessLink API. Sleep data is non-transactional and can
    be retrieved multiple times.
    """

    def __init__(self, client: "PolarFlow") -> None:
        """Initialize sleep endpoint.

        Args:
            client: Parent PolarFlow client instance
        """
        self.client = client

    async def get(self, user_id: str, date: str | date) -> SleepData:
        """Get sleep data for a specific date.

        Args:
            user_id: Polar user ID
            date: Date in YYYY-MM-DD format or date object (the day user woke up)

        Returns:
            Sleep data for the specified date

        Raises:
            NotFoundError: If no sleep data exists for the date
            AuthenticationError: If access token is invalid
            ValidationError: If date format is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                sleep = await client.sleep.get(user_id="123", date="2026-01-09")
                print(f"Sleep score: {sleep.sleep_score}/100")
                print(f"Total sleep: {sleep.total_sleep_hours} hours")
            ```
        """
        date_str = date if isinstance(date, str) else date.isoformat()

        path = f"/v3/users/{user_id}/sleep/{date_str}"
        return await self.client._request("GET", path, response_model=SleepData)

    async def list(
        self,
        user_id: str | None = None,  # Keep for backwards compat but not used
        *,
        days: int | None = None,
        since: str | None = None,
        end_date: str | date | None = None,
    ) -> list[SleepData]:
        """Get sleep data for multiple days.

        Args:
            user_id: (Deprecated) Polar user ID - not needed, API uses token
            days: Number of days to fetch (1-30). Defaults to 7.
            since: Fetch data since this date (YYYY-MM-DD). Alternative to days.
            end_date: End date (inclusive). Defaults to today.

        Returns:
            List of sleep data, ordered by date (most recent first)

        Raises:
            ValueError: If both days and since specified, or if since is invalid
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                # Get last 7 days of sleep
                sleep_list = await client.sleep.list(days=7)

                # Get sleep since specific date
                sleep_list = await client.sleep.list(since="2026-01-01")

                for sleep in sleep_list:
                    print(f"{sleep.date}: {sleep.sleep_score}/100")
            ```
        """
        if days is not None and since is not None:
            raise ValueError("Specify either 'days' or 'since', not both")

        # Calculate date range
        end = (
            date.today()
            if end_date is None
            else date.fromisoformat(end_date)
            if isinstance(end_date, str)
            else end_date
        )

        if since is not None:
            try:
                start = date.fromisoformat(since)
            except ValueError as e:
                raise ValueError(f"Invalid date format for 'since': {since}. Use YYYY-MM-DD") from e

            if start > end:
                raise ValueError(f"'since' date {since} is after end_date")
        else:
            if days is None:
                days = 7  # default

            if days < 1 or days > 30:
                raise ValueError("days must be between 1 and 30")

            start = end - timedelta(days=days - 1)

        # Call the actual Polar API list endpoint
        path = f"/v3/users/sleep?from={start.isoformat()}&to={end.isoformat()}"
        response = await self.client._request("GET", path, response_model=SleepListResponse)

        # Sort by date, most recent first
        results = sorted(response.nights, key=lambda x: x.date, reverse=True)

        return results
