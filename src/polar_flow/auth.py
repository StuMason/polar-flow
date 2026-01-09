"""OAuth2 authentication handler for Polar AccessLink API."""

import secrets
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from polar_flow.exceptions import AuthenticationError, PolarFlowError


class OAuth2Token(BaseModel):
    """OAuth2 access token response."""

    access_token: str = Field(description="Access token for API requests")
    token_type: str = Field(description="Token type (usually 'bearer')")
    x_user_id: int = Field(description="Polar user ID")

    @property
    def user_id(self) -> str:
        """Get the user ID as string.

        Returns:
            Polar user ID as string
        """
        return str(self.x_user_id)


class OAuth2Handler:
    """OAuth2 authorization flow handler for Polar AccessLink API.

    This class handles the OAuth2 authorization code flow for obtaining
    access tokens from Polar AccessLink API.

    Example:
        ```python
        oauth = OAuth2Handler(
            client_id="your_client_id",
            client_secret="your_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )

        # Step 1: Get authorization URL
        auth_url = oauth.get_authorization_url()
        # Redirect user to auth_url

        # Step 2: Exchange authorization code for token
        token = await oauth.exchange_code(code="authorization_code_from_callback")

        # Step 3: Use token with PolarFlow client
        async with PolarFlow(access_token=token.access_token) as client:
            ...
        ```
    """

    AUTHORIZE_URL = "https://flow.polar.com/oauth2/authorization"
    TOKEN_URL = "https://polarremote.com/v2/oauth2/token"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str | None = None) -> None:
        """Initialize OAuth2 handler.

        Args:
            client_id: OAuth2 client ID from Polar AccessLink admin
            client_secret: OAuth2 client secret from Polar AccessLink admin
            redirect_uri: Optional redirect URI (must match registration)

        Raises:
            ValueError: If client_id or client_secret is empty
        """
        if not client_id or not client_id.strip():
            raise ValueError("client_id is required and cannot be empty")

        if not client_secret or not client_secret.strip():
            raise ValueError("client_secret is required and cannot be empty")

        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state: str | None = None) -> str:
        """Generate authorization URL for user to visit.

        The user should be redirected to this URL to authorize the application.
        After authorization, they will be redirected back to your redirect_uri
        with an authorization code.

        Args:
            state: Optional state parameter for CSRF protection.
                  If not provided, a random state will be generated.

        Returns:
            Authorization URL to redirect the user to

        Example:
            ```python
            oauth = OAuth2Handler(...)
            auth_url = oauth.get_authorization_url(state="random_string")
            # Redirect user to auth_url
            ```
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {"response_type": "code", "client_id": self.client_id, "state": state}

        if self.redirect_uri:
            params["redirect_uri"] = self.redirect_uri

        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> OAuth2Token:
        """Exchange authorization code for access token.

        After the user authorizes your application, they will be redirected
        to your redirect_uri with a 'code' parameter. Use this method to
        exchange that code for an access token.

        Args:
            code: Authorization code from callback URL

        Returns:
            OAuth2Token containing access_token and user_id

        Raises:
            ValueError: If code is empty
            AuthenticationError: If token exchange fails (invalid code, etc.)
            PolarFlowError: If request fails

        Example:
            ```python
            # In your callback handler:
            code = request.args.get("code")
            token = await oauth.exchange_code(code)
            # Store token.access_token for future API requests
            ```
        """
        if not code or not code.strip():
            raise ValueError("authorization code is required and cannot be empty")

        data = {
            "grant_type": "authorization_code",
            "code": code.strip(),
        }

        if self.redirect_uri:
            data["redirect_uri"] = self.redirect_uri

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json;charset=UTF-8",
                    },
                    auth=(self.client_id, self.client_secret),  # HTTP Basic Auth
                    timeout=30.0,
                )

                if response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error_description", "Invalid authorization code")
                    raise AuthenticationError(f"Token exchange failed: {error_msg}")

                if response.status_code == 401:
                    raise AuthenticationError("Invalid client credentials")

                if not response.is_success:
                    raise PolarFlowError(
                        f"Token exchange failed with status {response.status_code}: {response.text}"
                    )

                token_data = response.json()
                return OAuth2Token.model_validate(token_data)

        except httpx.TimeoutException as e:
            raise PolarFlowError(f"Token exchange timeout: {e}") from e
        except httpx.RequestError as e:
            raise PolarFlowError(f"Token exchange request failed: {e}") from e
