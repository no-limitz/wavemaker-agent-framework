"""
Wavemaker Agent Framework

A framework for building AgentField-compatible AI agents with reduced code duplication.
Provides core utilities, testing infrastructure, and templates for rapid agent development.

Enhanced with BigRipple integration:
- Context module for entity context handling (brands, campaigns, content)
- Tools module for tool registration and execution
- Operations module for entity operation schemas and extraction
- Agent runtime for complete execution with context injection
"""

__version__ = "0.1.0"

# Core utilities
from wavemaker_agent_framework.core import (
    AgentConfig,
    LLMClientFactory,
    AgentRuntime,
    AgentExecutionInput,
    AgentExecutionOutput,
    create_default_runtime,
)

# Context handling
from wavemaker_agent_framework.context import (
    EntityContext,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    BrandVoiceSettings,
    ContextInjector,
)

# Tools
from wavemaker_agent_framework.tools import (
    ToolRegistry,
    ToolExecutor,
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)

# Operations
from wavemaker_agent_framework.operations import (
    OperationExtractor,
    ResponseFormatter,
    EntityOperationType,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "AgentConfig",
    "LLMClientFactory",
    "AgentRuntime",
    "AgentExecutionInput",
    "AgentExecutionOutput",
    "create_default_runtime",
    # Context
    "EntityContext",
    "BrandSummary",
    "CampaignSummary",
    "ContentSummary",
    "BrandVoiceSettings",
    "ContextInjector",
    # Tools
    "ToolRegistry",
    "ToolExecutor",
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
    "ToolCategory",
    # Operations
    "OperationExtractor",
    "ResponseFormatter",
    "EntityOperationType",
]
