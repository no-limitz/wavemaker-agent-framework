"""
Tools module for BigRipple agents.

Provides tools that agents can use to create and update BigRipple entities.
Uses Strands SDK @tool decorator for simple tool definition.
"""

# New Strands-based tools (recommended)
from wavemaker_agent_framework.tools.strands_tools import (
    # Campaign tools
    create_campaign,
    update_campaign,
    # Content tools
    create_content,
    update_content,
    # Brand tools
    create_brand,
    # Knowledge tools
    search_knowledge_base,
    get_brand_guidelines,
    get_campaign_performance,
    # Tool collections
    ALL_TOOLS,
    ENTITY_TOOLS,
    KNOWLEDGE_TOOLS,
)

# Legacy tools (kept for backwards compatibility during transition)
# These will be deprecated in a future version
try:
    from wavemaker_agent_framework.tools.definitions import (
        ToolCategory,
        ToolParameter,
        ToolDefinition,
        ToolResult,
    )
    from wavemaker_agent_framework.tools.registry import ToolRegistry
    from wavemaker_agent_framework.tools.executor import ToolExecutor
    _LEGACY_AVAILABLE = True
except ImportError:
    _LEGACY_AVAILABLE = False

__all__ = [
    # Strands tools (primary API)
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
]

# Add legacy exports if available
if _LEGACY_AVAILABLE:
    __all__.extend([
        "ToolCategory",
        "ToolParameter",
        "ToolDefinition",
        "ToolResult",
        "ToolRegistry",
        "ToolExecutor",
    ])
