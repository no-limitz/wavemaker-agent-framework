"""
Reusable pytest fixtures for wavemaker agents.

This module provides common test fixtures that can be imported by all agents,
eliminating the need to rewrite test infrastructure for each agent.

Usage in agent tests:
    # In your agent's conftest.py
    from bigripple.testing.fixtures import *

    # Add agent-specific fixtures
    @pytest.fixture
    def my_agent_data():
        return {"custom": "data"}
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient
from aioresponses import aioresponses


# =============================================================================
# EVENT LOOP FIXTURE
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.

    Required for pytest-asyncio to work properly with async tests.
    This fixture ensures all async tests share the same event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# HTTP MOCKING FIXTURES
# =============================================================================


@pytest.fixture
def mock_aiohttp():
    """
    Mock aiohttp responses for testing HTTP requests.

    This fixture uses aioresponses to mock HTTP calls made with aiohttp,
    preventing actual network requests during tests.

    Usage:
        ```python
        def test_http_request(mock_aiohttp):
            mock_aiohttp.get(
                "https://example.com",
                body="<html><title>Test</title></html>",
                status=200
            )

            # Your code that makes the HTTP request
            result = await fetch_url("https://example.com")
            assert "Test" in result
        ```
    """
    with aioresponses() as m:
        yield m


# =============================================================================
# OPENAI MOCKING FIXTURES
# =============================================================================


@pytest.fixture
def mock_openai_response():
    """
    Provide a mock OpenAI API response structure.

    Returns a dictionary that matches the OpenAI API response format,
    useful for creating mock responses in tests.

    Returns:
        dict: Mock OpenAI response with standard structure
    """
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"result": "test response"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def mock_openai_client(mocker, mock_openai_response):
    """
    Mock the OpenAI client to avoid real API calls during tests.

    This fixture patches the OpenAI AsyncOpenAI client to return mock responses,
    preventing actual API calls and associated costs during testing.

    Args:
        mocker: pytest-mock fixture for patching
        mock_openai_response: Mock response structure

    Returns:
        AsyncMock: Mocked create method that can be inspected/configured

    Usage:
        ```python
        async def test_llm_call(mock_openai_client):
            # Configure custom response if needed
            mock_openai_client.return_value.choices[0].message.content = '{"custom": "response"}'

            # Your code that uses OpenAI
            result = await my_llm_function()
            assert result == expected
        ```
    """
    # Create a mock response object
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = mock_openai_response["choices"][0]["message"]["content"]

    # Mock the OpenAI client's create method
    mock_create = AsyncMock(return_value=mock_response)

    # Patch the OpenAI client
    mocker.patch(
        "openai.AsyncOpenAI",
        return_value=MagicMock(
            chat=MagicMock(
                completions=MagicMock(create=mock_create)
            )
        )
    )

    return mock_create


# =============================================================================
# FASTAPI CLIENT FIXTURE
# =============================================================================


@pytest.fixture
async def fastapi_client(app_module: str = None) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for testing FastAPI endpoints.

    This fixture creates an AsyncClient configured to test your FastAPI app
    without starting an actual HTTP server.

    Note: This is a generic fixture. Agents should override it to import their specific app:

        ```python
        # In your agent's conftest.py
        import pytest
        from httpx import AsyncClient
        from bigripple.testing.fixtures import *

        @pytest.fixture
        async def fastapi_client():
            from my_agent.main import app
            async with AsyncClient(app=app, base_url="http://test") as client:
                yield client
        ```

    Usage:
        ```python
        async def test_endpoint(fastapi_client):
            response = await fastapi_client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        ```
    """
    # This is a placeholder - agents should override this fixture
    # with their specific app import
    raise NotImplementedError(
        "fastapi_client fixture must be overridden in your agent's conftest.py "
        "to import your specific FastAPI app. Example:\n\n"
        "@pytest.fixture\n"
        "async def fastapi_client():\n"
        "    from my_agent.main import app\n"
        "    async with AsyncClient(app=app, base_url='http://test') as client:\n"
        "        yield client"
    )


# =============================================================================
# ENVIRONMENT VARIABLE FIXTURES
# =============================================================================


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Mock environment variables for testing.

    Sets common environment variables to test values, preventing tests
    from using real credentials or affecting production systems.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Usage:
        ```python
        def test_config_loading(mock_env_vars):
            from bigripple.core import AgentConfig

            config = AgentConfig.from_env()
            assert config.openai_api_key == "sk-test-key-1234567890"
        ```

    Agents can extend this fixture with additional environment variables:
        ```python
        @pytest.fixture
        def mock_env_vars(monkeypatch):
            # Get base env vars from framework
            from bigripple.testing.fixtures import mock_env_vars as base_mock
            base_mock(monkeypatch)

            # Add agent-specific env vars
            monkeypatch.setenv("MY_AGENT_SETTING", "test-value")
        ```
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test-public-key")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test-secret-key")
    monkeypatch.setenv("LANGFUSE_HOST", "https://test.langfuse.com")
    monkeypatch.setenv("AGENTFIELD_CONTROL_PLANE_URL", "http://test-control-plane:8000")
    monkeypatch.setenv("PORT", "8001")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


# =============================================================================
# SAMPLE HTML FIXTURES
# =============================================================================


@pytest.fixture
def sample_html_simple():
    """
    Provide a simple HTML document for testing.

    Returns:
        str: Simple HTML with basic structure, title, and contact info
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Website</title>
        <meta name="description" content="A test website for unit tests">
    </head>
    <body>
        <h1>Welcome to Test Website</h1>
        <p>Contact us at test@example.com or call 555-1234</p>
        <a href="https://facebook.com/testpage">Facebook</a>
        <a href="https://twitter.com/testpage">Twitter</a>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_complex():
    """
    Provide a complex HTML document with multiple elements for testing.

    Returns:
        str: Complex HTML with meta tags, headers, sections, and social links
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Professional web design services">
        <meta name="keywords" content="web design, development, SEO">
        <meta property="og:title" content="Test Web Design Co">
        <meta property="og:description" content="Expert web solutions">
        <title>Test Web Design Company - Professional Services</title>
    </head>
    <body>
        <header>
            <h1>Test Web Design Company</h1>
            <nav>
                <a href="/services">Services</a>
                <a href="/portfolio">Portfolio</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>
        <main>
            <section>
                <h2>Our Services</h2>
                <p>We offer web design, development, and SEO services.</p>
            </section>
            <section>
                <h2>Contact Information</h2>
                <p>Email: contact@testwebdesign.com</p>
                <p>Phone: (555) 123-4567</p>
                <p>Alternative: +1-555-987-6543</p>
            </section>
            <footer>
                <a href="https://facebook.com/testwebdesign">Facebook</a>
                <a href="https://twitter.com/testwebdesign">Twitter</a>
                <a href="https://linkedin.com/company/testwebdesign">LinkedIn</a>
                <a href="https://instagram.com/testwebdesign">Instagram</a>
            </footer>
        </main>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_malformed():
    """
    Provide malformed HTML for testing error handling.

    Returns:
        str: Intentionally malformed HTML with missing closing tags
    """
    return """
    <html>
    <head><title>Broken HTML
    <body>
    <h1>Missing closing tags
    <p>This HTML is intentionally malformed
    <div>
    <span>Unclosed elements
    """


@pytest.fixture
def sample_html_minimal():
    """
    Provide minimal HTML with no meta tags for testing edge cases.

    Returns:
        str: Minimal HTML with just title and basic content
    """
    return """
    <html>
    <head><title>Minimal Page</title></head>
    <body><p>Just text</p></body>
    </html>
    """


# Export all fixtures for easy import
__all__ = [
    # Event loop
    "event_loop",
    # HTTP mocking
    "mock_aiohttp",
    # OpenAI mocking
    "mock_openai_response",
    "mock_openai_client",
    # FastAPI testing
    "fastapi_client",
    # Environment
    "mock_env_vars",
    # Sample HTML
    "sample_html_simple",
    "sample_html_complex",
    "sample_html_malformed",
    "sample_html_minimal",
]
