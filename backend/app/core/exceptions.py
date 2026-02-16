"""
Custom exceptions
"""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception"""
    pass


class ValidationError(AppException):
    """Validation error"""
    def __init__(self, message: str, details: list = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": details or []
            }
        )


class AuthenticationError(AppException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": message
            }
        )


class AuthorizationError(AppException):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AUTHORIZATION_FAILED",
                "message": message
            }
        )


class NotFoundError(AppException):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RESOURCE_NOT_FOUND",
                "message": message
            }
        )


class ConflictError(AppException):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RESOURCE_CONFLICT",
                "message": message
            }
        )


class BusinessRuleError(AppException):
    """Business rule violation error"""
    def __init__(self, message: str, code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": code,
                "message": message
            }
        )


class RateLimitError(AppException):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": message
            }
        )

