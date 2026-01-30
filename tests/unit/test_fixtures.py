"""
Unit tests for testing fixtures.

Tests that reusable pytest fixtures work correctly.
"""

import pytest
import asyncio
from unittest.mock import MagicMock
from aioresponses import aioresponses


class TestEventLoopFixture:
    """Test event_loop fixture."""

    def test_event_loop_exists(self, event_loop):
        """Test that event loop fixture provides a valid loop."""
        assert event_loop is not None
        assert isinstance(event_loop, asyncio.AbstractEventLoop)

    def test_event_loop_can_run_async_code(self, event_loop):
        """Test that event loop can execute async code."""
        async def sample_async_function():
            return "test_result"

        result = event_loop.run_until_complete(sample_async_function())
        assert result == "test_result"


class TestMockAiohttpFixture:
    """Test mock_aiohttp fixture."""

    def test_mock_aiohttp_exists(self, mock_aiohttp):
        """Test that mock_aiohttp fixture is provided."""
        assert mock_aiohttp is not None
        assert isinstance(mock_aiohttp, aioresponses)

    @pytest.mark.asyncio
    async def test_mock_aiohttp_can_mock_get_requests(self, mock_aiohttp):
        """Test that mock_aiohttp can mock HTTP GET requests."""
        import aiohttp

        mock_aiohttp.get(
            "https://example.com",
            body="<html><title>Test</title></html>",
            status=200
        )

        async with aiohttp.ClientSession() as session:
            async with session.get("https://example.com") as response:
                content = await response.text()

        assert response.status == 200
        assert "Test" in content

    @pytest.mark.asyncio
    async def test_mock_aiohttp_can_mock_post_requests(self, mock_aiohttp):
        """Test that mock_aiohttp can mock HTTP POST requests."""
        import aiohttp

        mock_aiohttp.post(
            "https://api.example.com/data",
            payload={"result": "success"},
            status=201
        )

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.example.com/data") as response:
                data = await response.json()

        assert response.status == 201
        assert data["result"] == "success"


class TestMockOpenAIResponseFixture:
    """Test mock_openai_response fixture."""

    def test_mock_openai_response_structure(self, mock_openai_response):
        """Test that mock_openai_response has correct structure."""
        assert "id" in mock_openai_response
        assert "object" in mock_openai_response
        assert "created" in mock_openai_response
        assert "model" in mock_openai_response
        assert "choices" in mock_openai_response
        assert "usage" in mock_openai_response

    def test_mock_openai_response_has_choices(self, mock_openai_response):
        """Test that mock_openai_response has choices array."""
        assert len(mock_openai_response["choices"]) > 0
        choice = mock_openai_response["choices"][0]

        assert "index" in choice
        assert "message" in choice
        assert "finish_reason" in choice

    def test_mock_openai_response_has_message(self, mock_openai_response):
        """Test that mock_openai_response has message with content."""
        message = mock_openai_response["choices"][0]["message"]

        assert "role" in message
        assert "content" in message
        assert message["role"] == "assistant"

    def test_mock_openai_response_has_usage(self, mock_openai_response):
        """Test that mock_openai_response has usage info."""
        usage = mock_openai_response["usage"]

        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage


class TestMockOpenAIClientFixture:
    """Test mock_openai_client fixture."""

    @pytest.mark.asyncio
    async def test_mock_openai_client_exists(self, mock_openai_client):
        """Test that mock_openai_client fixture is provided."""
        assert mock_openai_client is not None

    @pytest.mark.asyncio
    async def test_mock_openai_client_returns_mock_response(self, mock_openai_client, mock_openai_response):
        """Test that mocked OpenAI client returns expected response."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key="sk-test-key")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert response.choices[0].message.content == mock_openai_response["choices"][0]["message"]["content"]

    @pytest.mark.asyncio
    async def test_mock_openai_client_can_be_called_multiple_times(self, mock_openai_client):
        """Test that mocked client can be called multiple times."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key="sk-test-key")

        # First call
        response1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test1"}]
        )

        # Second call
        response2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test2"}]
        )

        # Both should return mocked responses
        assert response1.choices[0].message.content is not None
        assert response2.choices[0].message.content is not None


class TestMockEnvVarsFixture:
    """Test mock_env_vars fixture."""

    def test_mock_env_vars_sets_openai_key(self, mock_env_vars):
        """Test that mock_env_vars sets OPENAI_API_KEY."""
        import os

        assert os.getenv("OPENAI_API_KEY") == "sk-test-key-1234567890"

    def test_mock_env_vars_sets_langfuse_keys(self, mock_env_vars):
        """Test that mock_env_vars sets Langfuse keys."""
        import os

        assert os.getenv("LANGFUSE_PUBLIC_KEY") == "pk-test-public-key"
        assert os.getenv("LANGFUSE_SECRET_KEY") == "sk-test-secret-key"
        assert os.getenv("LANGFUSE_HOST") == "https://test.langfuse.com"

    def test_mock_env_vars_sets_agentfield_url(self, mock_env_vars):
        """Test that mock_env_vars sets AgentField URL."""
        import os

        assert os.getenv("AGENTFIELD_CONTROL_PLANE_URL") == "http://test-control-plane:8000"

    def test_mock_env_vars_sets_port(self, mock_env_vars):
        """Test that mock_env_vars sets PORT."""
        import os

        assert os.getenv("PORT") == "8001"

    def test_mock_env_vars_sets_environment(self, mock_env_vars):
        """Test that mock_env_vars sets ENVIRONMENT."""
        import os

        assert os.getenv("ENVIRONMENT") == "test"

    def test_mock_env_vars_sets_log_level(self, mock_env_vars):
        """Test that mock_env_vars sets LOG_LEVEL."""
        import os

        assert os.getenv("LOG_LEVEL") == "DEBUG"


class TestSampleHTMLFixtures:
    """Test sample HTML fixtures."""

    def test_sample_html_simple_exists(self, sample_html_simple):
        """Test that sample_html_simple provides HTML."""
        assert sample_html_simple is not None
        assert isinstance(sample_html_simple, str)
        assert "<html" in sample_html_simple

    def test_sample_html_simple_has_title(self, sample_html_simple):
        """Test that sample_html_simple has a title."""
        assert "<title>" in sample_html_simple
        assert "Test Website" in sample_html_simple

    def test_sample_html_simple_has_contact_info(self, sample_html_simple):
        """Test that sample_html_simple has contact info."""
        assert "test@example.com" in sample_html_simple
        assert "555-1234" in sample_html_simple

    def test_sample_html_complex_exists(self, sample_html_complex):
        """Test that sample_html_complex provides HTML."""
        assert sample_html_complex is not None
        assert isinstance(sample_html_complex, str)
        assert "<html" in sample_html_complex

    def test_sample_html_complex_has_meta_tags(self, sample_html_complex):
        """Test that sample_html_complex has meta tags."""
        assert '<meta name="description"' in sample_html_complex
        assert '<meta name="keywords"' in sample_html_complex
        assert '<meta property="og:title"' in sample_html_complex

    def test_sample_html_complex_has_structure(self, sample_html_complex):
        """Test that sample_html_complex has proper structure."""
        assert "<header>" in sample_html_complex
        assert "<main>" in sample_html_complex
        assert "<footer>" in sample_html_complex
        assert "<nav>" in sample_html_complex

    def test_sample_html_malformed_exists(self, sample_html_malformed):
        """Test that sample_html_malformed provides HTML."""
        assert sample_html_malformed is not None
        assert isinstance(sample_html_malformed, str)
        assert "<html>" in sample_html_malformed

    def test_sample_html_malformed_is_actually_malformed(self, sample_html_malformed):
        """Test that sample_html_malformed has missing closing tags."""
        # Should have opening tags but missing some closing tags
        assert "<title>Broken HTML" in sample_html_malformed
        assert "</title>" not in sample_html_malformed
        assert "<h1>Missing closing tags" in sample_html_malformed
        assert "</h1>" not in sample_html_malformed

    def test_sample_html_minimal_exists(self, sample_html_minimal):
        """Test that sample_html_minimal provides HTML."""
        assert sample_html_minimal is not None
        assert isinstance(sample_html_minimal, str)
        assert "<html>" in sample_html_minimal

    def test_sample_html_minimal_has_basic_structure(self, sample_html_minimal):
        """Test that sample_html_minimal has minimal structure."""
        assert "<title>Minimal Page</title>" in sample_html_minimal
        assert "<p>Just text</p>" in sample_html_minimal


class TestFastAPIClientFixture:
    """Test fastapi_client fixture."""

    def test_fastapi_client_is_exported(self):
        """Test that fastapi_client fixture is available for import."""
        from wavemaker_agent_framework.testing.fixtures import fastapi_client

        # Verify it's a fixture function (has pytest marker)
        assert hasattr(fastapi_client, "pytestmark") or callable(fastapi_client)

    def test_fastapi_client_docstring_has_usage_example(self):
        """Test that fastapi_client has proper documentation."""
        from wavemaker_agent_framework.testing.fixtures import fastapi_client

        # Verify the docstring explains how to override
        assert fastapi_client.__doc__ is not None
        assert "override" in fastapi_client.__doc__.lower() or "AsyncClient" in fastapi_client.__doc__


class TestFixtureIntegration:
    """Integration tests combining multiple fixtures."""

    @pytest.mark.asyncio
    async def test_can_use_multiple_fixtures_together(
        self,
        mock_env_vars,
        mock_openai_client,
        sample_html_simple
    ):
        """Test that multiple fixtures work together."""
        import os
        from wavemaker_agent_framework.core.config import AgentConfig

        # Environment variables are set
        assert os.getenv("OPENAI_API_KEY") is not None

        # Config can be loaded
        config = AgentConfig.from_env()
        assert config.openai_api_key == "sk-test-key-1234567890"

        # Sample HTML is available
        assert "Test Website" in sample_html_simple

        # OpenAI client is mocked
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=config.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )
        assert response.choices[0].message.content is not None
