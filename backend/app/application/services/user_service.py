from typing import List, Optional

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.user import User, UserRole
from backend.app.domain.rules.role_rules import can_access_feature
from backend.app.infrastructure.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def get_user(self, customer_id: str) -> User:
        user = self._users.get_by_id(customer_id)
        if user is None:
            raise NotFoundError(f"User '{customer_id}' not found.")
        return user

    def list_users(
        self,
        role: Optional[UserRole] = None,
        location: Optional[str] = None,
    ) -> List[User]:
        if role is not None:
            users = self._users.get_by_role(role)
        else:
            users = self._users.get_all()

        if location is not None:
            users = [u for u in users if u.location == location]

        return users

    def update_profile(
        self,
        customer_id: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        location: Optional[str] = None,
        preferred_cuisine: Optional[str] = None,
        order_frequency: Optional[str] = None,
        loyalty_program: Optional[bool] = None,
    ) -> User:
        user = self.get_user(customer_id)

        if name is not None:
            user = user.model_copy(update={"name": name})
        if age is not None:
            user = user.model_copy(update={"age": age})
        if gender is not None:
            user = user.model_copy(update={"gender": gender})
        if location is not None:
            user = user.model_copy(update={"location": location})
        if preferred_cuisine is not None:
            user = user.model_copy(update={"preferred_cuisine": preferred_cuisine})
        if order_frequency is not None:
            user = user.model_copy(update={"order_frequency": order_frequency})
        if loyalty_program is not None:
            user = user.model_copy(update={"loyalty_program": loyalty_program})

        return self._users.save(user)

    def change_role(
        self,
        requesting_user: User,
        target_customer_id: str,
        new_role: UserRole,
    ) -> User:
        if not can_access_feature(requesting_user, UserRole.RESTAURANT_OWNER):
            raise AuthorizationError("Only restaurant owners can change user roles.")

        target = self.get_user(target_customer_id)
        updated = target.model_copy(update={"role": new_role})
        return self._users.save(updated)

    def delete_user(self, customer_id: str) -> None:
        if not self._users.delete(customer_id):
            raise NotFoundError(f"User '{customer_id}' not found.")
