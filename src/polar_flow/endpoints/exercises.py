"""Exercises endpoint for Polar AccessLink API."""

from typing import TYPE_CHECKING

from polar_flow.models.exercise import Exercise, ExerciseSamples, ExerciseZones

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class ExercisesEndpoint:
    """Exercises endpoint handler.

    This class provides methods for accessing training session data from
    the Polar AccessLink API. Note: Only last 30 days of exercises are available.
    """

    def __init__(self, client: "PolarFlow") -> None:
        """Initialize exercises endpoint.

        Args:
            client: Parent PolarFlow client instance
        """
        self.client = client

    async def list(self) -> list[Exercise]:
        """List all available exercises (last 30 days).

        Returns:
            List of exercises from the last 30 days

        Raises:
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                exercises = await client.exercises.list()
                for ex in exercises:
                    print(f"{ex.start_time}: {ex.sport} - {ex.duration_minutes} min")
            ```
        """
        path = "/v3/exercises"
        response = await self.client._request("GET", path)
        # API returns array directly, not {"exercises": [...]}
        if isinstance(response, list):
            return [Exercise.model_validate(ex) for ex in response]
        # Fallback for dict response (shouldn't happen but be safe)
        exercises_data = response.get("exercises", [])
        return [Exercise.model_validate(ex) for ex in exercises_data]

    async def get(self, exercise_id: str) -> Exercise:
        """Get detailed exercise data by ID.

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            Detailed exercise data

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                exercise = await client.exercises.get(exercise_id="123")
                print(f"Calories: {exercise.calories}")
                print(f"Distance: {exercise.distance_km} km")
            ```
        """
        path = f"/v3/exercises/{exercise_id}"
        return await self.client._request("GET", path, response_model=Exercise)

    async def get_samples(self, exercise_id: str) -> ExerciseSamples:
        """Get exercise samples (HR, speed, cadence, altitude, etc.).

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            Exercise samples data

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                samples = await client.exercises.get_samples(exercise_id="123")
                hr_sample = samples.get_sample_by_type("HEARTRATE")
                if hr_sample:
                    print(f"HR values: {hr_sample.values[:5]}...")  # First 5 values
            ```
        """
        path = f"/v3/exercises/{exercise_id}/samples"
        response = await self.client._request("GET", path)
        return ExerciseSamples(samples=response.get("samples", []))

    async def get_zones(self, exercise_id: str) -> ExerciseZones:
        """Get heart rate zones for exercise.

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            Heart rate zones data

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                zones = await client.exercises.get_zones(exercise_id="123")
                for zone in zones.zones:
                    print(f"Zone {zone.index}: {zone.in_zone_minutes} minutes "
                          f"({zone.lower_limit}-{zone.upper_limit} BPM)")
            ```
        """
        path = f"/v3/exercises/{exercise_id}/zones"
        response = await self.client._request("GET", path)
        return ExerciseZones(zones=response.get("zone", []))

    async def export_tcx(self, exercise_id: str) -> str:
        """Export exercise as TCX (Training Center XML) format.

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            TCX XML content as string

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                tcx_xml = await client.exercises.export_tcx(exercise_id="123")
                with open("exercise.tcx", "w") as f:
                    f.write(tcx_xml)
            ```
        """
        path = f"/v3/exercises/{exercise_id}/tcx"

        if not self.client._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with PolarFlow(...) as client:' pattern"
            )

        # TCX export returns XML, not JSON
        response = await self.client._client.get(path)

        # Use same error handling as regular requests
        if response.status_code == 401:
            from polar_flow.exceptions import AuthenticationError

            raise AuthenticationError("Invalid or expired access token")

        if response.status_code == 404:
            from polar_flow.exceptions import NotFoundError

            raise NotFoundError(f"Exercise not found: {exercise_id}")

        if not response.is_success:
            from polar_flow.exceptions import PolarFlowError

            raise PolarFlowError(
                f"API error {response.status_code}: {response.text or 'Unknown error'}"
            )

        return response.text

    async def export_gpx(self, exercise_id: str) -> str:
        """Export exercise as GPX (GPS Exchange Format).

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            GPX XML content as string

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                gpx_xml = await client.exercises.export_gpx(exercise_id="123")
                with open("exercise.gpx", "w") as f:
                    f.write(gpx_xml)
            ```
        """
        path = f"/v3/exercises/{exercise_id}/gpx"

        if not self.client._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with PolarFlow(...) as client:' pattern"
            )

        # GPX export returns XML, not JSON
        response = await self.client._client.get(path)

        # Use same error handling as regular requests
        if response.status_code == 401:
            from polar_flow.exceptions import AuthenticationError

            raise AuthenticationError("Invalid or expired access token")

        if response.status_code == 404:
            from polar_flow.exceptions import NotFoundError

            raise NotFoundError(f"Exercise not found: {exercise_id}")

        if not response.is_success:
            from polar_flow.exceptions import PolarFlowError

            raise PolarFlowError(
                f"API error {response.status_code}: {response.text or 'Unknown error'}"
            )

        return response.text
