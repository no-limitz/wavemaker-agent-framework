"""
BigRipple tools using Strands @tool decorator.

These tools return entity operations that BigRipple processes to create/update entities.
Each tool returns a dict with the operation details.
"""

import re
from typing import Optional
from strands import tool


# Valid values matching BigRipple schemas
CHANNELS = ["facebook", "instagram", "linkedin", "twitter", "blog", "email"]
CAMPAIGN_STATUSES = ["DRAFT", "PENDING_APPROVAL", "APPROVED", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED"]
CONTENT_TYPES = ["BLOG_POST", "SOCIAL_POST", "EMAIL", "AD_COPY", "LANDING_PAGE"]
CONTENT_STATUSES = ["DRAFT", "PENDING_REVIEW", "APPROVED", "SCHEDULED", "PUBLISHING", "PUBLISHED", "FAILED", "ARCHIVED"]
BRAND_TONES = ["professional", "casual", "friendly", "authoritative", "playful"]


# =============================================================================
# CAMPAIGN TOOLS
# =============================================================================

@tool
def create_campaign(
    brand_id: str,
    name: str,
    channels: list[str],
    description: Optional[str] = None,
    goal: Optional[str] = None,
    target_audience: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Create a new marketing campaign for a brand.

    Use this when you need to create a new campaign with specific goals and channels.
    The campaign will be created in DRAFT status.

    Args:
        brand_id: The ID of the brand to create the campaign for.
        name: Campaign name (2-200 characters).
        channels: Marketing channels (facebook, instagram, linkedin, twitter, blog, email).
        description: Campaign description (max 1000 characters).
        goal: Campaign goal or objective (max 500 characters).
        target_audience: Target audience description (max 500 characters).
        start_date: Campaign start date (ISO datetime format).
        end_date: Campaign end date (ISO datetime format).

    Returns:
        Entity operation for BigRipple to process.
    """
    # Validate channels
    invalid_channels = [c for c in channels if c not in CHANNELS]
    if invalid_channels:
        return {"error": f"Invalid channels: {invalid_channels}. Valid: {CHANNELS}"}

    # Build entity operation
    operation = {
        "type": "create_campaign",
        "brandId": brand_id,
        "data": {
            "name": name,
            "channels": channels,
            "status": "DRAFT",
        },
        "metadata": {"aiGenerated": True},
    }

    if description:
        operation["data"]["description"] = description
    if goal:
        operation["data"]["goal"] = goal
    if target_audience:
        operation["data"]["targetAudience"] = target_audience
    if start_date:
        operation["data"]["startDate"] = start_date
    if end_date:
        operation["data"]["endDate"] = end_date

    return {"entityOperation": operation, "message": f"Campaign '{name}' will be created"}


@tool
def update_campaign(
    campaign_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    goal: Optional[str] = None,
    target_audience: Optional[str] = None,
    channels: Optional[list[str]] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Update an existing campaign.

    Only provide the fields you want to change.

    Args:
        campaign_id: The ID of the campaign to update.
        name: New campaign name.
        description: New description.
        goal: New goal.
        target_audience: New target audience.
        channels: New list of channels.
        status: New status (DRAFT, ACTIVE, PAUSED, COMPLETED, ARCHIVED).
        start_date: New start date.
        end_date: New end date.

    Returns:
        Entity operation for BigRipple to process.
    """
    if status and status not in CAMPAIGN_STATUSES:
        return {"error": f"Invalid status: {status}. Valid: {CAMPAIGN_STATUSES}"}

    if channels:
        invalid = [c for c in channels if c not in CHANNELS]
        if invalid:
            return {"error": f"Invalid channels: {invalid}. Valid: {CHANNELS}"}

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
        return {"error": "No fields provided to update"}

    operation = {
        "type": "update_campaign",
        "campaignId": campaign_id,
        "data": update_data,
    }

    return {"entityOperation": operation, "message": f"Campaign {campaign_id} will be updated"}


# =============================================================================
# CONTENT TOOLS
# =============================================================================

@tool
def create_content(
    brand_id: str,
    content_type: str,
    channel: str,
    body: str,
    title: Optional[str] = None,
    campaign_id: Optional[str] = None,
    media_urls: Optional[list[str]] = None,
    scheduled_at: Optional[str] = None,
) -> dict:
    """Create new content for a brand.

    This can be a blog post, social media post, email, ad copy, or landing page.
    The content will be created in DRAFT status.

    Args:
        brand_id: The ID of the brand to create content for.
        content_type: Type of content (BLOG_POST, SOCIAL_POST, EMAIL, AD_COPY, LANDING_PAGE).
        channel: Distribution channel (facebook, instagram, linkedin, twitter, blog, email).
        body: The main content body (required).
        title: Content title (max 200 characters).
        campaign_id: Optional campaign ID to link content to.
        media_urls: Optional list of media URLs (images, videos).
        scheduled_at: When to publish (ISO datetime).

    Returns:
        Entity operation for BigRipple to process.
    """
    if content_type not in CONTENT_TYPES:
        return {"error": f"Invalid content type: {content_type}. Valid: {CONTENT_TYPES}"}

    if not body or not body.strip():
        return {"error": "Content body cannot be empty"}

    operation = {
        "type": "create_content",
        "brandId": brand_id,
        "data": {
            "type": content_type,
            "channel": channel,
            "body": body,
            "status": "DRAFT",
        },
        "metadata": {"aiGenerated": True},
    }

    if campaign_id:
        operation["campaignId"] = campaign_id
    if title:
        operation["data"]["title"] = title
    if media_urls:
        operation["data"]["mediaUrls"] = media_urls
    if scheduled_at:
        operation["data"]["scheduledAt"] = scheduled_at

    content_desc = title or (body[:50] + "..." if len(body) > 50 else body)
    return {"entityOperation": operation, "message": f"Content '{content_desc}' will be created"}


@tool
def update_content(
    content_id: str,
    content_type: Optional[str] = None,
    channel: Optional[str] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
    media_urls: Optional[list[str]] = None,
    scheduled_at: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """Update existing content.

    Only provide the fields you want to change.

    Args:
        content_id: The ID of the content to update.
        content_type: New content type.
        channel: New distribution channel.
        title: New title.
        body: New content body.
        media_urls: New list of media URLs.
        scheduled_at: New publish time.
        status: New status.

    Returns:
        Entity operation for BigRipple to process.
    """
    if content_type and content_type not in CONTENT_TYPES:
        return {"error": f"Invalid content type: {content_type}. Valid: {CONTENT_TYPES}"}

    if status and status not in CONTENT_STATUSES:
        return {"error": f"Invalid status: {status}. Valid: {CONTENT_STATUSES}"}

    if body is not None and not body.strip():
        return {"error": "Content body cannot be empty"}

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
        return {"error": "No fields provided to update"}

    operation = {
        "type": "update_content",
        "contentId": content_id,
        "data": update_data,
    }

    return {"entityOperation": operation, "message": f"Content {content_id} will be updated"}


# =============================================================================
# BRAND TOOLS
# =============================================================================

@tool
def create_brand(
    customer_id: str,
    name: str,
    slug: str,
    description: Optional[str] = None,
    tone: Optional[str] = None,
    personality: Optional[list[str]] = None,
    target_audience: Optional[str] = None,
    brand_values: Optional[list[str]] = None,
    avoid_words: Optional[list[str]] = None,
    primary_color: Optional[str] = None,
    logo_url: Optional[str] = None,
) -> dict:
    """Create a new brand for a customer.

    A brand represents a business or product that will have campaigns and content.

    Args:
        customer_id: The ID of the customer to create the brand for.
        name: Brand name (2-100 characters).
        slug: URL-friendly identifier (lowercase letters, numbers, hyphens only).
        description: Brand description (max 500 characters).
        tone: Brand voice tone (professional, casual, friendly, authoritative, playful).
        personality: Brand personality traits (max 5).
        target_audience: Target audience description.
        brand_values: Core brand values.
        avoid_words: Words to avoid in content.
        primary_color: Primary brand color (hex format, e.g., #FF5733).
        logo_url: URL to brand logo.

    Returns:
        Entity operation for BigRipple to process.
    """
    if len(name) < 2 or len(name) > 100:
        return {"error": "Brand name must be 2-100 characters"}

    if not re.match(r'^[a-z0-9-]+$', slug):
        return {"error": "Slug must contain only lowercase letters, numbers, and hyphens"}

    if len(slug) < 2 or len(slug) > 50:
        return {"error": "Slug must be 2-50 characters"}

    if tone and tone not in BRAND_TONES:
        return {"error": f"Invalid tone: {tone}. Valid: {BRAND_TONES}"}

    if personality and len(personality) > 5:
        return {"error": "Maximum 5 personality traits allowed"}

    if primary_color and not re.match(r'^#[0-9A-Fa-f]{6}$', primary_color):
        return {"error": "Primary color must be hex format (e.g., #FF5733)"}

    operation = {
        "type": "create_brand",
        "customerId": customer_id,
        "data": {
            "name": name,
            "slug": slug,
        },
        "metadata": {"aiGenerated": True},
    }

    if description:
        operation["data"]["description"] = description

    # Build voice settings
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
        operation["data"]["voiceSettings"] = voice_settings

    if primary_color:
        operation["data"]["primaryColor"] = primary_color
    if logo_url:
        operation["data"]["logoUrl"] = logo_url

    return {"entityOperation": operation, "message": f"Brand '{name}' will be created"}


# =============================================================================
# KNOWLEDGE TOOLS
# =============================================================================

@tool
def search_knowledge_base(
    query: str,
    max_results: int = 5,
    filter_type: Optional[str] = None,
) -> dict:
    """Search the brand's knowledge base for relevant information.

    Use this to find past campaign performance, brand guidelines,
    successful content examples, or other relevant context.

    Args:
        query: The search query describing what information you need.
        max_results: Maximum number of results to return (default: 5).
        filter_type: Optional filter (campaign, content, brand_guidelines, performance_data).

    Returns:
        Search results or note about pre-loaded context.
    """
    return {
        "message": "Knowledge search requested",
        "query": query,
        "max_results": max_results,
        "filter_type": filter_type,
        "note": (
            "In production, this triggers a RAG query against the brand's knowledge base. "
            "Results are typically pre-loaded in the EntityContext.retrievalContext field."
        ),
    }


@tool
def get_brand_guidelines(brand_id: str) -> dict:
    """Get the brand's voice and style guidelines.

    Returns the brand's tone, personality, target audience, values, and words to avoid.

    Args:
        brand_id: The ID of the brand to get guidelines for.

    Returns:
        Brand guidelines or note about pre-loaded context.
    """
    return {
        "message": "Brand guidelines requested",
        "brand_id": brand_id,
        "note": (
            "Brand voice guidelines are typically pre-loaded in EntityContext.brandVoice. "
            "Check the context for tone, personality, target_audience, brand_values, and avoid_words."
        ),
    }


@tool
def get_campaign_performance(
    brand_id: str,
    limit: int = 10,
    status: Optional[str] = None,
) -> dict:
    """Get performance data for past campaigns.

    Returns metrics like impressions, engagement, and clicks.

    Args:
        brand_id: The ID of the brand to get campaign data for.
        limit: Maximum number of campaigns to return (default: 10).
        status: Filter by status (ACTIVE, COMPLETED, ALL).

    Returns:
        Campaign performance data or note about pre-loaded context.
    """
    return {
        "message": "Campaign performance data requested",
        "brand_id": brand_id,
        "limit": limit,
        "status_filter": status,
        "note": (
            "Campaign summaries are typically pre-loaded in EntityContext.campaigns. "
            "For detailed performance metrics, check the campaigns list in context."
        ),
    }


# =============================================================================
# TOOL COLLECTIONS
# =============================================================================

# All available BigRipple tools
ALL_TOOLS = [
    create_campaign,
    update_campaign,
    create_content,
    update_content,
    create_brand,
    search_knowledge_base,
    get_brand_guidelines,
    get_campaign_performance,
]

# Entity creation/update tools (produce entity operations)
ENTITY_TOOLS = [
    create_campaign,
    update_campaign,
    create_content,
    update_content,
    create_brand,
]

# Knowledge/utility tools (don't produce entity operations)
KNOWLEDGE_TOOLS = [
    search_knowledge_base,
    get_brand_guidelines,
    get_campaign_performance,
]
