"""Example: Fetching exercise/training data from Polar AccessLink API.

This example demonstrates:
- Listing recent exercises (last 30 days)
- Getting detailed exercise data
- Fetching exercise samples (HR, speed, cadence, etc.)
- Getting heart rate zones
- Exporting exercises to TCX/GPX format
"""

import asyncio
import os
from pathlib import Path

from polar_flow import OAuth2Handler, PolarFlow


async def main() -> None:
    """Run exercises example."""
    # Get credentials from environment
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")

    # If no access token, do OAuth flow
    if not access_token:
        if not client_id or not client_secret:
            print("Error: Need CLIENT_ID and CLIENT_SECRET in .env for OAuth flow")
            print("Or provide ACCESS_TOKEN directly")
            return

        print("No access token found. Starting OAuth flow...")
        oauth = OAuth2Handler(client_id=client_id, client_secret=client_secret)
        auth_url = oauth.get_authorization_url()

        print(f"\n1. Open this URL in your browser:\n{auth_url}\n")
        print("2. After authorizing, copy the 'code' from the callback URL")
        auth_code = input("Enter the authorization code: ").strip()

        token = await oauth.exchange_code(auth_code)
        access_token = token.access_token
        print(f"\nAccess token: {access_token}")
        print("Save this to .env as ACCESS_TOKEN for future use\n")

    # Use the Polar Flow client
    async with PolarFlow(access_token=access_token) as client:
        print("=" * 60)
        print("Fetching exercises from last 30 days...")
        print("=" * 60)

        # List all exercises (last 30 days only)
        exercises = await client.exercises.list()
        print(f"\nFound {len(exercises)} exercises\n")

        if not exercises:
            print("No exercises found in the last 30 days!")
            return

        # Show summary of each exercise
        for i, exercise in enumerate(exercises[:10], 1):  # Show first 10
            start = exercise.start_time.strftime("%Y-%m-%d %H:%M")
            duration = exercise.duration_minutes
            distance = f"{exercise.distance_km}km" if exercise.distance_km else "no distance"

            print(f"{i}. {start} - {exercise.sport}")
            print(f"   Duration: {duration} min | Calories: {exercise.calories} | {distance}")

            if exercise.average_heart_rate:
                print(
                    f"   HR: avg {exercise.average_heart_rate} bpm, "
                    f"max {exercise.maximum_heart_rate} bpm"
                )
            print()

        # Get detailed data for first exercise
        first_exercise = exercises[0]
        print("=" * 60)
        print(f"Detailed data for: {first_exercise.sport} ({first_exercise.start_time})")
        print("=" * 60)

        exercise_detail = await client.exercises.get(exercise_id=first_exercise.id)
        print(f"\nSport: {exercise_detail.detailed_sport_info or exercise_detail.sport}")
        print(f"Device: {exercise_detail.device}")
        print(f"Duration: {exercise_detail.duration_minutes} minutes")
        print(f"Calories: {exercise_detail.calories}")

        if exercise_detail.distance_km:
            print(f"Distance: {exercise_detail.distance_km} km")

        if exercise_detail.training_load:
            print(f"Training Load: {exercise_detail.training_load}")

        if exercise_detail.fat_percentage:
            print(
                f"\nEnergy sources: {exercise_detail.fat_percentage}% fat, "
                f"{exercise_detail.carbohydrate_percentage}% carbs"
            )

        # Get exercise samples (HR, speed, cadence, etc.)
        print("\n" + "=" * 60)
        print("Exercise samples (sensor data)")
        print("=" * 60)

        samples = await client.exercises.get_samples(exercise_id=first_exercise.id)
        print(f"\nFound {len(samples.samples)} sample types:")

        for sample in samples.samples:
            print(f"\n  {sample.sample_type}:")
            print(f"    Recording rate: {sample.recording_rate}s")
            print(f"    Data points: {len(sample.values)}")

            if sample.values:
                values = sample.values[:10]  # Show first 10
                print(f"    First values: {values}")

        # Get heart rate zones
        hr_sample = samples.get_sample_by_type("HEARTRATE")
        if hr_sample:
            print("\n" + "=" * 60)
            print("Heart rate zones")
            print("=" * 60)

            zones = await client.exercises.get_zones(exercise_id=first_exercise.id)

            if zones.zones:
                print(f"\nTotal time in zones: {zones.total_time_seconds // 60} minutes\n")

                for zone in zones.zones:
                    percentage = (
                        zone.in_zone_seconds / zones.total_time_seconds * 100
                        if zones.total_time_seconds > 0
                        else 0
                    )
                    print(
                        f"  Zone {zone.index}: {zone.lower_limit}-{zone.upper_limit} bpm "
                        f"→ {zone.in_zone_minutes} min ({percentage:.1f}%)"
                    )

        # Export to TCX/GPX if exercise has route data
        if first_exercise.has_route:
            print("\n" + "=" * 60)
            print("Exporting exercise with GPS data")
            print("=" * 60)

            # Export as TCX (Training Center XML)
            tcx_xml = await client.exercises.export_tcx(exercise_id=first_exercise.id)
            tcx_path = Path(f"exercise_{first_exercise.id}.tcx")
            tcx_path.write_text(tcx_xml)
            print(f"\nExported to {tcx_path} ({len(tcx_xml)} chars)")

            # Export as GPX (GPS Exchange Format)
            gpx_xml = await client.exercises.export_gpx(exercise_id=first_exercise.id)
            gpx_path = Path(f"exercise_{first_exercise.id}.gpx")
            gpx_path.write_text(gpx_xml)
            print(f"Exported to {gpx_path} ({len(gpx_xml)} chars)")

        print("\n" + "=" * 60)
        print("Example complete!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
