"""
BigRipple content tools.

Tools for creating and updating content pieces.
Matches BigRipple's CreateContentOperationSchema and UpdateContentOperationSchema.
"""

from bigripple_agent_framework.tools.registry import ToolRegistry
from bigripple_agent_framework.tools.definitions import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)


# Valid content types and statuses matching BigRipple schemas
CONTENT_TYPES = ["BLOG_POST", "SOCIAL_POST", "EMAIL", "AD_COPY", "LANDING_PAGE"]
CONTENT_STATUSES = ["DRAFT", "PENDING_REVIEW", "APPROVED", "SCHEDULED", "PUBLISHING", "PUBLISHED", "FAILED", "ARCHIVED"]
CHANNELS = ["facebook", "instagram", "linkedin", "twitter", "blog", "email"]


def register_content_tools(registry: ToolRegistry) -> None:
    """Register content tools with the registry."""

    # CREATE CONTENT
    registry.register(
        definition=ToolDefinition(
            id="bigripple.content.create",
            name="create_content",
            description=(
                "Create new content for a brand. "
                "This can be a blog post, social media post, email, ad copy, or landing page. "
                "Returns a content creation operation that will be processed by BigRipple."
            ),
            category=ToolCategory.ENTITY,
            parameters=[
                ToolParameter(
                    name="brand_id",
                    type="string",
                    description="The ID of the brand to create content for",
                    required=True,
                ),
                ToolParameter(
                    name="content_type",
                    type="string",
                    description="Type of content to create",
                    required=True,
                    enum=CONTENT_TYPES,
                ),
                ToolParameter(
                    name="channel",
                    type="string",
                    description="Distribution channel for the content",
                    required=True,
                ),
                ToolParameter(
                    name="body",
                    type="string",
                    description="The main content body (required, min 1 character)",
                    required=True,
                ),
                ToolParameter(
                    name="title",
                    type="string",
                    description="Content title (max 200 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="campaign_id",
                    type="string",
                    description="Optional campaign ID to link content to",
                    required=False,
                ),
                ToolParameter(
                    name="media_urls",
                    type="array",
                    description="Optional list of media URLs (images, videos)",
                    required=False,
                    items={"type": "string"},
                ),
                ToolParameter(
                    name="scheduled_at",
                    type="string",
                    description="When to publish (ISO datetime)",
                    required=False,
                ),
            ],
            returns_entity_operation=True,
        ),
        handler=_handle_create_content,
    )

    # UPDATE CONTENT
    registry.register(
        definition=ToolDefinition(
            id="bigripple.content.update",
            name="update_content",
            description=(
                "Update existing content. "
                "Only provide the fields you want to change. "
                "Returns an update operation that will be processed by BigRipple."
            ),
            category=ToolCategory.ENTITY,
            parameters=[
                ToolParameter(
                    name="content_id",
                    type="string",
                    description="The ID of the content to update",
                    required=True,
                ),
                ToolParameter(
                    name="content_type",
                    type="string",
                    description="New content type",
                    required=False,
                    enum=CONTENT_TYPES,
                ),
                ToolParameter(
                    name="channel",
                    type="string",
                    description="New distribution channel",
                    required=False,
                ),
                ToolParameter(
                    name="title",
                    type="string",
                    description="New title (max 200 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="body",
                    type="string",
                    description="New content body",
                    required=False,
                ),
                ToolParameter(
                    name="media_urls",
                    type="array",
                    description="New list of media URLs",
                    required=False,
                    items={"type": "string"},
                ),
                ToolParameter(
                    name="scheduled_at",
                    type="string",
                    description="New publish time (ISO datetime)",
                    required=False,
                ),
                ToolParameter(
                    name="status",
                    type="string",
                    description="New content status",
                    required=False,
                    enum=CONTENT_STATUSES,
                ),
            ],
            returns_entity_operation=True,
        ),
        handler=_handle_update_content,
    )


def _handle_create_content(
    brand_id: str,
    content_type: str,
    channel: str,
    body: str,
    title: str = None,
    campaign_id: str = None,
    media_urls: list = None,
    scheduled_at: str = None,
    execution_id: str = None,
    **context,
) -> ToolResult:
    """Handle create_content tool call."""

    # Validate content type
    if content_type not in CONTENT_TYPES:
        return ToolResult.fail(
            code="INVALID_CONTENT_TYPE",
            message=f"Invalid content type: {content_type}. Valid: {CONTENT_TYPES}",
        )

    # Validate body is not empty
    if not body or not body.strip():
        return ToolResult.fail(
            code="EMPTY_BODY",
            message="Content body cannot be empty",
        )

    # Build entity operation matching BigRipple's CreateContentOperationSchema
    entity_operation = {
        "type": "create_content",
        "brandId": brand_id,
        "data": {
            "type": content_type,
            "channel": channel,
            "body": body,
            "status": "DRAFT",
        },
        "metadata": {
            "aiGenerated": True,
            "sourceExecutionId": execution_id or "unknown",
        }
    }

    # Add optional fields
    if campaign_id:
        entity_operation["campaignId"] = campaign_id
    if title:
        entity_operation["data"]["title"] = title
    if media_urls:
        entity_operation["data"]["mediaUrls"] = media_urls
    if scheduled_at:
        entity_operation["data"]["scheduledAt"] = scheduled_at

    content_desc = title or body[:50] + "..." if len(body) > 50 else body
    return ToolResult.ok(
        data={
            "message": f"Content '{content_desc}' will be created",
            "operation_type": "create_content",
            "brand_id": brand_id,
            "content_type": content_type,
            "channel": channel,
        },
        entity_operation=entity_operation,
    )


def _handle_update_content(
    content_id: str,
    content_type: str = None,
    channel: str = None,
    title: str = None,
    body: str = None,
    media_urls: list = None,
    scheduled_at: str = None,
    status: str = None,
    **context,
) -> ToolResult:
    """Handle update_content tool call."""

    # Validate content type if provided
    if content_type and content_type not in CONTENT_TYPES:
        return ToolResult.fail(
            code="INVALID_CONTENT_TYPE",
            message=f"Invalid content type: {content_type}. Valid: {CONTENT_TYPES}",
        )

    # Validate status if provided
    if status and status not in CONTENT_STATUSES:
        return ToolResult.fail(
            code="INVALID_STATUS",
            message=f"Invalid status: {status}. Valid: {CONTENT_STATUSES}",
        )

    # Validate body if provided
    if body is not None and not body.strip():
        return ToolResult.fail(
            code="EMPTY_BODY",
            message="Content body cannot be empty",
        )

    # Build update data with only provided fields
    update_data = {}
    if content_type is not None:
        update_data["type"] = content_type
    if channel is not None:
        update_data["channel"] = channel
    if title is not None:
        update_data["title"] = title
    if body is not None:
        update_data["body"] = body
    if media_urls is not None:
        update_data["mediaUrls"] = media_urls
    if scheduled_at is not None:
        update_data["scheduledAt"] = scheduled_at
    if status is not None:
        update_data["status"] = status

    if not update_data:
        return ToolResult.fail(
            code="NO_UPDATES",
            message="No fields provided to update",
        )

    # Build entity operation matching BigRipple's UpdateContentOperationSchema
    entity_operation = {
        "type": "update_content",
        "contentId": content_id,
        "data": update_data,
    }

    return ToolResult.ok(
        data={
            "message": f"Content {content_id} will be updated",
            "operation_type": "update_content",
            "content_id": content_id,
            "updates": list(update_data.keys()),
        },
        entity_operation=entity_operation,
    )
