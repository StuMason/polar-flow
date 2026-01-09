"""Custom exceptions for polar-flow."""


class PolarFlowError(Exception):
    """Base exception for polar-flow.

    Attributes:
        endpoint: API endpoint that failed
        status_code: HTTP status code
        response_body: Response body (truncated to 500 chars)
    """

    def __init__(
        self,
        message: str,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize polar flow error.

        Args:
            message: Error message
            endpoint: API endpoint that failed
            status_code: HTTP status code
            response_body: Response body
        """
        super().__init__(message)
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(PolarFlowError):
    """Invalid or expired access token."""


class RateLimitError(PolarFlowError):
    """Rate limit exceeded.

    Attributes:
        retry_after: Number of seconds to wait before retrying
        endpoint: API endpoint that failed
        status_code: HTTP status code
        response_body: Response body
    """

    def __init__(
        self,
        message: str,
        retry_after: int,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
            endpoint: API endpoint that failed
            status_code: HTTP status code
            response_body: Response body
        """
        super().__init__(
            message, endpoint=endpoint, status_code=status_code, response_body=response_body
        )
        self.retry_after = retry_after


class NotFoundError(PolarFlowError):
    """Requested resource not found."""


class ValidationError(PolarFlowError):
    """Invalid request parameters."""
