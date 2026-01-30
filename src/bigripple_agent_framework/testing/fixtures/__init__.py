"""
Test fixtures for BigRipple integration testing.

Provides reusable fixtures for entity context, tool results, and agent responses.
"""

# Import base fixtures from base_fixtures.py
from bigripple_agent_framework.testing.base_fixtures import (
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

# Import BigRipple context fixtures
from bigripple_agent_framework.testing.fixtures.context_fixtures import (
    sample_brand_voice,
    sample_brand_summary,
    sample_campaign_summary,
    sample_content_summary,
    sample_entity_context,
    sample_entity_context_minimal,
    sample_entity_context_full,
    sample_rag_context,
)

__all__ = [
    # Base fixtures
    "event_loop",
    "fastapi_client",
    "mock_aiohttp",
    "mock_env_vars",
    "mock_openai_client",
    "mock_openai_response",
    "sample_html_complex",
    "sample_html_malformed",
    "sample_html_minimal",
    "sample_html_simple",
    # BigRipple context fixtures
    "sample_brand_voice",
    "sample_brand_summary",
    "sample_campaign_summary",
    "sample_content_summary",
    "sample_entity_context",
    "sample_entity_context_minimal",
    "sample_entity_context_full",
    "sample_rag_context",
]
