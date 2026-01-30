"""
BigRipple campaign tools.

Tools for creating and updating marketing campaigns.
Matches BigRipple's CreateCampaignOperationSchema and UpdateCampaignOperationSchema.
"""

from bigripple_agent_framework.tools.registry import ToolRegistry
from bigripple_agent_framework.tools.definitions import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)


# Valid channel and status values matching BigRipple schemas
CHANNELS = ["facebook", "instagram", "linkedin", "twitter", "blog", "email"]
CAMPAIGN_STATUSES = ["DRAFT", "PENDING_APPROVAL", "APPROVED", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED"]


def register_campaign_tools(registry: ToolRegistry) -> None:
    """Register campaign tools with the registry."""

    # CREATE CAMPAIGN
    registry.register(
        definition=ToolDefinition(
            id="bigripple.campaign.create",
            name="create_campaign",
            description=(
                "Create a new marketing campaign for a brand. "
                "Returns a campaign creation operation that will be processed by BigRipple. "
                "Use this when the user wants to create a new campaign with specific goals and channels."
            ),
            category=ToolCategory.ENTITY,
            parameters=[
                ToolParameter(
                    name="brand_id",
                    type="string",
                    description="The ID of the brand to create the campaign for",
                    required=True,
                ),
                ToolParameter(
                    name="name",
                    type="string",
                    description="Campaign name (2-200 characters)",
                    required=True,
                ),
                ToolParameter(
                    name="channels",
                    type="array",
                    description="Marketing channels for the campaign",
                    required=True,
                    items={"type": "string", "enum": CHANNELS},
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="Campaign description (max 1000 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="goal",
                    type="string",
                    description="Campaign goal or objective (max 500 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience description (max 500 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="start_date",
                    type="string",
                    description="Campaign start date (ISO datetime format)",
                    required=False,
                ),
                ToolParameter(
                    name="end_date",
                    type="string",
                    description="Campaign end date (ISO datetime format)",
                    required=False,
                ),
            ],
            returns_entity_operation=True,
        ),
        handler=_handle_create_campaign,
    )

    # UPDATE CAMPAIGN
    registry.register(
        definition=ToolDefinition(
            id="bigripple.campaign.update",
            name="update_campaign",
            description=(
                "Update an existing campaign. "
                "Only provide the fields you want to change. "
                "Returns an update operation that will be processed by BigRipple."
            ),
            category=ToolCategory.ENTITY,
            parameters=[
                ToolParameter(
                    name="campaign_id",
                    type="string",
                    description="The ID of the campaign to update",
                    required=True,
                ),
                ToolParameter(
                    name="name",
                    type="string",
                    description="New campaign name (2-200 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="New description (max 1000 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="goal",
                    type="string",
                    description="New goal (max 500 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="New target audience (max 500 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="channels",
                    type="array",
                    description="New list of channels",
                    required=False,
                    items={"type": "string", "enum": CHANNELS},
                ),
                ToolParameter(
                    name="status",
                    type="string",
                    description="New campaign status",
                    required=False,
                    enum=CAMPAIGN_STATUSES,
                ),
                ToolParameter(
                    name="start_date",
                    type="string",
                    description="New start date (ISO datetime)",
                    required=False,
                ),
                ToolParameter(
                    name="end_date",
                    type="string",
                    description="New end date (ISO datetime)",
                    required=False,
                ),
            ],
            returns_entity_operation=True,
        ),
        handler=_handle_update_campaign,
    )


def _handle_create_campaign(
    brand_id: str,
    name: str,
    channels: list,
    description: str = None,
    goal: str = None,
    target_audience: str = None,
    start_date: str = None,
    end_date: str = None,
    execution_id: str = None,
    **context,
) -> ToolResult:
    """Handle create_campaign tool call."""

    # Validate channels
    invalid_channels = [c for c in channels if c not in CHANNELS]
    if invalid_channels:
        return ToolResult.fail(
            code="INVALID_CHANNELS",
            message=f"Invalid channels: {invalid_channels}. Valid: {CHANNELS}",
        )

    # Build entity operation matching BigRipple's CreateCampaignOperationSchema
    entity_operation = {
        "type": "create_campaign",
        "brandId": brand_id,
        "data": {
            "name": name,
            "channels": channels,
            "status": "DRAFT",
        },
        "metadata": {
            "aiGenerated": True,
            "sourceExecutionId": execution_id or "unknown",
        }
    }

    # Add optional fields
    if description:
        entity_operation["data"]["description"] = description
    if goal:
        entity_operation["data"]["goal"] = goal
    if target_audience:
        entity_operation["data"]["targetAudience"] = target_audience
    if start_date:
        entity_operation["data"]["startDate"] = start_date
    if end_date:
        entity_operation["data"]["endDate"] = end_date

    return ToolResult.ok(
        data={
            "message": f"Campaign '{name}' will be created",
            "operation_type": "create_campaign",
            "brand_id": brand_id,
        },
        entity_operation=entity_operation,
    )


def _handle_update_campaign(
    campaign_id: str,
    name: str = None,
    description: str = None,
    goal: str = None,
    target_audience: str = None,
    channels: list = None,
    status: str = None,
    start_date: str = None,
    end_date: str = None,
    **context,
) -> ToolResult:
    """Handle update_campaign tool call."""

    # Validate status if provided
    if status and status not in CAMPAIGN_STATUSES:
        return ToolResult.fail(
            code="INVALID_STATUS",
            message=f"Invalid status: {status}. Valid: {CAMPAIGN_STATUSES}",
        )

    # Validate channels if provided
    if channels:
        invalid_channels = [c for c in channels if c not in CHANNELS]
        if invalid_channels:
            return ToolResult.fail(
                code="INVALID_CHANNELS",
                message=f"Invalid channels: {invalid_channels}. Valid: {CHANNELS}",
            )

    # Build update data with only provided fields
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if goal is not None:
        update_data["goal"] = goal
    if target_audience is not None:
        update_data["targetAudience"] = target_audience
    if channels is not None:
        update_data["channels"] = channels
    if status is not None:
        update_data["status"] = status
    if start_date is not None:
        update_data["startDate"] = start_date
    if end_date is not None:
        update_data["endDate"] = end_date

    if not update_data:
        return ToolResult.fail(
            code="NO_UPDATES",
            message="No fields provided to update",
        )

    # Build entity operation matching BigRipple's UpdateCampaignOperationSchema
    entity_operation = {
        "type": "update_campaign",
        "campaignId": campaign_id,
        "data": update_data,
    }

    return ToolResult.ok(
        data={
            "message": f"Campaign {campaign_id} will be updated",
            "operation_type": "update_campaign",
            "campaign_id": campaign_id,
            "updates": list(update_data.keys()),
        },
        entity_operation=entity_operation,
    )
