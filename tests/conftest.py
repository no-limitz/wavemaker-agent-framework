"""
Pytest configuration for wavemaker-agent-framework tests.

Imports all fixtures from the framework's testing module to make them
available to the test suite.
"""

# Import all fixtures from the framework
from wavemaker_agent_framework.testing.fixtures import (
    event_loop,
    mock_aiohttp,
    mock_openai_response,
    mock_openai_client,
    mock_env_vars,
    sample_html_simple,
    sample_html_complex,
    sample_html_malformed,
    sample_html_minimal,
)

# Make fixtures available to tests
__all__ = [
    "event_loop",
    "mock_aiohttp",
    "mock_openai_response",
    "mock_openai_client",
    "mock_env_vars",
    "sample_html_simple",
    "sample_html_complex",
    "sample_html_malformed",
    "sample_html_minimal",
]
