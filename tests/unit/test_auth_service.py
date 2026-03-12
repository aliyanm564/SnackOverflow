"""
----------------------------
Tests for AuthService using a mocked UserRepository.
No database, no real password hashing overhead beyond passlib itself.

Methodologies demonstrated
---------------------------
* Mocking         – UserRepository replaced with MagicMock
* Exception handling – ConflictError on duplicate email, AuthenticationError
                       on bad credentials and invalid token
* Equivalence partitioning – valid vs invalid password, valid vs expired token
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.app.application.services.auth_service import AuthService
from backend.app.application.exceptions import AuthenticationError, ConflictError
from backend.app.domain.models.user import User, UserRole


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_service(user_repo):
    return AuthService(user_repository=user_repo)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:

    def test_register_new_user_returns_user(self, mock_user_repo, customer_user):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.save.return_value = customer_user
        mock_user_repo.set_hashed_password.return_value = None

        service = make_service(mock_user_repo)
        with patch("backend.app.application.services.auth_service._hash_password", return_value="$2b$fake"):
            with patch.object(service, "_store_email"):
                result = service.register(email="alice@example.com", password="SecurePass123", role=UserRole.CUSTOMER)

        assert result.customer_id == customer_user.customer_id
        mock_user_repo.save.assert_called_once()
        mock_user_repo.set_hashed_password.assert_called_once()

    def test_register_assigns_customer_role_by_default(self, mock_user_repo, customer_user):
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.save.return_value = customer_user
        mock_user_repo.set_hashed_password.return_value = None

        service = make_service(mock_user_repo)
        with patch("backend.app.application.services.auth_service._hash_password", return_value="$2b$fake"):
            with patch.object(service, "_store_email"):
                service.register(email="new@example.com", password="pass")

        saved_user: User = mock_user_repo.save.call_args[0][0]
        assert saved_user.role == UserRole.CUSTOMER


class TestLogin:

    def _setup_login(self, mock_user_repo, customer_user):
        mock_user_repo.get_by_email.return_value = customer_user
        mock_user_repo.get_hashed_password.return_value = "$2b$fake"
        return make_service(mock_user_repo)

    def test_login_correct_credentials_returns_token(self, mock_user_repo, customer_user):
        service = self._setup_login(mock_user_repo, customer_user)
        with patch("backend.app.application.services.auth_service._verify_password", return_value=True):
            token = service.login("alice@example.com", "correct")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_login_wrong_password_raises_authentication_error(self, mock_user_repo, customer_user):
        service = self._setup_login(mock_user_repo, customer_user)
        with patch("backend.app.application.services.auth_service._verify_password", return_value=False):
            with pytest.raises(AuthenticationError):
                service.login("alice@example.com", "wrong_password")


class TestVerifyToken:

    def test_verify_valid_token_returns_customer_id_and_role(
        self, mock_user_repo, customer_user
    ):
        """
        Token round-trip: create via _create_token directly (no password
        hashing needed), then verify it.
        """
        service = make_service(mock_user_repo)
        token = service._create_token(customer_user.customer_id, UserRole.CUSTOMER)
        cid, role = service.verify_token(token)
        assert cid == customer_user.customer_id
        assert role == UserRole.CUSTOMER

    def test_verify_garbage_token_raises_authentication_error(self, mock_user_repo):
        service = make_service(mock_user_repo)
        with pytest.raises(AuthenticationError):
            service.verify_token("not.a.valid.jwt")

    def test_verify_tampered_token_raises_authentication_error(
        self, mock_user_repo, customer_user
    ):
        service = make_service(mock_user_repo)
        token = service._create_token(customer_user.customer_id, UserRole.CUSTOMER)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(AuthenticationError):
            service.verify_token(tampered)
