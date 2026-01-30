"""
Entity context fixtures for testing.

Provides sample EntityContext objects and related data for use in tests.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from bigripple.context.entity_context import (
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    EntityContext,
)


# ==========================================
# Sample Data Factories
# ==========================================

def sample_brand_voice(
    tone: str = "professional",
    personality: list = None,
    target_audience: str = "Tech professionals",
) -> BrandVoiceSettings:
    """Create a sample brand voice settings object.

    Args:
        tone: Voice tone.
        personality: List of personality traits.
        target_audience: Target audience description.

    Returns:
        BrandVoiceSettings instance.
    """
    return BrandVoiceSettings(
        tone=tone,
        personality=personality or ["innovative", "trustworthy", "knowledgeable"],
        vocabulary=["enterprise", "scalable", "innovative"],
        avoid_words=["cheap", "basic", "simple"],
        target_audience=target_audience,
        brand_values=["innovation", "reliability", "customer-focus"],
    )


def sample_brand_summary(
    brand_id: str = "brand_test123",
    name: str = "TechCorp",
    slug: str = "techcorp",
    with_voice: bool = True,
) -> BrandSummary:
    """Create a sample brand summary.

    Args:
        brand_id: Brand ID.
        name: Brand name.
        slug: Brand slug.
        with_voice: Whether to include voice settings.

    Returns:
        BrandSummary instance.
    """
    return BrandSummary(
        id=brand_id,
        name=name,
        slug=slug,
        description=f"{name} is a leading technology company specializing in enterprise solutions.",
        voice_settings=sample_brand_voice() if with_voice else None,
        primary_color="#2563EB",
        campaigns_count=5,
        contents_count=42,
    )


def sample_campaign_summary(
    campaign_id: str = "campaign_test123",
    name: str = "Q1 Product Launch",
    status: str = "ACTIVE",
    channels: list = None,
) -> CampaignSummary:
    """Create a sample campaign summary.

    Args:
        campaign_id: Campaign ID.
        name: Campaign name.
        status: Campaign status.
        channels: Marketing channels.

    Returns:
        CampaignSummary instance.
    """
    return CampaignSummary(
        id=campaign_id,
        name=name,
        description="Launch campaign for our new enterprise product line.",
        status=status,
        goal="Increase brand awareness and generate 500 qualified leads",
        target_audience="CTOs and IT decision makers at mid-size companies",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90),
        channels=channels or ["linkedin", "twitter", "email"],
        contents_count=12,
    )


def sample_content_summary(
    content_id: str = "content_test123",
    content_type: str = "SOCIAL_POST",
    channel: str = "linkedin",
    status: str = "PUBLISHED",
) -> ContentSummary:
    """Create a sample content summary.

    Args:
        content_id: Content ID.
        content_type: Type of content.
        channel: Distribution channel.
        status: Content status.

    Returns:
        ContentSummary instance.
    """
    return ContentSummary(
        id=content_id,
        type=content_type,
        channel=channel,
        title="Announcing Our Latest Innovation",
        body="We're excited to announce our new enterprise platform that helps companies scale their operations...",
        status=status,
        scheduled_at=datetime.utcnow() + timedelta(hours=2) if status == "SCHEDULED" else None,
        published_at=datetime.utcnow() - timedelta(hours=1) if status == "PUBLISHED" else None,
        campaign_id="campaign_test123",
        campaign_name="Q1 Product Launch",
        ai_generated=True,
        impressions=5420,
        engagements=324,
        clicks=89,
    )


def sample_rag_context() -> str:
    """Create sample RAG retrieval context.

    Returns:
        Sample retrieval context string.
    """
    return """[Source 1: Q4 2024 Campaign Analysis]
Our most successful LinkedIn posts achieved 5x average engagement when focusing on industry trends rather than direct product promotion. Key themes that resonated:
- Digital transformation challenges
- ROI of automation
- Customer success stories

[Source 2: Brand Voice Guidelines]
Maintain a professional yet approachable tone. Use data and statistics to support claims. Avoid jargon unless speaking to technical audiences.

[Source 3: Competitor Analysis]
Top competitors are focusing on thought leadership content. Opportunity to differentiate through customer-centric storytelling and practical how-to guides."""


def sample_entity_context(
    user_id: str = "user_test123",
    brand_id: str = "brand_test123",
    include_brands: bool = True,
    include_campaigns: bool = True,
    include_content: bool = True,
    include_rag: bool = True,
) -> EntityContext:
    """Create a sample entity context with configurable content.

    Args:
        user_id: User ID.
        brand_id: Brand ID.
        include_brands: Include brand summaries.
        include_campaigns: Include campaign summaries.
        include_content: Include content summaries.
        include_rag: Include RAG context.

    Returns:
        EntityContext instance.
    """
    return EntityContext(
        user_id=user_id,
        agency_id="agency_test123",
        customer_id="customer_test123",
        brand_id=brand_id,
        brands=[sample_brand_summary(brand_id)] if include_brands else None,
        campaigns=[
            sample_campaign_summary("campaign_1", "Q1 Product Launch", "ACTIVE"),
            sample_campaign_summary("campaign_2", "Brand Awareness", "DRAFT"),
        ] if include_campaigns else None,
        contents=[
            sample_content_summary("content_1", "SOCIAL_POST", "linkedin", "PUBLISHED"),
            sample_content_summary("content_2", "BLOG_POST", "blog", "DRAFT"),
            sample_content_summary("content_3", "EMAIL", "email", "SCHEDULED"),
        ] if include_content else None,
        knowledge_bases=["kb_brand_123", "kb_customer_123"],
        brand_voice=sample_brand_voice(),
        retrieval_context=sample_rag_context() if include_rag else None,
    )


def sample_entity_context_minimal(user_id: str = "user_test123") -> EntityContext:
    """Create a minimal entity context with only required fields.

    Args:
        user_id: User ID.

    Returns:
        Minimal EntityContext instance.
    """
    return EntityContext(user_id=user_id)


def sample_entity_context_full() -> EntityContext:
    """Create a fully populated entity context for comprehensive testing.

    Returns:
        Full EntityContext instance.
    """
    return sample_entity_context(
        include_brands=True,
        include_campaigns=True,
        include_content=True,
        include_rag=True,
    )


# ==========================================
# Pytest Fixtures
# ==========================================

@pytest.fixture
def brand_voice():
    """Pytest fixture for sample brand voice."""
    return sample_brand_voice()


@pytest.fixture
def brand_summary():
    """Pytest fixture for sample brand summary."""
    return sample_brand_summary()


@pytest.fixture
def campaign_summary():
    """Pytest fixture for sample campaign summary."""
    return sample_campaign_summary()


@pytest.fixture
def content_summary():
    """Pytest fixture for sample content summary."""
    return sample_content_summary()


@pytest.fixture
def entity_context():
    """Pytest fixture for sample entity context."""
    return sample_entity_context()


@pytest.fixture
def entity_context_minimal():
    """Pytest fixture for minimal entity context."""
    return sample_entity_context_minimal()


@pytest.fixture
def entity_context_full():
    """Pytest fixture for full entity context."""
    return sample_entity_context_full()


@pytest.fixture
def rag_context():
    """Pytest fixture for sample RAG context."""
    return sample_rag_context()


# ==========================================
# JSON Fixtures (for API testing)
# ==========================================

def sample_entity_context_json() -> Dict[str, Any]:
    """Create a sample entity context as JSON (camelCase keys).

    Returns:
        Entity context as dictionary with camelCase keys.
    """
    return {
        "userId": "user_test123",
        "agencyId": "agency_test123",
        "customerId": "customer_test123",
        "brandId": "brand_test123",
        "brands": [
            {
                "id": "brand_test123",
                "name": "TechCorp",
                "slug": "techcorp",
                "description": "A leading technology company",
                "voiceSettings": {
                    "tone": "professional",
                    "personality": ["innovative", "trustworthy"],
                    "targetAudience": "Tech professionals",
                    "brandValues": ["innovation", "reliability"],
                    "avoidWords": ["cheap", "basic"],
                },
                "primaryColor": "#2563EB",
                "campaignsCount": 5,
                "contentsCount": 42,
            }
        ],
        "campaigns": [
            {
                "id": "campaign_test123",
                "name": "Q1 Product Launch",
                "description": "Launch campaign for new product",
                "status": "ACTIVE",
                "goal": "Generate 500 leads",
                "targetAudience": "CTOs",
                "channels": ["linkedin", "twitter"],
                "contentsCount": 12,
            }
        ],
        "brandVoice": {
            "tone": "professional",
            "personality": ["innovative", "trustworthy"],
            "targetAudience": "Tech professionals",
        },
        "retrievalContext": sample_rag_context(),
    }


def sample_execution_request_json() -> Dict[str, Any]:
    """Create a sample execution request as BigRipple would send.

    Returns:
        Execution request dictionary.
    """
    return {
        "input": {
            "goal": "Create a social media campaign for product launch",
            "targetAudience": "Tech professionals 25-45",
            "channels": ["linkedin", "twitter"],
        },
        "context": sample_entity_context_json(),
        "executionId": "exec_test123",
    }
