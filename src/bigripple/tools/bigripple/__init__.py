"""
BigRipple-specific tools for entity operations.

Provides tools that agents can use to create and update BigRipple
entities (brands, campaigns, content) via structured operations.
"""

from bigripple.tools.registry import ToolRegistry
from bigripple.tools.bigripple.campaign_tools import register_campaign_tools
from bigripple.tools.bigripple.content_tools import register_content_tools
from bigripple.tools.bigripple.brand_tools import register_brand_tools
from bigripple.tools.bigripple.knowledge_tools import register_knowledge_tools


def register_all_bigripple_tools(registry: ToolRegistry) -> None:
    """Register all BigRipple tools with the given registry.

    Args:
        registry: The tool registry to register tools with.
    """
    register_campaign_tools(registry)
    register_content_tools(registry)
    register_brand_tools(registry)
    register_knowledge_tools(registry)


def create_bigripple_registry() -> ToolRegistry:
    """Create a new registry with all BigRipple tools pre-registered.

    Returns:
        A ToolRegistry with all BigRipple tools.
    """
    registry = ToolRegistry()
    register_all_bigripple_tools(registry)
    return registry


__all__ = [
    "register_all_bigripple_tools",
    "create_bigripple_registry",
    "register_campaign_tools",
    "register_content_tools",
    "register_brand_tools",
    "register_knowledge_tools",
]
