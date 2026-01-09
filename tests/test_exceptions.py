"""Tests for custom exceptions."""

from polar_flow.exceptions import (
    AuthenticationError,
    NotFoundError,
    PolarFlowError,
    RateLimitError,
    ValidationError,
)


def test_polar_flow_error() -> None:
    """Test base PolarFlowError exception."""
    error = PolarFlowError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_authentication_error() -> None:
    """Test AuthenticationError inherits from PolarFlowError."""
    error = AuthenticationError("Invalid token")
    assert str(error) == "Invalid token"
    assert isinstance(error, PolarFlowError)


def test_rate_limit_error() -> None:
    """Test RateLimitError with retry_after attribute."""
    error = RateLimitError("Rate limit exceeded", retry_after=60)
    assert str(error) == "Rate limit exceeded"
    assert error.retry_after == 60
    assert isinstance(error, PolarFlowError)


def test_not_found_error() -> None:
    """Test NotFoundError inherits from PolarFlowError."""
    error = NotFoundError("Resource not found")
    assert str(error) == "Resource not found"
    assert isinstance(error, PolarFlowError)


def test_validation_error() -> None:
    """Test ValidationError inherits from PolarFlowError."""
    error = ValidationError("Invalid parameters")
    assert str(error) == "Invalid parameters"
    assert isinstance(error, PolarFlowError)
