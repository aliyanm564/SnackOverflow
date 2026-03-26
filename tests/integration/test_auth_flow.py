import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.application.services.auth_service import AuthService
from backend.app.application.exceptions import AuthenticationError, ConflictError
from backend.app.domain.models.user import UserRole

@pytest.fixture
def auth_setup(db_session: Session):
    user_repo = UserRepository(db_session)
    service = AuthService(user_repository=user_repo)
    return {"service": service, "db": db_session}

class TestAuthFlow:

    def test_register_persists_user_in_database(self, auth_setup):
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
        svc: AuthService = auth_setup["service"]
        repo = UserRepository(auth_setup["db"])

        user = svc.register(email="hash@example.com", password="MySecret")
        stored = repo.get_hashed_password(user.customer_id)

        assert stored is not None
        assert stored != "MySecret"
        assert stored.startswith("$2b$")   # bcrypt prefix

    def test_register_duplicate_email_raises_conflict(self, auth_setup):
        svc: AuthService = auth_setup["service"]
        svc.register(email="dup@example.com", password="pass1")

        with pytest.raises(ConflictError) as exc_info:
            svc.register(email="dup@example.com", password="pass2")
        assert "already registered" in str(exc_info.value)

    def test_login_correct_credentials_returns_jwt(self, auth_setup):
        svc: AuthService = auth_setup["service"]
        svc.register(email="login@example.com", password="CorrectPass")
        token = svc.login("login@example.com", "CorrectPass")

        assert isinstance(token, str)
        assert len(token) > 30

    def test_login_wrong_password_raises_authentication_error(self, auth_setup):
        svc: AuthService = auth_setup["service"]
        svc.register(email="wrong@example.com", password="RightPassword")

        with pytest.raises(AuthenticationError):
            svc.login("wrong@example.com", "WrongPassword")

    def test_login_unknown_email_raises_authentication_error(self, auth_setup):
        svc: AuthService = auth_setup["service"]
        with pytest.raises(AuthenticationError):
            svc.login("nobody@example.com", "whatever")

    def test_verify_token_roundtrip(self, auth_setup):
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
        svc: AuthService = auth_setup["service"]
        svc.register(email="tamper@example.com", password="Pass")
        token = svc.login("tamper@example.com", "Pass")
        tampered = token[:-8] + "TAMPERED"

        with pytest.raises(AuthenticationError):
            svc.verify_token(tampered)
