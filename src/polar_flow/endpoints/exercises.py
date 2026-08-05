"""Exercises endpoint for Polar AccessLink API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from polar_flow.models.exercise import Exercise, ExerciseSamples, ExerciseZones, RoutePoint

if TYPE_CHECKING:
    import builtins

    from polar_flow.client import PolarFlow


def _detail_params(*, samples: bool, zones: bool, route: bool) -> dict[str, str]:
    """Build query params for the optional exercise detail flags."""
    params: dict[str, str] = {}
    if samples:
        params["samples"] = "true"
    if zones:
        params["zones"] = "true"
    if route:
        params["route"] = "true"
    return params


class ExercisesEndpoint:
    """Exercises endpoint handler.

    This class provides methods for accessing training session data from
    the Polar AccessLink API. Note: Only last 30 days of exercises are available.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize exercises endpoint.

        Args:
            client: Parent PolarFlow client instance
        """
        self.client = client

    async def list(
        self, *, samples: bool = False, zones: bool = False, route: bool = False
    ) -> list[Exercise]:
        """List all available exercises (last 30 days).

        Args:
            samples: Include raw sample series in each exercise
            zones: Include heart-rate-zone breakdown in each exercise
            route: Include GPS route points in each exercise

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
        kwargs: dict[str, Any] = {}
        params = _detail_params(samples=samples, zones=zones, route=route)
        if params:
            kwargs["params"] = params
        response = await self.client._request("GET", path, **kwargs)
        # API returns array directly, not {"exercises": [...]}
        if isinstance(response, list):
            return [Exercise.model_validate(ex) for ex in response]
        # Fallback for dict response (shouldn't happen but be safe)
        exercises_data = response.get("exercises", [])
        return [Exercise.model_validate(ex) for ex in exercises_data]

    async def get(
        self,
        exercise_id: str,
        *,
        samples: bool = False,
        zones: bool = False,
        route: bool = False,
    ) -> Exercise:
        """Get detailed exercise data by ID.

        Args:
            exercise_id: Unique exercise identifier
            samples: Include raw sample series (HR, speed, cadence, ...)
            zones: Include heart-rate-zone breakdown
            route: Include GPS route points

        Returns:
            Detailed exercise data

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                exercise = await client.exercises.get(
                    exercise_id="123", samples=True, zones=True, route=True
                )
                print(f"Calories: {exercise.calories}")
                print(f"Route points: {len(exercise.route or [])}")
            ```
        """
        path = f"/v3/exercises/{exercise_id}"
        kwargs: dict[str, Any] = {}
        params = _detail_params(samples=samples, zones=zones, route=route)
        if params:
            kwargs["params"] = params
        return await self.client._request("GET", path, response_model=Exercise, **kwargs)

    async def get_samples(self, exercise_id: str) -> ExerciseSamples:
        """Get exercise samples (HR, speed, cadence, altitude, etc.).

        Uses the ``samples=true`` query flag on the exercise endpoint —
        the ``/samples`` sub-path only ever existed on the deprecated
        transaction flow and 404s for hashed exercise IDs.

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
        exercise = await self.get(exercise_id, samples=True)
        return ExerciseSamples(samples=exercise.samples or [])

    async def get_zones(self, exercise_id: str) -> ExerciseZones:
        """Get heart rate zones for exercise.

        Uses the ``zones=true`` query flag on the exercise endpoint —
        the ``/zones`` sub-path only ever existed on the deprecated
        transaction flow and 404s for hashed exercise IDs.

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
        exercise = await self.get(exercise_id, zones=True)
        return ExerciseZones(zones=exercise.heart_rate_zones or [])

    # builtins.list because the `list` method above shadows the builtin in class scope
    async def get_route(self, exercise_id: str) -> builtins.list[RoutePoint]:
        """Get GPS route points for exercise.

        Uses the ``route=true`` query flag on the exercise endpoint to
        return the route as structured JSON (see also :meth:`export_gpx`
        / :meth:`export_tcx` for file formats).

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            List of GPS route points (empty if the exercise has no route)

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                points = await client.exercises.get_route(exercise_id="123")
                if points:
                    print(f"Start: {points[0].latitude}, {points[0].longitude}")
            ```
        """
        exercise = await self.get(exercise_id, route=True)
        return exercise.route or []

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

    async def export_fit(self, exercise_id: str) -> bytes:
        """Export exercise as FIT (Flexible and Interoperable Data Transfer) format.

        FIT is a binary format, so this returns raw bytes.

        Args:
            exercise_id: Unique exercise identifier

        Returns:
            FIT file content as bytes

        Raises:
            NotFoundError: If exercise not found
            AuthenticationError: If access token is invalid

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                fit_data = await client.exercises.export_fit(exercise_id="123")
                with open("exercise.fit", "wb") as f:
                    f.write(fit_data)
            ```
        """
        path = f"/v3/exercises/{exercise_id}/fit"

        if not self.client._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with PolarFlow(...) as client:' pattern"
            )

        # FIT export returns binary data, not JSON
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

        return response.content

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
