from backend.app.domain.models.user import User, UserRole


def can_access_feature(user: User, required_role: UserRole) -> bool:
    return user.role == required_role
