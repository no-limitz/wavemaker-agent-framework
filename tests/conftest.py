"""
Pytest configuration for wavemaker-agent-framework tests.

Imports all fixtures from the framework's testing module to make them
available to the test suite.
"""

# Import all fixtures from the framework
from wavemaker_agent_framework.testing import (
    # Base pytest fixtures
    event_loop,
    mock_aiohttp,
    mock_openai_response,
    mock_openai_client,
    mock_env_vars,
    sample_html_simple,
    sample_html_complex,
    sample_html_malformed,
    sample_html_minimal,
    # BigRipple context fixtures
    sample_brand_voice,
    sample_brand_summary,
    sample_campaign_summary,
    sample_content_summary,
    sample_entity_context,
    sample_entity_context_minimal,
    sample_entity_context_full,
    sample_rag_context,
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
    "sample_brand_voice",
    "sample_brand_summary",
    "sample_campaign_summary",
    "sample_content_summary",
    "sample_entity_context",
    "sample_entity_context_minimal",
    "sample_entity_context_full",
    "sample_rag_context",
]
