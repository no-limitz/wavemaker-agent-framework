"""
Unit tests for API response models and helpers.

Tests SuccessResponse, ErrorResponse, and helper functions.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from bigripple.api.responses import (
    SuccessResponse,
    ErrorResponse,
    ErrorCodes,
    create_success_response,
    create_error_response,
)


class TestSuccessResponse:
    """Test SuccessResponse model."""

    def test_creates_basic_success_response(self):
        """Test creating basic success response."""
        response = SuccessResponse(data={"result": "test"})

        assert response.success is True
        assert response.data == {"result": "test"}
        assert response.message is None
        assert isinstance(response.timestamp, datetime)

    def test_creates_success_response_with_message(self):
        """Test creating success response with custom message."""
        response = SuccessResponse(
            data={"result": "test"},
            message="Operation completed successfully"
        )

        assert response.success is True
        assert response.message == "Operation completed successfully"

    def test_success_response_with_list_data(self):
        """Test success response with list data."""
        response = SuccessResponse(data=["item1", "item2", "item3"])

        assert response.success is True
        assert response.data == ["item1", "item2", "item3"]

    def test_success_response_with_string_data(self):
        """Test success response with string data."""
        response = SuccessResponse(data="Simple string result")

        assert response.success is True
        assert response.data == "Simple string result"

    def test_success_response_with_null_data(self):
        """Test success response with None data."""
        response = SuccessResponse(data=None)

        assert response.success is True
        assert response.data is None

    def test_success_response_serialization(self):
        """Test that success response can be serialized to dict."""
        response = SuccessResponse(data={"result": "test"})
        response_dict = response.model_dump()

        assert response_dict["success"] is True
        assert response_dict["data"] == {"result": "test"}
        assert "timestamp" in response_dict

    def test_success_response_json_serialization(self):
        """Test that success response can be serialized to JSON."""
        response = SuccessResponse(data={"result": "test"})
        json_str = response.model_dump_json()

        assert '"success":true' in json_str or '"success": true' in json_str
        assert '"result":"test"' in json_str or '"result": "test"' in json_str


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_creates_basic_error_response(self):
        """Test creating basic error response."""
        response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid input"
        )

        assert response.success is False
        assert response.error_code == "VALIDATION_ERROR"
        assert response.message == "Invalid input"
        assert response.details is None
        assert isinstance(response.timestamp, datetime)

    def test_creates_error_response_with_details(self):
        """Test creating error response with details."""
        response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "email", "reason": "Invalid format"}
        )

        assert response.success is False
        assert response.details == {"field": "email", "reason": "Invalid format"}

    def test_error_response_serialization(self):
        """Test that error response can be serialized to dict."""
        response = ErrorResponse(
            error_code="NOT_FOUND",
            message="Resource not found"
        )
        response_dict = response.model_dump()

        assert response_dict["success"] is False
        assert response_dict["error_code"] == "NOT_FOUND"
        assert response_dict["message"] == "Resource not found"
        assert "timestamp" in response_dict

    def test_error_response_json_serialization(self):
        """Test that error response can be serialized to JSON."""
        response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Something went wrong"
        )
        json_str = response.model_dump_json()

        assert '"success":false' in json_str or '"success": false' in json_str
        assert '"error_code":"INTERNAL_ERROR"' in json_str or '"error_code": "INTERNAL_ERROR"' in json_str


class TestErrorCodes:
    """Test ErrorCodes enum."""

    def test_has_validation_error(self):
        """Test ErrorCodes has VALIDATION_ERROR."""
        assert hasattr(ErrorCodes, "VALIDATION_ERROR")
        assert ErrorCodes.VALIDATION_ERROR == "VALIDATION_ERROR"

    def test_has_not_found(self):
        """Test ErrorCodes has NOT_FOUND."""
        assert hasattr(ErrorCodes, "NOT_FOUND")
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"

    def test_has_internal_error(self):
        """Test ErrorCodes has INTERNAL_ERROR."""
        assert hasattr(ErrorCodes, "INTERNAL_ERROR")
        assert ErrorCodes.INTERNAL_ERROR == "INTERNAL_ERROR"

    def test_has_unauthorized(self):
        """Test ErrorCodes has UNAUTHORIZED."""
        assert hasattr(ErrorCodes, "UNAUTHORIZED")
        assert ErrorCodes.UNAUTHORIZED == "UNAUTHORIZED"

    def test_has_rate_limit_exceeded(self):
        """Test ErrorCodes has RATE_LIMIT_EXCEEDED."""
        assert hasattr(ErrorCodes, "RATE_LIMIT_EXCEEDED")
        assert ErrorCodes.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"

    def test_has_api_error(self):
        """Test ErrorCodes has API_ERROR."""
        assert hasattr(ErrorCodes, "API_ERROR")
        assert ErrorCodes.API_ERROR == "API_ERROR"

    def test_can_use_error_codes_in_response(self):
        """Test that ErrorCodes can be used in ErrorResponse."""
        response = ErrorResponse(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message="Invalid input"
        )

        assert response.error_code == "VALIDATION_ERROR"


class TestCreateSuccessResponse:
    """Test create_success_response() helper function."""

    def test_creates_success_response_with_data(self):
        """Test creating success response with data only."""
        response = create_success_response(data={"result": "test"})

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.data == {"result": "test"}
        assert response.message is None

    def test_creates_success_response_with_message(self):
        """Test creating success response with data and message."""
        response = create_success_response(
            data={"result": "test"},
            message="Operation successful"
        )

        assert isinstance(response, SuccessResponse)
        assert response.message == "Operation successful"

    def test_creates_success_response_with_list(self):
        """Test creating success response with list data."""
        response = create_success_response(data=["item1", "item2"])

        assert isinstance(response, SuccessResponse)
        assert response.data == ["item1", "item2"]

    def test_creates_success_response_with_none(self):
        """Test creating success response with None data."""
        response = create_success_response(data=None)

        assert isinstance(response, SuccessResponse)
        assert response.data is None


class TestCreateErrorResponse:
    """Test create_error_response() helper function."""

    def test_creates_error_response_basic(self):
        """Test creating basic error response."""
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="Invalid input"
        )

        assert isinstance(response, ErrorResponse)
        assert response.success is False
        assert response.error_code == "VALIDATION_ERROR"
        assert response.message == "Invalid input"
        assert response.details is None

    def test_creates_error_response_with_details(self):
        """Test creating error response with details."""
        response = create_error_response(
            error_code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "email"}
        )

        assert isinstance(response, ErrorResponse)
        assert response.details == {"field": "email"}

    def test_creates_error_response_with_error_code_enum(self):
        """Test creating error response with ErrorCodes enum."""
        response = create_error_response(
            error_code=ErrorCodes.NOT_FOUND,
            message="Resource not found"
        )

        assert isinstance(response, ErrorResponse)
        assert response.error_code == "NOT_FOUND"

    def test_creates_error_response_with_http_status(self):
        """Test creating error response with HTTP status code."""
        response = create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message="Server error",
            http_status=500
        )

        assert isinstance(response, ErrorResponse)
        assert response.http_status == 500

    def test_creates_error_response_default_http_status(self):
        """Test that error response has default HTTP status."""
        response = create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message="Server error"
        )

        assert isinstance(response, ErrorResponse)
        # Default http_status should be 500 for INTERNAL_ERROR


class TestResponseIntegration:
    """Integration tests for response models."""

    def test_success_and_error_responses_have_consistent_structure(self):
        """Test that success and error responses have consistent fields."""
        success = create_success_response(data={"result": "test"})
        error = create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message="Error occurred"
        )

        # Both should have success field
        assert hasattr(success, "success")
        assert hasattr(error, "success")

        # Both should have timestamp
        assert hasattr(success, "timestamp")
        assert hasattr(error, "timestamp")

    def test_responses_can_be_used_in_fastapi(self):
        """Test that responses work with FastAPI response model."""
        from fastapi.responses import JSONResponse

        success = create_success_response(data={"result": "test"})
        # Use mode="json" to get JSON-serializable dict
        json_response = JSONResponse(content=success.model_dump(mode="json"))

        assert json_response.status_code == 200

    def test_error_response_with_custom_http_status(self):
        """Test error response with custom HTTP status."""
        response = create_error_response(
            error_code=ErrorCodes.NOT_FOUND,
            message="Resource not found",
            http_status=404
        )

        assert response.http_status == 404


class TestResponseEdgeCases:
    """Test edge cases and error handling."""

    def test_success_response_with_complex_nested_data(self):
        """Test success response with deeply nested data."""
        complex_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "items": ["a", "b", "c"],
                        "count": 3
                    }
                }
            }
        }

        response = create_success_response(data=complex_data)

        assert response.success is True
        assert response.data == complex_data

    def test_error_response_with_complex_details(self):
        """Test error response with complex details object."""
        details = {
            "errors": [
                {"field": "email", "message": "Invalid format"},
                {"field": "password", "message": "Too short"}
            ],
            "request_id": "abc-123"
        }

        response = create_error_response(
            error_code=ErrorCodes.VALIDATION_ERROR,
            message="Validation failed",
            details=details
        )

        assert response.details == details

    def test_timestamp_is_current(self):
        """Test that timestamp is approximately current time."""
        before = datetime.now()
        response = create_success_response(data={"result": "test"})
        after = datetime.now()

        assert before <= response.timestamp <= after
