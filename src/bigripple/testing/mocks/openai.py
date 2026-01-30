"""
Mock OpenAI client utilities for testing without making real API calls.

This module provides utilities to mock OpenAI API responses for deterministic testing
across all wavemaker agents.
"""

from typing import Any, Callable, Dict, Optional
from unittest.mock import AsyncMock, MagicMock


# =============================================================================
# MOCK RESPONSE CLASS
# =============================================================================


class MockOpenAIResponse:
    """
    Mock OpenAI API response object.

    Mimics the structure of actual OpenAI API responses for testing purposes.
    """

    def __init__(self, content: str, model: str = "gpt-4o-mini"):
        """
        Initialize mock response.

        Args:
            content: The response content (usually JSON string)
            model: Model name to include in response
        """
        self.id = "chatcmpl-mock-123"
        self.object = "chat.completion"
        self.created = 1234567890
        self.model = model

        # Create message mock
        message_mock = MagicMock()
        message_mock.role = "assistant"
        message_mock.content = content

        # Create choice mock
        choice_mock = MagicMock()
        choice_mock.index = 0
        choice_mock.message = message_mock
        choice_mock.finish_reason = "stop"

        self.choices = [choice_mock]

        # Create usage mock
        usage_mock = MagicMock()
        usage_mock.prompt_tokens = 100
        usage_mock.completion_tokens = 200
        usage_mock.total_tokens = 300

        self.usage = usage_mock


# =============================================================================
# MOCK CLIENT CREATION
# =============================================================================


def create_mock_openai_client(response_content: Optional[str] = None) -> MagicMock:
    """
    Create a mocked OpenAI client that returns predetermined responses.

    Args:
        response_content: Optional custom response content. If None, uses default.

    Returns:
        MagicMock: Mock client configured to behave like OpenAI AsyncOpenAI client

    Usage:
        ```python
        from bigripple.testing.mocks import create_mock_openai_client

        # Create mock client
        mock_client = create_mock_openai_client('{"result": "success"}')

        # Use in your code
        response = await mock_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )
        assert response.choices[0].message.content == '{"result": "success"}'
        ```
    """
    if response_content is None:
        response_content = '{"result": "test response"}'

    mock_response = MockOpenAIResponse(response_content)
    mock_create = AsyncMock(return_value=mock_response)

    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    return mock_client


# =============================================================================
# ERROR MOCKING
# =============================================================================


def create_mock_openai_error(error_type: str = "rate_limit") -> MagicMock:
    """
    Create a mocked OpenAI client that raises errors.

    Args:
        error_type: Type of error to raise:
            - "rate_limit": RateLimitError (429)
            - "invalid_key": AuthenticationError (401)
            - "timeout": APITimeoutError
            - Any other value: Generic APIError

    Returns:
        MagicMock: Mock client that raises the specified error

    Usage:
        ```python
        from bigripple.testing.mocks import create_mock_openai_error
        import pytest

        async def test_rate_limit_handling():
            mock_client = create_mock_openai_error("rate_limit")

            with pytest.raises(RateLimitError):
                await mock_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "test"}]
                )
        ```
    """
    mock_create = AsyncMock()

    if error_type == "rate_limit":
        from openai import RateLimitError
        mock_create.side_effect = RateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None
        )
    elif error_type == "invalid_key":
        from openai import AuthenticationError
        mock_create.side_effect = AuthenticationError(
            "Invalid API key",
            response=MagicMock(status_code=401),
            body=None
        )
    elif error_type == "timeout":
        from openai import APITimeoutError
        mock_create.side_effect = APITimeoutError(request=MagicMock())
    else:
        from openai import APIError
        mock_create.side_effect = APIError(
            f"Mock error: {error_type}",
            request=MagicMock(),
            body=None
        )

    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    return mock_client


# =============================================================================
# BUILDER PATTERN
# =============================================================================


class MockOpenAIClientBuilder:
    """
    Builder class for creating complex mock OpenAI client scenarios.

    Allows building mock clients that return different responses
    for successive API calls, useful for testing multi-step workflows.

    Usage:
        ```python
        from bigripple.testing.mocks import MockOpenAIClientBuilder

        # Build client with multiple sequential responses
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .with_response('{"step": 2}')
                  .with_response('{"step": 3}')
                  .build())

        # First call returns step 1
        response1 = await client.chat.completions.create(...)
        assert response1.choices[0].message.content == '{"step": 1}'

        # Second call returns step 2
        response2 = await client.chat.completions.create(...)
        assert response2.choices[0].message.content == '{"step": 2}'
        ```
    """

    def __init__(self):
        """Initialize builder with empty response list."""
        self.responses = []
        self.call_count = 0

    def with_response(self, content: str) -> "MockOpenAIClientBuilder":
        """
        Add a custom response to the sequence.

        Args:
            content: Response content string (usually JSON)

        Returns:
            Self for method chaining
        """
        self.responses.append(content)
        return self

    def with_json_response(self, data: Dict[str, Any]) -> "MockOpenAIClientBuilder":
        """
        Add a JSON response to the sequence.

        Args:
            data: Dictionary to serialize as JSON

        Returns:
            Self for method chaining
        """
        import json
        self.responses.append(json.dumps(data))
        return self

    def with_error(self, error_type: str = "rate_limit") -> "MockOpenAIClientBuilder":
        """
        Add an error response to the sequence.

        Args:
            error_type: Type of error ("rate_limit", "invalid_key", "timeout")

        Returns:
            Self for method chaining

        Note: When the error response is reached, it will raise an exception
        """
        self.responses.append(("ERROR", error_type))
        return self

    async def _get_next_response(self, *args, **kwargs):
        """
        Internal method to return next response in sequence.

        Returns:
            MockOpenAIResponse: Next response in the sequence

        Raises:
            Appropriate OpenAI error if an error response was configured
        """
        if self.call_count < len(self.responses):
            response_item = self.responses[self.call_count]
            self.call_count += 1

            # Check if this is an error response
            if isinstance(response_item, tuple) and response_item[0] == "ERROR":
                error_type = response_item[1]
                if error_type == "rate_limit":
                    from openai import RateLimitError
                    raise RateLimitError("Rate limit exceeded", response=MagicMock(status_code=429), body=None)
                elif error_type == "invalid_key":
                    from openai import AuthenticationError
                    raise AuthenticationError("Invalid API key", response=MagicMock(status_code=401), body=None)
                elif error_type == "timeout":
                    from openai import APITimeoutError
                    raise APITimeoutError(request=MagicMock())
                else:
                    from openai import APIError
                    raise APIError(f"Mock error: {error_type}", request=MagicMock(), body=None)

            return MockOpenAIResponse(response_item)
        else:
            # Default response if we run out
            return MockOpenAIResponse('{"result": "default response"}')

    def build(self) -> MagicMock:
        """
        Build the mock client.

        Returns:
            MagicMock: Configured mock OpenAI client
        """
        mock_create = AsyncMock(side_effect=self._get_next_response)

        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create

        return mock_client


# =============================================================================
# JSON FORMATTING UTILITIES
# =============================================================================


def mock_json_response(json_content: Dict[str, Any], format_type: str = "plain") -> str:
    """
    Create a mock response with JSON in various formats.

    Useful for testing JSON extraction from LLM responses that may
    include markdown formatting or additional text.

    Args:
        json_content: Dictionary to convert to JSON
        format_type: Response format:
            - "plain": Raw JSON only
            - "markdown": JSON wrapped in markdown code block
            - "mixed": JSON with surrounding explanatory text

    Returns:
        str: Formatted string containing JSON

    Usage:
        ```python
        from bigripple.testing.mocks import mock_json_response

        # Plain JSON
        response = mock_json_response({"status": "success"}, "plain")

        # Markdown-wrapped JSON
        response = mock_json_response({"status": "success"}, "markdown")

        # JSON with surrounding text
        response = mock_json_response({"status": "success"}, "mixed")
        ```
    """
    import json
    json_str = json.dumps(json_content, indent=2)

    if format_type == "plain":
        return json_str
    elif format_type == "markdown":
        return f"```json\n{json_str}\n```"
    elif format_type == "mixed":
        return f"Here's the result:\n\n```json\n{json_str}\n```\n\nThis provides the requested information."
    else:
        return json_str


# Export all mock utilities
__all__ = [
    "MockOpenAIResponse",
    "MockOpenAIClientBuilder",
    "create_mock_openai_client",
    "create_mock_openai_error",
    "mock_json_response",
]
