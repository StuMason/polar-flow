"""Custom exceptions for polar-flow."""


class PolarFlowError(Exception):
    """Base exception for polar-flow."""


class AuthenticationError(PolarFlowError):
    """Invalid or expired access token."""


class RateLimitError(PolarFlowError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after


class NotFoundError(PolarFlowError):
    """Requested resource not found."""


class ValidationError(PolarFlowError):
    """Invalid request parameters."""
