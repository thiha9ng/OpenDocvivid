from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    Base application exception
    """
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(AppException):
    """
    400 Bad Request
    """
    def __init__(
        self,
        detail: Any = "Bad Request",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
        )


class UnauthorizedException(AppException):
    """
    401 Unauthorized
    """
    def __init__(
        self,
        detail: Any = "Unauthorized",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class ForbiddenException(AppException):
    """
    403 Forbidden
    """
    def __init__(
        self,
        detail: Any = "Forbidden",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class NotFoundException(AppException):
    """
    404 Not Found
    """
    def __init__(
        self,
        detail: Any = "Not Found",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class ConflictException(AppException):
    """
    409 Conflict
    """
    def __init__(
        self,
        detail: Any = "Resource Conflict",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers,
        )


class InternalServerException(AppException):
    """
    500 Internal Server Error
    """
    def __init__(
        self,
        detail: Any = "Internal Server Error",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class URLAccessException(AppException):
    """
    502 Bad Gateway - URL access error
    """
    def __init__(
        self,
        detail: Any = "Failed to access the provided URL",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            headers=headers,
        )


class FileProcessingException(AppException):
    """
    400 Bad Request - File processing error
    """
    def __init__(
        self,
        detail: Any = "Failed to process the uploaded file",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
        )


class StorageException(AppException):
    """
    500 Internal Server Error - Storage operation error
    """
    def __init__(
        self,
        detail: Any = "Failed to perform storage operation",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class TokenLimitExceededException(AppException):
    """
    413 Payload Too Large - Token limit exceeded
    """
    def __init__(
        self,
        detail: Any = "Input text exceeds the maximum token limit, please reduce the text length.",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=detail,
            headers=headers,
        )


class InsufficientCreditException(AppException):
    """
    402 Payment Required - Insufficient credit balance
    """
    def __init__(
        self,
        detail: Any = "Insufficient credit balance. Please purchase more credits to continue.",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            headers=headers,
        ) 