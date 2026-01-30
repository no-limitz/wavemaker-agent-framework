"""Tests for EntityContext and related models."""

import sys
import os

# Add src to path to import directly without triggering package __init__
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest
from datetime import datetime

# Import directly from module to avoid langfuse import in main __init__
from bigripple_agent_framework.context.entity_context import (
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    EntityContext,
)


class TestBrandVoiceSettings:
    """Tests for BrandVoiceSettings model."""

    def test_create_empty(self):
        """Can create empty voice settings."""
        settings = BrandVoiceSettings()
        assert settings.tone is None
        assert settings.personality is None

    def test_create_full(self):
        """Can create full voice settings."""
        settings = BrandVoiceSettings(
            tone="professional",
            personality=["innovative", "trustworthy"],
            vocabulary=["tech", "enterprise"],
            avoid_words=["cheap", "basic"],
            target_audience="CTOs",
            brand_values=["innovation", "reliability"],
        )
        assert settings.tone == "professional"
        assert len(settings.personality) == 2
        assert "cheap" in settings.avoid_words

    def test_alias_parsing(self):
        """Parses camelCase field names from JSON."""
        settings = BrandVoiceSettings(**{
            "tone": "friendly",
            "avoidWords": ["boring"],
            "targetAudience": "Millennials",
            "brandValues": ["fun"],
        })
        assert settings.avoid_words == ["boring"]
        assert settings.target_audience == "Millennials"
        assert settings.brand_values == ["fun"]


class TestBrandSummary:
    """Tests for BrandSummary model."""

    def test_create_minimal(self):
        """Can create brand with required fields only."""
        brand = BrandSummary(
            id="brand_123",
            name="TechCorp",
            slug="techcorp",
        )
        assert brand.id == "brand_123"
        assert brand.campaigns_count == 0
        assert brand.contents_count == 0

    def test_create_full(self):
        """Can create brand with all fields."""
        brand = BrandSummary(
            id="brand_123",
            name="TechCorp",
            slug="techcorp",
            description="A tech company",
            voice_settings=BrandVoiceSettings(tone="professional"),
            primary_color="#FF5733",
            campaigns_count=5,
            contents_count=42,
        )
        assert brand.voice_settings.tone == "professional"
        assert brand.primary_color == "#FF5733"

    def test_alias_parsing(self):
        """Parses camelCase from JSON."""
        brand = BrandSummary(**{
            "id": "b1",
            "name": "Test",
            "slug": "test",
            "voiceSettings": {"tone": "casual"},
            "primaryColor": "#000000",
            "campaignsCount": 10,
            "contentsCount": 50,
        })
        assert brand.voice_settings.tone == "casual"
        assert brand.campaigns_count == 10


class TestCampaignSummary:
    """Tests for CampaignSummary model."""

    def test_create_minimal(self):
        """Can create campaign with required fields."""
        campaign = CampaignSummary(
            id="camp_123",
            name="Q1 Launch",
            status="ACTIVE",
        )
        assert campaign.id == "camp_123"
        assert campaign.channels == []

    def test_create_with_channels(self):
        """Can create campaign with channels."""
        campaign = CampaignSummary(
            id="camp_123",
            name="Social Push",
            status="DRAFT",
            channels=["facebook", "instagram", "linkedin"],
        )
        assert len(campaign.channels) == 3

    def test_alias_parsing(self):
        """Parses camelCase from JSON."""
        campaign = CampaignSummary(**{
            "id": "c1",
            "name": "Test",
            "status": "ACTIVE",
            "targetAudience": "Developers",
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2024-03-31T23:59:59Z",
            "contentsCount": 15,
        })
        assert campaign.target_audience == "Developers"
        assert campaign.contents_count == 15


class TestContentSummary:
    """Tests for ContentSummary model."""

    def test_create_minimal(self):
        """Can create content with required fields."""
        content = ContentSummary(
            id="content_123",
            type="SOCIAL_POST",
            channel="linkedin",
            body="Check out our new product!",
            status="DRAFT",
        )
        assert content.id == "content_123"
        assert content.ai_generated is False
        assert content.impressions == 0

    def test_alias_parsing(self):
        """Parses camelCase from JSON."""
        content = ContentSummary(**{
            "id": "c1",
            "type": "BLOG_POST",
            "channel": "blog",
            "body": "Article content...",
            "status": "PUBLISHED",
            "scheduledAt": "2024-01-15T10:00:00Z",
            "publishedAt": "2024-01-15T10:05:00Z",
            "campaignId": "camp_1",
            "campaignName": "Q1 Push",
            "aiGenerated": True,
        })
        assert content.campaign_id == "camp_1"
        assert content.ai_generated is True


class TestEntityContext:
    """Tests for EntityContext model."""

    def test_create_minimal(self):
        """Can create context with userId only."""
        context = EntityContext(user_id="user_123")
        assert context.user_id == "user_123"
        assert context.brand_id is None
        assert context.brands is None

    def test_create_from_json(self):
        """Can create context from camelCase JSON."""
        context = EntityContext(**{
            "userId": "user_123",
            "agencyId": "agency_456",
            "customerId": "customer_789",
            "brandId": "brand_abc",
            "brands": [
                {"id": "brand_abc", "name": "TechCorp", "slug": "techcorp"}
            ],
            "campaigns": [
                {"id": "camp_1", "name": "Q1", "status": "ACTIVE"}
            ],
            "brandVoice": {"tone": "professional"},
            "retrievalContext": "Some RAG context here...",
        })
        assert context.user_id == "user_123"
        assert context.brand_id == "brand_abc"
        assert len(context.brands) == 1
        assert context.brand_voice.tone == "professional"
        assert context.has_rag_context()

    def test_get_active_brand(self):
        """Can get active brand from context."""
        context = EntityContext(
            user_id="user_123",
            brand_id="brand_abc",
            brands=[
                BrandSummary(id="brand_abc", name="TechCorp", slug="techcorp"),
                BrandSummary(id="brand_xyz", name="OtherCorp", slug="othercorp"),
            ],
        )
        active = context.get_active_brand()
        assert active is not None
        assert active.name == "TechCorp"

    def test_get_active_campaigns_filter(self):
        """Can filter campaigns by status."""
        context = EntityContext(
            user_id="user_123",
            campaigns=[
                CampaignSummary(id="c1", name="Active", status="ACTIVE"),
                CampaignSummary(id="c2", name="Draft", status="DRAFT"),
                CampaignSummary(id="c3", name="Also Active", status="ACTIVE"),
            ],
        )
        active = context.get_active_campaigns(status="ACTIVE")
        assert len(active) == 2

    def test_has_rag_context(self):
        """Correctly reports RAG context availability."""
        context_without = EntityContext(user_id="user_123")
        assert not context_without.has_rag_context()

        context_with = EntityContext(
            user_id="user_123",
            retrieval_context="Some context",
        )
        assert context_with.has_rag_context()
