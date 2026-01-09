"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_access_token() -> str:
    """Return a mock access token for testing."""
    return "mock_access_token_1234567890"


@pytest.fixture
def mock_user_id() -> str:
    """Return a mock user ID for testing."""
    return "12345678"
