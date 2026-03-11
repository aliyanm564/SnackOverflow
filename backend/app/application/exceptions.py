"""
exceptions.py
-------------
Application-layer exception hierarchy.

Services raise these typed exceptions instead of generic ValueError or
HTTPException so that:
  * The domain layer stays framework-agnostic.
  * Presentation-layer routers translate them into the correct HTTP status
    codes in one place (see dependencies.py / exception handlers in main.py).

Hierarchy
---------
AppError                   (base – never raised directly)
├── NotFoundError          → 404
├── ConflictError          → 409  (duplicate resource)
├── AuthenticationError    → 401  (bad credentials)
├── AuthorizationError     → 403  (insufficient role)
├── BusinessRuleError      → 422  (domain rule violated)
└── PaymentError           → 402  (simulated payment failure)
"""


class AppError(Exception):
    """Base class for all application-layer errors."""

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
    """Raised when a simulated payment is rejected."""
