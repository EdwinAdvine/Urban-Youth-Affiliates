"""
Custom application exceptions.
"""

from fastapi import status


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "APP_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
        )


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
        )


class PaymentError(AppError):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="PAYMENT_ERROR",
        )
