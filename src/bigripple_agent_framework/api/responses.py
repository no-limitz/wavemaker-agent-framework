"""
Standard API response wrappers for wavemaker agents.

This module provides consistent response structures and helper functions
for creating success and error responses across all agents.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# ERROR MODELS
# =============================================================================


class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Used to represent error details in API responses.
    """

    success: bool = Field(default=False, description="Always false for error responses")
    error_code: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    http_status: int = Field(default=500, description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "validation_error",
                "message": "Invalid input provided",
                "details": {"field": "url", "issue": "Invalid URL format"},
                "http_status": 400,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


# =============================================================================
# RESPONSE WRAPPERS
# =============================================================================


class SuccessResponse(BaseModel):
    """
    Standard success response wrapper.

    Wraps successful API responses in a consistent format.
    """

    success: bool = Field(default=True, description="Always true for success responses")
    data: Any = Field(..., description="Response payload (can be any type)")
    message: Optional[str] = Field(None, description="Optional success message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123", "status": "completed"},
                "message": "Operation completed successfully",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class ErrorResponseWrapper(BaseModel):
    """
    Standard error response wrapper.

    Wraps error responses in a consistent format.
    """

    success: bool = Field(default=False, description="Always false for error responses")
    error: ErrorResponse = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "error": "not_found",
                    "message": "Resource not found",
                    "timestamp": "2024-01-15T10:30:00Z",
                },
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_success_response(
    data: Any,
    message: Optional[str] = None,
) -> SuccessResponse:
    """
    Create a standardized success response.

    Args:
        data: Response payload (can be any type - dict, Pydantic model, list, etc.)
        message: Optional success message

    Returns:
        SuccessResponse: Wrapped success response

    Example:
        ```python
        from bigripple_agent_framework.api import create_success_response

        # Simple dict response
        return create_success_response(
            data={"id": "123", "status": "completed"},
            message="Analysis completed successfully"
        )

        # Pydantic model response
        result = AnalysisResult(...)
        return create_success_response(
            data=result,
            message="Website analyzed"
        )
        ```
    """
    return SuccessResponse(data=data, message=message)


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    http_status: int = 500,
) -> ErrorResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Error type/code (e.g., "validation_error", "not_found", "internal_error")
        message: Human-readable error message
        details: Optional dictionary with additional error context
        http_status: HTTP status code (default: 500)

    Returns:
        ErrorResponse: Error response

    Example:
        ```python
        from bigripple_agent_framework.api import create_error_response

        # Simple error
        return create_error_response(
            error_code="invalid_url",
            message="The provided URL is not valid",
            http_status=400
        )

        # Error with details
        return create_error_response(
            error_code="validation_error",
            message="Invalid input provided",
            details={"field": "max_pages", "issue": "Must be between 1 and 20"},
            http_status=400
        )
        ```
    """
    return ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        http_status=http_status,
    )


# =============================================================================
# COMMON ERROR CODES
# =============================================================================


class ErrorCodes:
    """
    Common error codes used across agents.

    Use these constants instead of hardcoding error strings.
    """

    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    LLM_ERROR = "LLM_ERROR"
    API_ERROR = "API_ERROR"

    # Agent-specific errors
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    PROCESSING_ERROR = "PROCESSING_ERROR"


# Export all response types
__all__ = [
    "ErrorResponse",
    "SuccessResponse",
    "ErrorResponseWrapper",
    "create_success_response",
    "create_error_response",
    "ErrorCodes",
]
