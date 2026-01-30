"""
Wavemaker Agent Framework

A framework for building BigRipple-compatible AI agents using Strands SDK.
Provides context injection, entity operations, and simplified agent creation.

Quick Start:
    ```python
    from bigripple_agent_framework import BigRippleAgent, EntityContext

    agent = BigRippleAgent(
        system_prompt="You are a campaign planning assistant.",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    result = agent.run(
        prompt="Create a Q1 marketing campaign for brand awareness",
        context=EntityContext(
            userId="user_123",
            brandId="brand_456",
            brands=[...],
        ),
    )

    print(result.entity_operations)  # Operations for BigRipple to process
    ```
"""

__version__ = "0.2.0"

# Primary API: Strands-based agent
from bigripple_agent_framework.strands import (
    BigRippleAgent,
    create_agent,
    AgentResult,
)

# Context handling
from bigripple_agent_framework.context import (
    EntityContext,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    BrandVoiceSettings,
    BrandVoice,
    ContextInjector,
)

# Tools (Strands @tool decorated functions)
from bigripple_agent_framework.tools import (
    create_campaign,
    update_campaign,
    create_content,
    update_content,
    create_brand,
    search_knowledge_base,
    get_brand_guidelines,
    get_campaign_performance,
    ALL_TOOLS,
    ENTITY_TOOLS,
    KNOWLEDGE_TOOLS,
)

# Operations
from bigripple_agent_framework.operations import (
    OperationExtractor,
    ResponseFormatter,
    EntityOperationType,
)

# Configuration (still useful for environment setup)
from bigripple_agent_framework.core.config import AgentConfig

__all__ = [
    # Version
    "__version__",
    # Primary API
    "BigRippleAgent",
    "create_agent",
    "AgentResult",
    # Context
    "EntityContext",
    "BrandSummary",
    "CampaignSummary",
    "ContentSummary",
    "BrandVoiceSettings",
    "BrandVoice",
    "ContextInjector",
    # Tools
    "create_campaign",
    "update_campaign",
    "create_content",
    "update_content",
    "create_brand",
    "search_knowledge_base",
    "get_brand_guidelines",
    "get_campaign_performance",
    "ALL_TOOLS",
    "ENTITY_TOOLS",
    "KNOWLEDGE_TOOLS",
    # Operations
    "OperationExtractor",
    "ResponseFormatter",
    "EntityOperationType",
    # Configuration
    "AgentConfig",
]


# Legacy exports (deprecated, will be removed in 0.3.0)
# Kept for backwards compatibility during transition
def __getattr__(name):
    """Lazy import for deprecated legacy exports."""
    deprecated = {
        "AgentRuntime": "bigripple.core.agent_runtime",
        "AgentExecutionInput": "bigripple.core.agent_runtime",
        "AgentExecutionOutput": "bigripple.core.agent_runtime",
        "create_default_runtime": "bigripple.core.agent_runtime",
        "LLMClientFactory": "bigripple.core.client",
        "ToolRegistry": "bigripple.tools.registry",
        "ToolExecutor": "bigripple.tools.executor",
        "ToolDefinition": "bigripple.tools.definitions",
        "ToolParameter": "bigripple.tools.definitions",
        "ToolResult": "bigripple.tools.definitions",
        "ToolCategory": "bigripple.tools.definitions",
    }

    if name in deprecated:
        import warnings
        import importlib

        module_path = deprecated[name]
        warnings.warn(
            f"{name} is deprecated and will be removed in version 0.3.0. "
            f"Use BigRippleAgent with Strands SDK instead.",
            DeprecationWarning,
            stacklevel=2
        )

        module = importlib.import_module(module_path)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
