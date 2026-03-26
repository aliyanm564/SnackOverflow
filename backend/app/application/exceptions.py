class AppError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""


class ConflictError(AppError):
    """Raised when trying to create a resource that already exists."""


class AuthenticationError(AppError):
    """Raised when credentials are invalid or a token cannot be verified."""


class AuthorizationError(AppError):
    """Raised when a user lacks the required role for an operation."""


class BusinessRuleError(AppError):
    """Raised when a domain business rule is violated (e.g. modifying a completed order)."""


class PaymentError(AppError):
    """Raised when a payment is declined or fails to process."""
