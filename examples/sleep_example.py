"""Example: Fetch and display sleep data from Polar AccessLink API.

This example demonstrates how to:
1. Authenticate with OAuth2
2. Fetch sleep data for a specific date
3. Fetch sleep data for multiple days
4. Display sleep metrics with computed properties

Setup:
    1. Get your client credentials from https://admin.polaraccesslink.com
    2. Set environment variables:
       export POLAR_CLIENT_ID="your_client_id"
       export POLAR_CLIENT_SECRET="your_client_secret"
       export POLAR_USER_ID="your_user_id"
       export POLAR_ACCESS_TOKEN="your_access_token"  # After OAuth flow

Usage:
    python examples/sleep_example.py
"""

import asyncio
import os
from datetime import date

from polar_flow import OAuth2Handler, PolarFlow


async def oauth_flow_example() -> str:
    """Example OAuth2 authorization flow.

    Returns:
        Access token for API requests
    """
    client_id = os.getenv("POLAR_CLIENT_ID")
    client_secret = os.getenv("POLAR_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("POLAR_CLIENT_ID and POLAR_CLIENT_SECRET environment variables required")

    oauth = OAuth2Handler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8000/callback",
    )

    # Step 1: Get authorization URL
    auth_url = oauth.get_authorization_url()
    print(f"Visit this URL to authorize: {auth_url}")

    # Step 2: User visits URL, authorizes, and is redirected with code
    code = input("Enter authorization code from callback: ")

    # Step 3: Exchange code for access token
    token = await oauth.exchange_code(code)
    print(f"Access token: {token.access_token}")
    print(f"User ID: {token.user_id}")

    return token.access_token


async def fetch_single_day_sleep(access_token: str, user_id: str, date_str: str) -> None:
    """Fetch and display sleep data for a single day.

    Args:
        access_token: Polar API access token
        user_id: Polar user ID
        date_str: Date in YYYY-MM-DD format
    """
    print(f"\n=== Sleep Data for {date_str} ===\n")

    async with PolarFlow(access_token=access_token) as client:
        sleep = await client.sleep.get(user_id=user_id, date=date_str)

        print(f"Sleep Quality: {sleep.get_sleep_quality()}")
        print(f"Sleep Score: {sleep.sleep_score}/100")
        print(f"Sleep Charge: {sleep.sleep_charge}/100")
        print()
        print(f"Sleep Duration: {sleep.total_sleep_hours} hours")
        print(f"  Light Sleep: {sleep.light_sleep / 3600:.1f}h")
        print(f"  Deep Sleep: {sleep.deep_sleep / 3600:.1f}h")
        print(f"  REM Sleep: {sleep.rem_sleep / 3600:.1f}h")
        print()
        print(f"Time in Bed: {sleep.time_in_bed_hours} hours")
        print(f"Sleep Efficiency: {sleep.sleep_efficiency}%")
        print()
        print(f"Sleep Cycles: {sleep.sleep_cycles}")
        print(f"Interruptions: {sleep.total_interruption_duration / 60:.0f} minutes")

        if sleep.hrv_avg:
            print()
            print(f"Average HRV: {sleep.hrv_avg} ms")

        if sleep.heart_rate_avg:
            print(f"Average HR: {sleep.heart_rate_avg} bpm")
            if sleep.heart_rate_min and sleep.heart_rate_max:
                print(f"HR Range: {sleep.heart_rate_min}-{sleep.heart_rate_max} bpm")

        if sleep.breathing_rate_avg:
            print(f"Breathing Rate: {sleep.breathing_rate_avg} breaths/min")


async def fetch_weekly_sleep(access_token: str, user_id: str) -> None:
    """Fetch and display sleep data for the last 7 days.

    Args:
        access_token: Polar API access token
        user_id: Polar user ID
    """
    print("\n=== Last 7 Days Sleep Summary ===\n")

    async with PolarFlow(access_token=access_token) as client:
        sleep_list = await client.sleep.list(user_id=user_id, days=7)

        if not sleep_list:
            print("No sleep data found for the last 7 days")
            return

        print(f"{'Date':<12} {'Score':<8} {'Quality':<12} {'Duration':<10} {'Efficiency'}")
        print("-" * 60)

        for sleep in sleep_list:
            print(
                f"{sleep.date!s:<12} "
                f"{sleep.sleep_score:>3}/100  "
                f"{sleep.get_sleep_quality():<12} "
                f"{sleep.total_sleep_hours:>5.1f}h     "
                f"{sleep.sleep_efficiency:>5.1f}%"
            )

        # Calculate averages
        avg_score = sum(s.sleep_score for s in sleep_list) / len(sleep_list)
        avg_duration = sum(s.total_sleep_hours for s in sleep_list) / len(sleep_list)
        avg_efficiency = sum(s.sleep_efficiency for s in sleep_list) / len(sleep_list)

        print("-" * 60)
        print(
            f"Averages:    {avg_score:>3.0f}/100  "
            f"{'':12} {avg_duration:>5.1f}h     {avg_efficiency:>5.1f}%"
        )


async def main() -> None:
    """Main example function."""
    # Check if access token is already available
    access_token = os.getenv("POLAR_ACCESS_TOKEN")
    user_id = os.getenv("POLAR_USER_ID")

    if not access_token:
        print("No access token found. Starting OAuth flow...\n")
        access_token = await oauth_flow_example()

        if not user_id:
            # User ID is returned during OAuth flow
            print("\nPlease set POLAR_USER_ID environment variable and run again")
            return

    if not user_id:
        raise ValueError("POLAR_USER_ID environment variable required")

    # Example 1: Fetch today's sleep
    today = date.today().isoformat()
    try:
        await fetch_single_day_sleep(access_token, user_id, today)
    except Exception as e:
        print(f"Error fetching today's sleep: {e}")

    # Example 2: Fetch weekly sleep summary
    try:
        await fetch_weekly_sleep(access_token, user_id)
    except Exception as e:
        print(f"Error fetching weekly sleep: {e}")


if __name__ == "__main__":
    asyncio.run(main())
