import pytest
from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthenticationError, ConflictError
from backend.app.presentation.dependencies import get_auth_service
from backend.app.domain.models.user import UserRole


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


@pytest.fixture
def mock_auth_svc(customer):
    svc = MagicMock()
    svc.register.return_value = customer
    svc.login.return_value = "mock.jwt.token"
    return svc


class TestRegisterEndpoint:

    def test_successful_registration_returns_201(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(REGISTER_URL, json={
                "email": "new@example.com",
                "password": "SecurePass1",
                "name": "Alice",
            })
        assert resp.status_code == 201
        body = resp.json()
        assert "customer_id" in body
        assert "hashed_password" not in body

    def test_duplicate_email_returns_409(self, client, mock_auth_svc, override):
        mock_auth_svc.register.side_effect = ConflictError("Email already registered.")
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(REGISTER_URL, json={
                "email": "dup@example.com",
                "password": "pass123",
            })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"]

    def test_password_too_short_returns_422(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(REGISTER_URL, json={
                "email": "short@example.com",
                "password": "ab",
            })
        assert resp.status_code == 422

    def test_missing_email_returns_422(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(REGISTER_URL, json={"password": "pass123"})
        assert resp.status_code == 422

    def test_invalid_role_returns_400(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(REGISTER_URL, json={
                "email": "r@example.com",
                "password": "pass123",
                "role": "superadmin",
            })
        assert resp.status_code == 400


class TestLoginEndpoint:

    def test_successful_login_returns_token(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(LOGIN_URL, json={
                "email": "alice@example.com",
                "password": "correct",
            })
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"] == "mock.jwt.token"
        assert body["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client, mock_auth_svc, override):
        mock_auth_svc.login.side_effect = AuthenticationError("Invalid email or password.")
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(LOGIN_URL, json={
                "email": "alice@example.com",
                "password": "wrong",
            })
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    def test_missing_password_returns_422(self, client, mock_auth_svc, override):
        with override(get_auth_service, mock_auth_svc):
            resp = client.post(LOGIN_URL, json={"email": "alice@example.com"})
        assert resp.status_code == 422

    def test_unauthenticated_request_to_protected_route_returns_401(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401
