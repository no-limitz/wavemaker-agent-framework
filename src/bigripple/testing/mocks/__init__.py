"""Mock utilities for wavemaker agent testing."""

from bigripple.testing.mocks.openai import (
    MockOpenAIClientBuilder,
    MockOpenAIResponse,
    create_mock_openai_client,
    create_mock_openai_error,
    mock_json_response,
)
from bigripple.testing.mocks.bigripple import (
    MockBigRippleClient,
    MockAgentFieldClient,
    create_mock_llm_client,
    create_mock_tool_call,
)

__all__ = [
    # OpenAI mocks
    "MockOpenAIResponse",
    "MockOpenAIClientBuilder",
    "create_mock_openai_client",
    "create_mock_openai_error",
    "mock_json_response",
    # BigRipple mocks
    "MockBigRippleClient",
    "MockAgentFieldClient",
    "create_mock_llm_client",
    "create_mock_tool_call",
]
