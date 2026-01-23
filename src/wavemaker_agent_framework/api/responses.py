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

    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid input provided",
                "details": {"field": "url", "issue": "Invalid URL format"},
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_123abc",
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
        from wavemaker_agent_framework.api import create_success_response

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
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponseWrapper:
    """
    Create a standardized error response.

    Args:
        error: Error type/code (e.g., "validation_error", "not_found", "internal_error")
        message: Human-readable error message
        details: Optional dictionary with additional error context
        request_id: Optional request ID for tracking

    Returns:
        ErrorResponseWrapper: Wrapped error response

    Example:
        ```python
        from wavemaker_agent_framework.api import create_error_response

        # Simple error
        return create_error_response(
            error="invalid_url",
            message="The provided URL is not valid"
        )

        # Error with details
        return create_error_response(
            error="validation_error",
            message="Invalid input provided",
            details={"field": "max_pages", "issue": "Must be between 1 and 20"},
            request_id="req_abc123"
        )
        ```
    """
    error_obj = ErrorResponse(
        error=error,
        message=message,
        details=details,
        request_id=request_id,
    )
    return ErrorResponseWrapper(error=error_obj)


# =============================================================================
# COMMON ERROR CODES
# =============================================================================


class ErrorCodes:
    """
    Common error codes used across agents.

    Use these constants instead of hardcoding error strings.
    """

    # Client errors (4xx)
    VALIDATION_ERROR = "validation_error"
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Server errors (5xx)
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT = "timeout"
    LLM_ERROR = "llm_error"

    # Agent-specific errors
    ANALYSIS_FAILED = "analysis_failed"
    EXTRACTION_FAILED = "extraction_failed"
    PROCESSING_ERROR = "processing_error"


# Export all response types
__all__ = [
    "ErrorResponse",
    "SuccessResponse",
    "ErrorResponseWrapper",
    "create_success_response",
    "create_error_response",
    "ErrorCodes",
]
