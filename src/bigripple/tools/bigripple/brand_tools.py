"""
BigRipple brand tools.

Tools for creating brands.
Matches BigRipple's CreateBrandOperationSchema.
"""

import re
from bigripple.tools.registry import ToolRegistry
from bigripple.tools.definitions import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)


# Valid tone values matching BigRipple schema
BRAND_TONES = ["professional", "casual", "friendly", "authoritative", "playful"]


def register_brand_tools(registry: ToolRegistry) -> None:
    """Register brand tools with the registry."""

    # CREATE BRAND
    registry.register(
        definition=ToolDefinition(
            id="bigripple.brand.create",
            name="create_brand",
            description=(
                "Create a new brand for a customer. "
                "A brand represents a business or product that will have campaigns and content. "
                "Returns a brand creation operation that will be processed by BigRipple."
            ),
            category=ToolCategory.ENTITY,
            parameters=[
                ToolParameter(
                    name="customer_id",
                    type="string",
                    description="The ID of the customer to create the brand for",
                    required=True,
                ),
                ToolParameter(
                    name="name",
                    type="string",
                    description="Brand name (2-100 characters)",
                    required=True,
                ),
                ToolParameter(
                    name="slug",
                    type="string",
                    description="URL-friendly identifier (2-50 chars, lowercase letters, numbers, hyphens only)",
                    required=True,
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="Brand description (max 500 characters)",
                    required=False,
                ),
                ToolParameter(
                    name="tone",
                    type="string",
                    description="Brand voice tone",
                    required=False,
                    enum=BRAND_TONES,
                ),
                ToolParameter(
                    name="personality",
                    type="array",
                    description="Brand personality traits (max 5)",
                    required=False,
                    items={"type": "string"},
                ),
                ToolParameter(
                    name="target_audience",
                    type="string",
                    description="Target audience description",
                    required=False,
                ),
                ToolParameter(
                    name="brand_values",
                    type="array",
                    description="Core brand values",
                    required=False,
                    items={"type": "string"},
                ),
                ToolParameter(
                    name="avoid_words",
                    type="array",
                    description="Words to avoid in content",
                    required=False,
                    items={"type": "string"},
                ),
                ToolParameter(
                    name="primary_color",
                    type="string",
                    description="Primary brand color (hex format, e.g., #FF5733)",
                    required=False,
                ),
                ToolParameter(
                    name="logo_url",
                    type="string",
                    description="URL to brand logo",
                    required=False,
                ),
            ],
            returns_entity_operation=True,
        ),
        handler=_handle_create_brand,
    )


def _handle_create_brand(
    customer_id: str,
    name: str,
    slug: str,
    description: str = None,
    tone: str = None,
    personality: list = None,
    target_audience: str = None,
    brand_values: list = None,
    avoid_words: list = None,
    primary_color: str = None,
    logo_url: str = None,
    execution_id: str = None,
    **context,
) -> ToolResult:
    """Handle create_brand tool call."""

    # Validate name length
    if len(name) < 2 or len(name) > 100:
        return ToolResult.fail(
            code="INVALID_NAME",
            message="Brand name must be 2-100 characters",
        )

    # Validate slug format
    if not re.match(r'^[a-z0-9-]+$', slug):
        return ToolResult.fail(
            code="INVALID_SLUG",
            message="Slug must contain only lowercase letters, numbers, and hyphens",
        )

    if len(slug) < 2 or len(slug) > 50:
        return ToolResult.fail(
            code="INVALID_SLUG",
            message="Slug must be 2-50 characters",
        )

    # Validate tone if provided
    if tone and tone not in BRAND_TONES:
        return ToolResult.fail(
            code="INVALID_TONE",
            message=f"Invalid tone: {tone}. Valid: {BRAND_TONES}",
        )

    # Validate personality length
    if personality and len(personality) > 5:
        return ToolResult.fail(
            code="TOO_MANY_PERSONALITY_TRAITS",
            message="Maximum 5 personality traits allowed",
        )

    # Validate primary color format if provided
    if primary_color and not re.match(r'^#[0-9A-Fa-f]{6}$', primary_color):
        return ToolResult.fail(
            code="INVALID_COLOR",
            message="Primary color must be hex format (e.g., #FF5733)",
        )

    # Build entity operation matching BigRipple's CreateBrandOperationSchema
    entity_operation = {
        "type": "create_brand",
        "customerId": customer_id,
        "data": {
            "name": name,
            "slug": slug,
        },
        "metadata": {
            "aiGenerated": True,
            "sourceExecutionId": execution_id or "unknown",
        }
    }

    # Add optional fields to data
    if description:
        entity_operation["data"]["description"] = description

    # Build voice settings if any voice-related fields provided
    voice_settings = {}
    if tone:
        voice_settings["tone"] = tone
    if personality:
        voice_settings["personality"] = personality
    if target_audience:
        voice_settings["targetAudience"] = target_audience
    if brand_values:
        voice_settings["brandValues"] = brand_values
    if avoid_words:
        voice_settings["avoidWords"] = avoid_words

    if voice_settings:
        entity_operation["data"]["voiceSettings"] = voice_settings

    if primary_color:
        entity_operation["data"]["primaryColor"] = primary_color
    if logo_url:
        entity_operation["data"]["logoUrl"] = logo_url

    return ToolResult.ok(
        data={
            "message": f"Brand '{name}' will be created",
            "operation_type": "create_brand",
            "customer_id": customer_id,
            "slug": slug,
        },
        entity_operation=entity_operation,
    )
