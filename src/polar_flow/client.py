"""Core HTTP client for Polar AccessLink API."""

import logging
from typing import Any, TypeVar, overload

import httpx
from pydantic import BaseModel

from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    PolarFlowError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class PolarFlow:
    """Async HTTP client for Polar AccessLink API.

    This client provides async-first access to the Polar AccessLink API with
    automatic error handling, rate limit awareness, and Pydantic model validation.

    Example:
        ```python
        async with PolarFlow(access_token="your_token") as client:
            sleep = await client.sleep.get(user_id="123", date="2026-01-09")
            print(sleep.sleep_score)
        ```
    """

    BASE_URL = "https://www.polaraccesslink.com"

    def __init__(self, access_token: str, base_url: str | None = None) -> None:
        """Initialize the Polar API client.

        Args:
            access_token: OAuth2 access token for authentication
            base_url: Optional custom base URL (defaults to production API)

        Raises:
            ValueError: If access_token is empty or invalid
        """
        if not access_token or not access_token.strip():
            raise ValueError("access_token is required and cannot be empty")

        if len(access_token) < 10:
            raise ValueError("access_token appears to be invalid (too short)")

        self.access_token = access_token.strip()
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self._client: httpx.AsyncClient | None = None

        # Import endpoints here to avoid circular imports
        from polar_flow.endpoints.activity import ActivityEndpoint
        from polar_flow.endpoints.exercises import ExercisesEndpoint
        from polar_flow.endpoints.physical_info import PhysicalInfoEndpoint
        from polar_flow.endpoints.recharge import RechargeEndpoint
        from polar_flow.endpoints.sleep import SleepEndpoint
        from polar_flow.endpoints.users import UsersEndpoint

        self.sleep = SleepEndpoint(self)
        self.exercises = ExercisesEndpoint(self)
        self.activity = ActivityEndpoint(self)
        self.recharge = RechargeEndpoint(self)
        self.users = UsersEndpoint(self)
        self.physical_info = PhysicalInfoEndpoint(self)

    async def __aenter__(self) -> "PolarFlow":
        """Enter async context manager.

        Returns:
            The client instance

        Example:
            ```python
            async with PolarFlow(access_token="token") as client:
                ...
            ```
        """
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
            follow_redirects=True,
        )
        logger.debug(f"Initialized Polar API client with base URL: {self.base_url}")
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager and cleanup resources.

        Args:
            *args: Exception info if any
        """
        if self._client:
            await self._client.aclose()
            logger.debug("Closed Polar API client connection")
            self._client = None

    @overload
    async def _request(
        self,
        method: str,
        path: str,
        response_model: type[T],
        **kwargs: Any,
    ) -> T: ...

    @overload
    async def _request(
        self,
        method: str,
        path: str,
        response_model: None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...

    async def _request(
        self,
        method: str,
        path: str,
        response_model: type[T] | None = None,
        **kwargs: Any,
    ) -> T | dict[str, Any]:
        """Make HTTP request to Polar API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path (will be prefixed with /v3)
            response_model: Optional Pydantic model to parse response into
            **kwargs: Additional arguments passed to httpx.request()

        Returns:
            Parsed Pydantic model instance or raw dict if no model provided

        Raises:
            RuntimeError: If client not initialized (use async with context manager)
            AuthenticationError: If access token is invalid (401)
            NotFoundError: If resource not found (404)
            RateLimitError: If rate limit exceeded (429)
            ValidationError: If request validation failed (422)
            PolarFlowError: For other API errors
        """
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with PolarFlow(...) as client:' pattern"
            )

        # Ensure path starts with /v3 (Polar API version)
        if not path.startswith("/v3"):
            path = f"/v3{path if path.startswith('/') else f'/{path}'}"

        logger.debug(f"Request: {method} {path}")

        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as e:
            raise PolarFlowError(f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise PolarFlowError(f"Request failed: {e}") from e

        logger.debug(
            f"Response: {response.status_code} (rate limit: "
            f"{response.headers.get('X-RateLimit-Remaining', 'N/A')}/"
            f"{response.headers.get('X-RateLimit-Limit', 'N/A')})"
        )

        # Check rate limit headers and warn if low
        self._check_rate_limit(response)

        # Handle HTTP errors
        data = await self._handle_response(response)

        # Parse into Pydantic model if provided
        if response_model:
            return response_model.model_validate(data)

        return data

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response from API

        Returns:
            Parsed JSON response data

        Raises:
            AuthenticationError: If 401 Unauthorized
            NotFoundError: If 404 Not Found
            RateLimitError: If 429 Too Many Requests
            ValidationError: If 422 Unprocessable Entity
            PolarFlowError: For other non-success status codes
        """
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired access token. Please re-authenticate.")

        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {response.url.path}")

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_after} seconds.", retry_after=retry_after
            )

        if response.status_code == 422:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except Exception:
                error_msg = response.text
            raise ValidationError(f"Invalid request parameters: {error_msg}")

        if not response.is_success:
            raise PolarFlowError(
                f"API error {response.status_code}: {response.text or 'Unknown error'}"
            )

        # Handle 204 No Content (e.g., successful DELETE operations)
        if response.status_code == 204:
            return {}

        # Parse JSON response
        try:
            json_data: dict[str, Any] = response.json()
            return json_data
        except Exception as e:
            raise PolarFlowError(f"Failed to parse JSON response: {e}") from e

    def _check_rate_limit(self, response: httpx.Response) -> None:
        """Check rate limit headers and log warnings if approaching limit.

        Args:
            response: HTTP response with rate limit headers
        """
        remaining = response.headers.get("X-RateLimit-Remaining")
        limit = response.headers.get("X-RateLimit-Limit")

        if remaining and limit:
            remaining_int = int(remaining)
            limit_int = int(limit)

            # Warn if less than 10% of rate limit remaining
            if remaining_int < limit_int * 0.1:
                logger.warning(
                    f"Rate limit warning: Only {remaining_int}/{limit_int} "
                    f"requests remaining ({remaining_int / limit_int * 100:.1f}%)"
                )
