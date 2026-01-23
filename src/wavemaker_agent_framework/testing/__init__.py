"""Testing utilities for wavemaker agent framework."""

from wavemaker_agent_framework.testing.fixtures import (
    event_loop,
    fastapi_client,
    mock_aiohttp,
    mock_env_vars,
    mock_openai_client,
    mock_openai_response,
    sample_html_complex,
    sample_html_malformed,
    sample_html_minimal,
    sample_html_simple,
)

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
