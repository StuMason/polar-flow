"""Tests for OAuth2 authentication."""

import pytest
from pytest_httpx import HTTPXMock

from polar_flow.auth import OAuth2Handler, OAuth2Token
from polar_flow.exceptions import AuthenticationError, PolarFlowError


def test_oauth2_handler_initialization() -> None:
    """Test OAuth2Handler initializes correctly."""
    oauth = OAuth2Handler(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/callback",
    )

    assert oauth.client_id == "test_client_id"
    assert oauth.client_secret == "test_client_secret"
    assert oauth.redirect_uri == "http://localhost:8000/callback"


def test_oauth2_handler_initialization_strips_whitespace() -> None:
    """Test that client_id and client_secret are stripped."""
    oauth = OAuth2Handler(client_id="  client_id  ", client_secret="  client_secret  ")

    assert oauth.client_id == "client_id"
    assert oauth.client_secret == "client_secret"


def test_oauth2_handler_empty_client_id_raises_error() -> None:
    """Test that empty client_id raises ValueError."""
    with pytest.raises(ValueError, match="client_id is required"):
        OAuth2Handler(client_id="", client_secret="secret")

    with pytest.raises(ValueError, match="client_id is required"):
        OAuth2Handler(client_id="   ", client_secret="secret")


def test_oauth2_handler_empty_client_secret_raises_error() -> None:
    """Test that empty client_secret raises ValueError."""
    with pytest.raises(ValueError, match="client_secret is required"):
        OAuth2Handler(client_id="client_id", client_secret="")

    with pytest.raises(ValueError, match="client_secret is required"):
        OAuth2Handler(client_id="client_id", client_secret="   ")


def test_get_authorization_url_with_state() -> None:
    """Test get_authorization_url returns correct URL with state."""
    oauth = OAuth2Handler(
        client_id="test_client",
        client_secret="test_secret",
        redirect_uri="http://localhost:8000/callback",
    )

    url = oauth.get_authorization_url(state="my_random_state")

    assert url.startswith("https://flow.polar.com/oauth2/authorization?")
    assert "response_type=code" in url
    assert "client_id=test_client" in url
    assert "state=my_random_state" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback" in url


def test_get_authorization_url_without_state_generates_random() -> None:
    """Test that get_authorization_url generates random state if not provided."""
    oauth = OAuth2Handler(client_id="test_client", client_secret="test_secret")

    url = oauth.get_authorization_url()

    assert "state=" in url
    # State should be reasonably long (URL-safe random string)
    state_part = next(part for part in url.split("&") if part.startswith("state="))
    state_value = state_part.split("=")[1]
    assert len(state_value) > 20


def test_get_authorization_url_without_redirect_uri() -> None:
    """Test get_authorization_url works without redirect_uri."""
    oauth = OAuth2Handler(client_id="test_client", client_secret="test_secret")

    url = oauth.get_authorization_url(state="test_state")

    assert "redirect_uri" not in url


@pytest.mark.asyncio
async def test_exchange_code_success(httpx_mock: HTTPXMock) -> None:
    """Test successful authorization code exchange."""
    httpx_mock.add_response(
        url="https://polarremote.com/v2/oauth2/token",
        method="POST",
        json={
            "access_token": "test_access_token_12345",
            "token_type": "bearer",
            "x_user_id": 98765432,
        },
    )

    oauth = OAuth2Handler(
        client_id="test_client",
        client_secret="test_secret",
        redirect_uri="http://localhost:8000/callback",
    )

    token = await oauth.exchange_code(code="authorization_code_12345")

    assert isinstance(token, OAuth2Token)
    assert token.access_token == "test_access_token_12345"
    assert token.token_type == "bearer"
    assert token.x_user_id == 98765432
    assert token.user_id == "98765432"  # user_id property returns string


@pytest.mark.asyncio
async def test_exchange_code_empty_code_raises_error() -> None:
    """Test that empty authorization code raises ValueError."""
    oauth = OAuth2Handler(client_id="client", client_secret="secret")

    with pytest.raises(ValueError, match="authorization code is required"):
        await oauth.exchange_code(code="")

    with pytest.raises(ValueError, match="authorization code is required"):
        await oauth.exchange_code(code="   ")


@pytest.mark.asyncio
async def test_exchange_code_400_raises_authentication_error(
    httpx_mock: HTTPXMock,
) -> None:
    """Test that 400 response raises AuthenticationError."""
    httpx_mock.add_response(
        url="https://polarremote.com/v2/oauth2/token",
        method="POST",
        status_code=400,
        json={"error": "invalid_grant", "error_description": "Invalid authorization code"},
    )

    oauth = OAuth2Handler(client_id="client", client_secret="secret")

    with pytest.raises(AuthenticationError, match="Invalid authorization code"):
        await oauth.exchange_code(code="invalid_code")


@pytest.mark.asyncio
async def test_exchange_code_401_raises_authentication_error(
    httpx_mock: HTTPXMock,
) -> None:
    """Test that 401 response raises AuthenticationError for invalid credentials."""
    httpx_mock.add_response(
        url="https://polarremote.com/v2/oauth2/token",
        method="POST",
        status_code=401,
    )

    oauth = OAuth2Handler(client_id="client", client_secret="wrong_secret")

    with pytest.raises(AuthenticationError, match="Invalid client credentials"):
        await oauth.exchange_code(code="auth_code_1234567890")


@pytest.mark.asyncio
async def test_exchange_code_500_raises_polar_flow_error(httpx_mock: HTTPXMock) -> None:
    """Test that 500 response raises PolarFlowError."""
    httpx_mock.add_response(
        url="https://polarremote.com/v2/oauth2/token",
        method="POST",
        status_code=500,
        text="Internal server error",
    )

    oauth = OAuth2Handler(client_id="client", client_secret="secret")

    with pytest.raises(PolarFlowError, match="Token exchange failed with status 500"):
        await oauth.exchange_code(code="auth_code_1234567890")


@pytest.mark.asyncio
async def test_exchange_code_sends_correct_request(httpx_mock: HTTPXMock) -> None:
    """Test that exchange_code sends correct POST request."""
    httpx_mock.add_response(
        url="https://polarremote.com/v2/oauth2/token",
        method="POST",
        json={
            "access_token": "token",
            "token_type": "bearer",
            "x_user_id": 123,
        },
    )

    oauth = OAuth2Handler(
        client_id="my_client_id",
        client_secret="my_client_secret",
        redirect_uri="http://localhost:8000/callback",
    )

    await oauth.exchange_code(code="my_auth_code")

    request = httpx_mock.get_requests()[0]
    assert request.method == "POST"
    assert request.url == "https://polarremote.com/v2/oauth2/token"
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert request.headers["Accept"] == "application/json;charset=UTF-8"

    # Check HTTP Basic Auth header (base64 encoded client_id:client_secret)
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")

    # Check request body (credentials should NOT be in body, they're in Auth header)
    body = request.content.decode("utf-8")
    assert "grant_type=authorization_code" in body
    assert "code=my_auth_code" in body
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback" in body
    assert "client_id" not in body  # Should be in Authorization header, not body
    assert "client_secret" not in body  # Should be in Authorization header, not body
