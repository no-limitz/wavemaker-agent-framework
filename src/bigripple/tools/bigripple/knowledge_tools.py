"""
BigRipple knowledge/RAG tools.

Tools for searching and retrieving from knowledge bases.
These are utility tools that help agents access information
but don't create entity operations.
"""

from bigripple.tools.registry import ToolRegistry
from bigripple.tools.definitions import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)


def register_knowledge_tools(registry: ToolRegistry) -> None:
    """Register knowledge tools with the registry."""

    # SEARCH KNOWLEDGE BASE
    registry.register(
        definition=ToolDefinition(
            id="bigripple.knowledge.search",
            name="search_knowledge_base",
            description=(
                "Search the brand's knowledge base for relevant information. "
                "Use this to find past campaign performance, brand guidelines, "
                "successful content examples, or other relevant context. "
                "The search uses semantic similarity to find the most relevant results."
            ),
            category=ToolCategory.KNOWLEDGE,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="The search query describing what information you need",
                    required=True,
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results to return (default: 5)",
                    required=False,
                    default=5,
                ),
                ToolParameter(
                    name="filter_type",
                    type="string",
                    description="Optional filter by content type",
                    required=False,
                    enum=["campaign", "content", "brand_guidelines", "performance_data"],
                ),
            ],
            returns_entity_operation=False,
        ),
        handler=_handle_search_knowledge,
    )

    # GET BRAND GUIDELINES
    registry.register(
        definition=ToolDefinition(
            id="bigripple.knowledge.brand_guidelines",
            name="get_brand_guidelines",
            description=(
                "Get the brand's voice and style guidelines. "
                "Returns the brand's tone, personality, target audience, "
                "values, and any words to avoid in content."
            ),
            category=ToolCategory.KNOWLEDGE,
            parameters=[
                ToolParameter(
                    name="brand_id",
                    type="string",
                    description="The ID of the brand to get guidelines for",
                    required=True,
                ),
            ],
            returns_entity_operation=False,
        ),
        handler=_handle_get_brand_guidelines,
    )

    # GET CAMPAIGN PERFORMANCE
    registry.register(
        definition=ToolDefinition(
            id="bigripple.knowledge.campaign_performance",
            name="get_campaign_performance",
            description=(
                "Get performance data for past campaigns. "
                "Returns metrics like impressions, engagement, and clicks "
                "to help inform future campaign planning."
            ),
            category=ToolCategory.KNOWLEDGE,
            parameters=[
                ToolParameter(
                    name="brand_id",
                    type="string",
                    description="The ID of the brand to get campaign data for",
                    required=True,
                ),
                ToolParameter(
                    name="limit",
                    type="integer",
                    description="Maximum number of campaigns to return (default: 10)",
                    required=False,
                    default=10,
                ),
                ToolParameter(
                    name="status",
                    type="string",
                    description="Filter by campaign status",
                    required=False,
                    enum=["ACTIVE", "COMPLETED", "ALL"],
                ),
            ],
            returns_entity_operation=False,
        ),
        handler=_handle_get_campaign_performance,
    )


def _handle_search_knowledge(
    query: str,
    max_results: int = 5,
    filter_type: str = None,
    tenant_context: dict = None,
    **context,
) -> ToolResult:
    """Handle search_knowledge_base tool call.

    Note: This is a placeholder. In production, this would call BigRipple's
    knowledge service via the retrieval_context in EntityContext.
    The actual RAG retrieval is typically pre-performed by BigRipple
    and included in the EntityContext.
    """
    # In the agent framework, we rely on pre-retrieved context
    # This tool exists for cases where agents need additional searches
    return ToolResult.ok(
        data={
            "message": "Knowledge search requested",
            "query": query,
            "max_results": max_results,
            "filter_type": filter_type,
            "note": (
                "In production, this triggers a RAG query against the brand's knowledge base. "
                "Results are typically pre-loaded in the EntityContext.retrievalContext field. "
                "If you need additional context, check the retrieval_context first."
            ),
        }
    )


def _handle_get_brand_guidelines(
    brand_id: str,
    tenant_context: dict = None,
    **context,
) -> ToolResult:
    """Handle get_brand_guidelines tool call.

    Note: Brand guidelines are typically already included in EntityContext.brandVoice.
    This tool exists for explicit requests.
    """
    return ToolResult.ok(
        data={
            "message": "Brand guidelines requested",
            "brand_id": brand_id,
            "note": (
                "Brand voice guidelines are typically pre-loaded in EntityContext.brandVoice. "
                "Check the context for tone, personality, target_audience, brand_values, and avoid_words."
            ),
        }
    )


def _handle_get_campaign_performance(
    brand_id: str,
    limit: int = 10,
    status: str = None,
    tenant_context: dict = None,
    **context,
) -> ToolResult:
    """Handle get_campaign_performance tool call.

    Note: Campaign data is typically included in EntityContext.campaigns.
    This tool exists for explicit requests for performance metrics.
    """
    return ToolResult.ok(
        data={
            "message": "Campaign performance data requested",
            "brand_id": brand_id,
            "limit": limit,
            "status_filter": status,
            "note": (
                "Campaign summaries are typically pre-loaded in EntityContext.campaigns. "
                "For detailed performance metrics, check the campaigns list in context."
            ),
        }
    )
