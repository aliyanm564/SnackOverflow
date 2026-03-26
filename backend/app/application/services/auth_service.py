import os
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt as _bcrypt_lib

from backend.app.application.exceptions import (
    AuthenticationError,
    ConflictError,
)
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.user_repository import UserRepository

_JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
_JWT_ALGORITHM = "HS256"
_JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

def _hash_password(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode(), _bcrypt_lib.gensalt()).decode()

def _verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt_lib.checkpw(plain.encode(), hashed.encode())


class AuthService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def register(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.CUSTOMER,
        name: str | None = None,
        age: int | None = None,
        gender: str | None = None,
        location: str | None = None,
        preferred_cuisine: str | None = None,
        order_frequency: str | None = None,
        loyalty_program: bool = False,
    ) -> User:

        if self._users.get_by_email(email) is not None:
            raise ConflictError(f"Email '{email}' is already registered.")

        customer_id = str(uuid.uuid4())
        new_user = User(
            customer_id=customer_id,
            name=name,
            age=age,
            gender=gender,
            location=location,
            loyalty_program=loyalty_program,
            preferred_cuisine=preferred_cuisine,
            order_frequency=order_frequency,
            role=role,
        )
        saved_user = self._users.save(new_user)

        hashed = _hash_password(password)
        self._users.set_hashed_password(saved_user.customer_id, hashed)
        self._store_email(saved_user.customer_id, email)

        return saved_user

    def login(self, email: str, password: str) -> str:

        user = self._users.get_by_email(email)
        if user is None:
            raise AuthenticationError("Invalid email or password.")

        stored_hash = self._users.get_hashed_password(user.customer_id)
        if not stored_hash or not _verify_password(password, stored_hash):
            raise AuthenticationError("Invalid email or password.")

        return self._create_token(user.customer_id, user.role)

    def verify_token(self, token: str) -> tuple[str, UserRole]:
        try:
            payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
            customer_id: str = payload.get("sub")
            role_str: str = payload.get("role", UserRole.CUSTOMER.value)
            if customer_id is None:
                raise AuthenticationError("Token missing subject claim.")
            return customer_id, UserRole(role_str)
        except JWTError as exc:
            raise AuthenticationError(f"Token invalid or expired: {exc}") from exc

    def _create_token(self, customer_id: str, role: UserRole) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=_JWT_EXPIRE_MINUTES)
        payload = {
            "sub": customer_id,
            "role": role.value,
            "exp": expire,
        }
        return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)

    def _store_email(self, customer_id: str, email: str) -> None:

        from backend.app.infrastructure.orm_models import UserORM

        orm_obj = self._users._db.get(UserORM, customer_id)
        if orm_obj:
            orm_obj.email = email
            self._users._db.flush()
