"""
---------------------------------
End-to-end tests for registration and login using a real UserRepository
wired to in-memory SQLite.

Flow tested
-----------
1. Register a new user → persisted in DB with hashed password.
2. Login with correct credentials → JWT returned.
3. Verify the JWT → customer_id and role decoded correctly.
4. Duplicate registration → ConflictError.
5. Login with wrong password → AuthenticationError.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.application.services.auth_service import AuthService
from backend.app.application.exceptions import AuthenticationError, ConflictError
from backend.app.domain.models.user import UserRole


# ---------------------------------------------------------------------------
# Integration fixture: wired auth service
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_setup(db_session: Session):
    user_repo = UserRepository(db_session)
    service = AuthService(user_repository=user_repo)
    return {"service": service, "db": db_session}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAuthFlow:

    def test_register_persists_user_in_database(self, auth_setup):
        """Registered user can be retrieved from the DB by email."""
        svc: AuthService = auth_setup["service"]
        repo = UserRepository(auth_setup["db"])

        user = svc.register(
            email="test@example.com",
            password="StrongPass99",
            role=UserRole.CUSTOMER,
            name="Test User",
        )

        assert user.customer_id is not None
        found = repo.get_by_email("test@example.com")
        assert found is not None
        assert found.customer_id == user.customer_id

    def test_register_hashes_password(self, auth_setup):
        """The stored hash must not equal the plaintext password."""
        svc: AuthService = auth_setup["service"]
        repo = UserRepository(auth_setup["db"])

        user = svc.register(email="hash@example.com", password="MySecret")
        stored = repo.get_hashed_password(user.customer_id)

        assert stored is not None
        assert stored != "MySecret"
        assert stored.startswith("$2b$")   # bcrypt prefix

    def test_register_duplicate_email_raises_conflict(self, auth_setup):
        """Fault injection: same email registered twice."""
        svc: AuthService = auth_setup["service"]
        svc.register(email="dup@example.com", password="pass1")

        with pytest.raises(ConflictError) as exc_info:
            svc.register(email="dup@example.com", password="pass2")
        assert "already registered" in str(exc_info.value)

    def test_login_correct_credentials_returns_jwt(self, auth_setup):
        """Happy path: correct email + password → non-empty token string."""
        svc: AuthService = auth_setup["service"]
        svc.register(email="login@example.com", password="CorrectPass")
        token = svc.login("login@example.com", "CorrectPass")

        assert isinstance(token, str)
        assert len(token) > 30

    def test_login_wrong_password_raises_authentication_error(self, auth_setup):
        """Equivalence partition: wrong password → AuthenticationError."""
        svc: AuthService = auth_setup["service"]
        svc.register(email="wrong@example.com", password="RightPassword")

        with pytest.raises(AuthenticationError):
            svc.login("wrong@example.com", "WrongPassword")

    def test_login_unknown_email_raises_authentication_error(self, auth_setup):
        """Fault injection: email not in DB."""
        svc: AuthService = auth_setup["service"]
        with pytest.raises(AuthenticationError):
            svc.login("nobody@example.com", "whatever")

    def test_verify_token_roundtrip(self, auth_setup):
        """Token issued on login must decode to the correct customer_id and role."""
        svc: AuthService = auth_setup["service"]
        user = svc.register(
            email="verify@example.com",
            password="Pass",
            role=UserRole.RESTAURANT_OWNER,
        )
        token = svc.login("verify@example.com", "Pass")
        customer_id, role = svc.verify_token(token)

        assert customer_id == user.customer_id
        assert role == UserRole.RESTAURANT_OWNER

    def test_verify_tampered_token_raises_authentication_error(self, auth_setup):
        """Fault injection: tampered JWT → AuthenticationError."""
        svc: AuthService = auth_setup["service"]
        svc.register(email="tamper@example.com", password="Pass")
        token = svc.login("tamper@example.com", "Pass")
        tampered = token[:-8] + "TAMPERED"

        with pytest.raises(AuthenticationError):
            svc.verify_token(tampered)
