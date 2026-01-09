"""Users endpoint for Polar AccessLink API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from polar_flow.models.user import UserInfo, UserRegistrationRequest

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow


class UsersEndpoint:
    """Users endpoint for user management.

    Provides user registration, information retrieval, and de-registration.
    """

    def __init__(self, client: PolarFlow) -> None:
        """Initialize users endpoint.

        Args:
            client: PolarFlow client instance
        """
        self.client = client

    async def register(self, member_id: str) -> UserInfo:
        """Register a new user.

        Args:
            member_id: Partner's custom identifier for user (must be unique)

        Returns:
            User information including Polar user ID

        Raises:
            ValidationError: If member_id already exists
        """
        path = "/v3/users"
        request_data = UserRegistrationRequest(member_id=member_id)
        response = await self.client._request(
            "POST", path, json=request_data.model_dump(by_alias=True)
        )
        return UserInfo.model_validate(response)

    async def get(self, user_id: int | str) -> UserInfo:
        """Get user information.

        Args:
            user_id: Polar user ID

        Returns:
            User profile information

        Raises:
            NotFoundError: If user not found
        """
        path = f"/v3/users/{user_id}"
        response = await self.client._request("GET", path)
        return UserInfo.model_validate(response)

    async def delete(self, user_id: int | str) -> None:
        """De-register user and revoke access.

        This permanently removes the user and revokes their access token.

        Args:
            user_id: Polar user ID

        Raises:
            NotFoundError: If user not found
        """
        path = f"/v3/users/{user_id}"
        await self.client._request("DELETE", path)
