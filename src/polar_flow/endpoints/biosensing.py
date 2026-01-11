"""Biosensing endpoint for Polar Elixir features.

Provides access to SpO2, ECG, and Temperature data from compatible devices.
These are premium features available on newer Polar devices.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.biosensing import (
    BodyTemperaturePeriod,
    ECGResult,
    SkinTemperature,
    SpO2Result,
)

if TYPE_CHECKING:
    from datetime import date

    from polar_flow.client import PolarFlow


class BiosensingEndpoint:
    """Biosensing endpoint for Elixir health metrics.

    Access SpO2 (blood oxygen), ECG, and temperature data from
    compatible Polar devices like Polar Loop.

    All methods support optional date range filtering (max 28 days).
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize Biosensing endpoint."""
        self.client = client

    async def get_spo2(
        self,
        *,
        from_date: str | date | None = None,
        to_date: str | date | None = None,
    ) -> list[SpO2Result]:
        """Get SpO2 (blood oxygen) test results.

        Args:
            from_date: Start date for range query (YYYY-MM-DD or date object)
            to_date: End date for range query (YYYY-MM-DD or date object)

        Returns:
            List of SpO2 test results, most recent first

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                # Get all recent SpO2 tests
                spo2_results = await client.biosensing.get_spo2()
                for result in spo2_results:
                    print(f"{result.test_datetime}: {result.blood_oxygen_percent}%")

                # Get SpO2 for date range
                spo2_results = await client.biosensing.get_spo2(
                    from_date="2026-01-01",
                    to_date="2026-01-07"
                )
            ```
        """
        path = "/v3/users/biosensing/spo2"

        if from_date and to_date:
            from_str = from_date if isinstance(from_date, str) else from_date.isoformat()
            to_str = to_date if isinstance(to_date, str) else to_date.isoformat()
            path = f"{path}?from={from_str}&to={to_str}"

        try:
            response = await self.client._request("GET", path)
            if isinstance(response, list):
                return [SpO2Result.model_validate(item) for item in response]
            return []
        except Exception:
            return []

    async def get_ecg(
        self,
        *,
        from_date: str | date | None = None,
        to_date: str | date | None = None,
    ) -> list[ECGResult]:
        """Get ECG (electrocardiogram) test results.

        Returns full ECG waveform data including samples and quality measurements.

        Args:
            from_date: Start date for range query (YYYY-MM-DD or date object)
            to_date: End date for range query (YYYY-MM-DD or date object)

        Returns:
            List of ECG test results with waveform samples

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                ecg_results = await client.biosensing.get_ecg()
                for result in ecg_results:
                    print(f"HR: {result.average_heart_rate_bpm} bpm")
                    print(f"HRV: {result.heart_rate_variability_ms} ms")
                    print(f"Samples: {len(result.samples)}")
            ```
        """
        path = "/v3/users/biosensing/ecg"

        if from_date and to_date:
            from_str = from_date if isinstance(from_date, str) else from_date.isoformat()
            to_str = to_date if isinstance(to_date, str) else to_date.isoformat()
            path = f"{path}?from={from_str}&to={to_str}"

        try:
            response = await self.client._request("GET", path)
            if isinstance(response, list):
                return [ECGResult.model_validate(item) for item in response]
            return []
        except Exception:
            return []

    async def get_body_temperature(
        self,
        *,
        from_date: str | date | None = None,
        to_date: str | date | None = None,
    ) -> list[BodyTemperaturePeriod]:
        """Get body temperature measurement periods.

        Returns temperature samples with timestamps for each measurement period.

        Args:
            from_date: Start date for range query (YYYY-MM-DD or date object)
            to_date: End date for range query (YYYY-MM-DD or date object)

        Returns:
            List of temperature measurement periods with samples

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                temp_data = await client.biosensing.get_body_temperature()
                for period in temp_data:
                    print(f"Avg temp: {period.avg_temperature:.1f}C")
                    print(f"Samples: {len(period.samples)}")
            ```
        """
        path = "/v3/users/biosensing/bodytemperature"

        if from_date and to_date:
            from_str = from_date if isinstance(from_date, str) else from_date.isoformat()
            to_str = to_date if isinstance(to_date, str) else to_date.isoformat()
            path = f"{path}?from={from_str}&to={to_str}"

        try:
            response = await self.client._request("GET", path)
            if isinstance(response, list):
                return [BodyTemperaturePeriod.model_validate(item) for item in response]
            return []
        except Exception:
            return []

    async def get_skin_temperature(
        self,
        *,
        from_date: str | date | None = None,
        to_date: str | date | None = None,
    ) -> list[SkinTemperature]:
        """Get sleep skin temperature with baseline deviation.

        Simpler than body temperature - provides sleep-time temperature
        with deviation from the user's established baseline.

        Args:
            from_date: Start date for range query (YYYY-MM-DD or date object)
            to_date: End date for range query (YYYY-MM-DD or date object)

        Returns:
            List of sleep skin temperature records

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                skin_temp = await client.biosensing.get_skin_temperature()
                for record in skin_temp:
                    status = "elevated" if record.is_elevated else "normal"
                    print(f"{record.sleep_date}: {record.sleep_time_skin_temperature_celsius}C ({status})")
            ```
        """
        path = "/v3/users/biosensing/skintemperature"

        if from_date and to_date:
            from_str = from_date if isinstance(from_date, str) else from_date.isoformat()
            to_str = to_date if isinstance(to_date, str) else to_date.isoformat()
            path = f"{path}?from={from_str}&to={to_str}"

        try:
            response = await self.client._request("GET", path)
            if isinstance(response, list):
                return [SkinTemperature.model_validate(item) for item in response]
            return []
        except Exception:
            return []
