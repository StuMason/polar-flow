"""Sleep endpoint for Polar AccessLink API."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

from polar_flow.models.sleep import SleepData

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


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
        user_id: str,
        *,
        days: int | None = None,
        since: str | None = None,
        end_date: str | date | None = None,
    ) -> list[SleepData]:
        """Get sleep data for multiple days.

        Note: This method makes multiple API calls (one per day) as the Polar API
        does not provide a batch endpoint for sleep data.

        Args:
            user_id: Polar user ID
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
                sleep_list = await client.sleep.list(user_id="123", days=7)

                # Get sleep since specific date
                sleep_list = await client.sleep.list(user_id="123", since="2026-01-01")

                for sleep in sleep_list:
                    print(f"{sleep.date}: {sleep.sleep_score}/100")
            ```
        """
        if days is not None and since is not None:
            raise ValueError("Specify either 'days' or 'since', not both")

        if since is not None:
            try:
                since_date = date.fromisoformat(since)
            except ValueError as e:
                raise ValueError(f"Invalid date format for 'since': {since}. Use YYYY-MM-DD") from e

            end = (
                date.today()
                if end_date is None
                else date.fromisoformat(end_date)
                if isinstance(end_date, str)
                else end_date
            )

            days = (end - since_date).days + 1
            if days < 1:
                raise ValueError(f"'since' date {since} is in the future or after end_date")

        if days is None:
            days = 7  # default

        if days < 1 or days > 30:
            raise ValueError("days must be between 1 and 30")

        end = (
            date.today()
            if end_date is None
            else date.fromisoformat(end_date)
            if isinstance(end_date, str)
            else end_date
        )

        # Generate date range (end_date going backwards for 'days' days)
        dates = [end - timedelta(days=i) for i in range(days)]

        # Fetch sleep data for each date (in parallel would be better but API has rate limits)
        results: list[SleepData] = []
        for d in dates:
            try:
                sleep_data = await self.get(user_id=user_id, date=d)
                results.append(sleep_data)
            except Exception:
                # Skip dates with no data or errors
                continue

        # Sort by date, most recent first
        results.sort(key=lambda x: x.date, reverse=True)

        return results
