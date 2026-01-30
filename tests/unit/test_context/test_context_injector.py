"""Tests for ContextInjector."""

import sys
import os

# Add src to path to import directly without triggering package __init__
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest

# Import directly from modules to avoid langfuse import in main __init__
from bigripple.context.entity_context import (
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    EntityContext,
)
from bigripple.context.context_injector import ContextInjector


class TestContextInjector:
    """Tests for ContextInjector."""

    @pytest.fixture
    def injector(self):
        """Create a context injector."""
        return ContextInjector()

    @pytest.fixture
    def full_context(self):
        """Create a full context with all fields."""
        return EntityContext(
            user_id="user_123",
            agency_id="agency_456",
            customer_id="customer_789",
            brand_id="brand_abc",
            brands=[
                BrandSummary(
                    id="brand_abc",
                    name="TechCorp",
                    slug="techcorp",
                    description="A technology company",
                    campaigns_count=5,
                    contents_count=42,
                ),
            ],
            campaigns=[
                CampaignSummary(
                    id="camp_1",
                    name="Q1 Product Launch",
                    status="ACTIVE",
                    goal="Increase awareness",
                    target_audience="CTOs",
                    channels=["linkedin", "twitter"],
                    contents_count=10,
                ),
            ],
            contents=[
                ContentSummary(
                    id="content_1",
                    type="SOCIAL_POST",
                    channel="linkedin",
                    title="Launch Announcement",
                    body="Excited to announce...",
                    status="PUBLISHED",
                    impressions=1000,
                    engagements=50,
                    clicks=25,
                ),
            ],
            brand_voice=BrandVoiceSettings(
                tone="professional",
                personality=["innovative", "trustworthy"],
                target_audience="Tech executives",
                brand_values=["innovation", "reliability"],
                avoid_words=["cheap", "basic"],
            ),
            retrieval_context="[Source 1: Past Campaign]\nOur Q4 campaign achieved 5x engagement...",
        )

    def test_build_context_prompt_minimal(self, injector):
        """Builds prompt with minimal context."""
        context = EntityContext(user_id="user_123")
        prompt = injector.build_context_prompt(context)

        assert "## Current Context" in prompt
        assert "User ID: user_123" in prompt

    def test_build_context_prompt_full(self, injector, full_context):
        """Builds prompt with full context."""
        prompt = injector.build_context_prompt(full_context)

        # Check all sections present
        assert "## Current Context" in prompt
        assert "## Available Brands" in prompt
        assert "## Brand Voice Guidelines" in prompt
        assert "## Active Campaigns" in prompt
        assert "## Recent Content" in prompt
        assert "## Knowledge Base Context" in prompt

        # Check specific content
        assert "TechCorp" in prompt
        assert "professional" in prompt
        assert "Q1 Product Launch" in prompt
        assert "Launch Announcement" in prompt
        assert "5x engagement" in prompt

    def test_build_context_prompt_exclude_sections(self, injector, full_context):
        """Can exclude specific sections."""
        prompt = injector.build_context_prompt(
            full_context,
            include_brands=False,
            include_campaigns=False,
            include_content=False,
        )

        assert "## Current Context" in prompt
        assert "## Available Brands" not in prompt
        assert "## Active Campaigns" not in prompt
        assert "## Recent Content" not in prompt
        # Still includes brand voice and RAG
        assert "## Brand Voice Guidelines" in prompt
        assert "## Knowledge Base Context" in prompt

    def test_build_minimal_context(self, injector, full_context):
        """Builds minimal context with just tenant info and voice."""
        prompt = injector.build_minimal_context(full_context)

        assert "## Current Context" in prompt
        assert "## Brand Voice Guidelines" in prompt
        assert "## Knowledge Base Context" in prompt
        # Should not include detailed entity lists
        assert "## Available Brands" not in prompt
        assert "## Active Campaigns" not in prompt

    def test_formats_brand_voice(self, injector):
        """Correctly formats brand voice."""
        context = EntityContext(
            user_id="user_123",
            brand_voice=BrandVoiceSettings(
                tone="friendly",
                personality=["approachable", "helpful"],
                avoid_words=["jargon", "buzzwords"],
            ),
        )
        prompt = injector.build_context_prompt(context)

        assert "**Tone**: friendly" in prompt
        assert "**Personality**: approachable, helpful" in prompt
        assert "**Avoid**: jargon, buzzwords" in prompt

    def test_truncates_long_descriptions(self, injector):
        """Truncates long descriptions."""
        long_desc = "A" * 300  # Longer than 200 char limit
        context = EntityContext(
            user_id="user_123",
            brands=[
                BrandSummary(
                    id="b1",
                    name="Test",
                    slug="test",
                    description=long_desc,
                ),
            ],
        )
        prompt = injector.build_context_prompt(context)

        # Should be truncated with ...
        assert "AAAAAAAAA..." in prompt
        # Should not contain full 300 chars
        assert "A" * 300 not in prompt

    def test_limits_items(self, injector):
        """Limits number of items shown."""
        # Create 15 brands
        brands = [
            BrandSummary(id=f"b{i}", name=f"Brand {i}", slug=f"brand-{i}")
            for i in range(15)
        ]
        context = EntityContext(user_id="user_123", brands=brands)
        prompt = injector.build_context_prompt(context)

        # Should only show first 10
        assert "Brand 9" in prompt
        assert "Brand 14" not in prompt  # Beyond limit
