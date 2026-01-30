"""
Unit tests for OpenAI mock utilities.

Tests MockOpenAIResponse, MockOpenAIClientBuilder, and helper functions.
"""

import pytest
import json
from unittest.mock import MagicMock
from openai import RateLimitError, AuthenticationError, APITimeoutError, APIError
from bigripple_agent_framework.testing.mocks.openai import (
    MockOpenAIResponse,
    MockOpenAIClientBuilder,
    create_mock_openai_client,
    create_mock_openai_error,
    mock_json_response,
)


class TestMockOpenAIResponse:
    """Test MockOpenAIResponse class."""

    def test_creates_basic_mock_response(self):
        """Test creating basic mock response."""
        response = MockOpenAIResponse(content='{"result": "test"}')

        assert response.id == "chatcmpl-mock-123"
        assert response.object == "chat.completion"
        assert response.model == "gpt-4o-mini"
        assert len(response.choices) == 1

    def test_mock_response_has_message(self):
        """Test that mock response has message with content."""
        content = '{"result": "test"}'
        response = MockOpenAIResponse(content=content)

        message = response.choices[0].message
        assert message.role == "assistant"
        assert message.content == content

    def test_mock_response_has_usage(self):
        """Test that mock response has usage information."""
        response = MockOpenAIResponse(content='{"result": "test"}')

        assert response.usage.prompt_tokens == 100
        assert response.usage.completion_tokens == 200
        assert response.usage.total_tokens == 300

    def test_mock_response_finish_reason(self):
        """Test that mock response has finish_reason."""
        response = MockOpenAIResponse(content='{"result": "test"}')

        assert response.choices[0].finish_reason == "stop"

    def test_mock_response_with_custom_model(self):
        """Test creating mock response with custom model."""
        response = MockOpenAIResponse(
            content='{"result": "test"}',
            model="gpt-4o"
        )

        assert response.model == "gpt-4o"

    def test_mock_response_with_json_content(self):
        """Test mock response with JSON content."""
        json_content = json.dumps({"key": "value", "items": [1, 2, 3]})
        response = MockOpenAIResponse(content=json_content)

        assert response.choices[0].message.content == json_content


class TestCreateMockOpenAIClient:
    """Test create_mock_openai_client() function."""

    @pytest.mark.asyncio
    async def test_creates_mock_client(self):
        """Test that create_mock_openai_client creates a working mock."""
        mock_client = create_mock_openai_client()

        response = await mock_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert response.choices[0].message.content == '{"result": "test response"}'

    @pytest.mark.asyncio
    async def test_creates_mock_client_with_custom_response(self):
        """Test creating mock client with custom response content."""
        custom_content = '{"custom": "data"}'
        mock_client = create_mock_openai_client(response_content=custom_content)

        response = await mock_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert response.choices[0].message.content == custom_content

    @pytest.mark.asyncio
    async def test_mock_client_can_be_called_multiple_times(self):
        """Test that mock client returns same response on multiple calls."""
        mock_client = create_mock_openai_client()

        response1 = await mock_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )

        response2 = await mock_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test2"}]
        )

        # Both should return the same mocked content
        assert response1.choices[0].message.content == response2.choices[0].message.content


class TestCreateMockOpenAIError:
    """Test create_mock_openai_error() function."""

    @pytest.mark.asyncio
    async def test_creates_rate_limit_error(self):
        """Test creating mock client that raises RateLimitError."""
        mock_client = create_mock_openai_error(error_type="rate_limit")

        with pytest.raises(RateLimitError):
            await mock_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}]
            )

    @pytest.mark.asyncio
    async def test_creates_authentication_error(self):
        """Test creating mock client that raises AuthenticationError."""
        mock_client = create_mock_openai_error(error_type="invalid_key")

        with pytest.raises(AuthenticationError):
            await mock_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}]
            )

    @pytest.mark.asyncio
    async def test_creates_timeout_error(self):
        """Test creating mock client that raises APITimeoutError."""
        mock_client = create_mock_openai_error(error_type="timeout")

        with pytest.raises(APITimeoutError):
            await mock_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}]
            )

    @pytest.mark.asyncio
    async def test_creates_generic_api_error(self):
        """Test creating mock client that raises generic APIError."""
        mock_client = create_mock_openai_error(error_type="unknown")

        with pytest.raises(APIError) as exc_info:
            await mock_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}]
            )

        assert "unknown" in str(exc_info.value)


class TestMockOpenAIClientBuilder:
    """Test MockOpenAIClientBuilder class."""

    @pytest.mark.asyncio
    async def test_builder_with_single_response(self):
        """Test builder with single response."""
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .build())

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert response.choices[0].message.content == '{"step": 1}'

    @pytest.mark.asyncio
    async def test_builder_with_multiple_responses(self):
        """Test builder with multiple sequential responses."""
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .with_response('{"step": 2}')
                  .with_response('{"step": 3}')
                  .build())

        # First call
        response1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )
        assert response1.choices[0].message.content == '{"step": 1}'

        # Second call
        response2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test2"}]
        )
        assert response2.choices[0].message.content == '{"step": 2}'

        # Third call
        response3 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test3"}]
        )
        assert response3.choices[0].message.content == '{"step": 3}'

    @pytest.mark.asyncio
    async def test_builder_with_json_response(self):
        """Test builder with JSON response method."""
        client = (MockOpenAIClientBuilder()
                  .with_json_response({"key": "value", "count": 42})
                  .build())

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        content = json.loads(response.choices[0].message.content)
        assert content["key"] == "value"
        assert content["count"] == 42

    @pytest.mark.asyncio
    async def test_builder_with_error_response(self):
        """Test builder with error in sequence."""
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .with_error("rate_limit")
                  .build())

        # First call succeeds
        response1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )
        assert response1.choices[0].message.content == '{"step": 1}'

        # Second call raises error
        with pytest.raises(RateLimitError):
            await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test2"}]
            )

    @pytest.mark.asyncio
    async def test_builder_mixed_responses_and_errors(self):
        """Test builder with mix of responses and errors."""
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .with_error("rate_limit")
                  .with_response('{"step": 2}')
                  .build())

        # First call succeeds
        response1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )
        assert response1.choices[0].message.content == '{"step": 1}'

        # Second call fails
        with pytest.raises(RateLimitError):
            await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test2"}]
            )

        # Third call succeeds
        response3 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test3"}]
        )
        assert response3.choices[0].message.content == '{"step": 2}'

    @pytest.mark.asyncio
    async def test_builder_returns_default_when_exhausted(self):
        """Test that builder returns default response when sequence exhausted."""
        client = (MockOpenAIClientBuilder()
                  .with_response('{"step": 1}')
                  .build())

        # First call gets configured response
        response1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )
        assert response1.choices[0].message.content == '{"step": 1}'

        # Second call gets default response
        response2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test2"}]
        )
        assert response2.choices[0].message.content == '{"result": "default response"}'


class TestMockJsonResponse:
    """Test mock_json_response() helper function."""

    def test_plain_json_format(self):
        """Test plain JSON format."""
        data = {"key": "value", "count": 42}
        result = mock_json_response(data, format_type="plain")

        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["count"] == 42

    def test_markdown_json_format(self):
        """Test markdown-wrapped JSON format."""
        data = {"key": "value"}
        result = mock_json_response(data, format_type="markdown")

        assert result.startswith("```json")
        assert result.endswith("```")
        assert '"key": "value"' in result or '"key":"value"' in result

    def test_mixed_json_format(self):
        """Test JSON with surrounding text."""
        data = {"key": "value"}
        result = mock_json_response(data, format_type="mixed")

        assert "Here's the result:" in result
        assert "```json" in result
        assert "```" in result
        assert "This provides the requested information" in result

    def test_default_format_is_plain(self):
        """Test that default format is plain JSON."""
        data = {"key": "value"}
        result = mock_json_response(data)

        # Should be parseable JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_json_response_with_complex_data(self):
        """Test JSON response with complex nested data."""
        data = {
            "level1": {
                "level2": {
                    "items": ["a", "b", "c"],
                    "count": 3
                }
            }
        }

        result = mock_json_response(data, format_type="plain")
        parsed = json.loads(result)

        assert parsed["level1"]["level2"]["items"] == ["a", "b", "c"]
        assert parsed["level1"]["level2"]["count"] == 3

    def test_json_response_preserves_formatting(self):
        """Test that JSON response is formatted with indentation."""
        data = {"key1": "value1", "key2": "value2"}
        result = mock_json_response(data, format_type="plain")

        # Should have newlines (indented JSON)
        assert "\n" in result


class TestMockUtilitiesIntegration:
    """Integration tests combining multiple mock utilities."""

    @pytest.mark.asyncio
    async def test_can_combine_mock_response_and_builder(self):
        """Test using both MockOpenAIResponse and Builder."""
        # Create a response directly
        direct_response = MockOpenAIResponse(content='{"direct": true}')
        assert direct_response.choices[0].message.content == '{"direct": true}'

        # Create a builder-based client
        client = (MockOpenAIClientBuilder()
                  .with_response('{"builder": true}')
                  .build())

        builder_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert builder_response.choices[0].message.content == '{"builder": true}'

    @pytest.mark.asyncio
    async def test_mock_json_response_with_builder(self):
        """Test using mock_json_response with MockOpenAIClientBuilder."""
        json_content = mock_json_response({"status": "success"}, format_type="markdown")

        client = (MockOpenAIClientBuilder()
                  .with_response(json_content)
                  .build())

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert "```json" in response.choices[0].message.content
        assert "success" in response.choices[0].message.content
