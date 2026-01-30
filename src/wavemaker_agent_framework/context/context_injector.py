"""
Context injector for building LLM prompts with entity context.

Formats EntityContext into structured text that can be injected into
system prompts for LLM calls.
"""

from typing import Optional, List
from wavemaker_agent_framework.context.entity_context import (
    EntityContext,
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
)


class ContextInjector:
    """Injects entity context into LLM prompts.

    Formats context for optimal LLM understanding while managing token usage.
    """

    def __init__(self, max_context_tokens: int = 4000):
        """Initialize the context injector.

        Args:
            max_context_tokens: Maximum tokens to use for context (approximate).
        """
        self.max_context_tokens = max_context_tokens

    def build_context_prompt(
        self,
        context: EntityContext,
        include_brands: bool = True,
        include_campaigns: bool = True,
        include_content: bool = True,
        include_brand_voice: bool = True,
        include_rag: bool = True,
    ) -> str:
        """Build a context string to inject into the system prompt.

        Args:
            context: The EntityContext from BigRipple.
            include_brands: Whether to include brand information.
            include_campaigns: Whether to include campaign information.
            include_content: Whether to include content information.
            include_brand_voice: Whether to include brand voice guidelines.
            include_rag: Whether to include RAG retrieval context.

        Returns:
            Formatted context string for prompt injection.
        """
        sections: List[str] = []

        # Tenant context (always included)
        sections.append(self._format_tenant_context(context))

        # Brand context
        if include_brands and context.brands:
            sections.append(self._format_brands(context.brands))

        # Brand voice guidelines
        if include_brand_voice and context.brand_voice:
            sections.append(self._format_brand_voice(context.brand_voice))

        # Campaign context
        if include_campaigns and context.campaigns:
            sections.append(self._format_campaigns(context.campaigns))

        # Content context
        if include_content and context.contents:
            sections.append(self._format_contents(context.contents))

        # RAG retrieval context
        if include_rag and context.retrieval_context:
            sections.append(self._format_rag_context(context.retrieval_context))

        return "\n\n".join(filter(None, sections))

    def _format_tenant_context(self, context: EntityContext) -> str:
        """Format tenant scope information."""
        lines = ["## Current Context"]
        lines.append(f"- User ID: {context.user_id}")
        if context.brand_id:
            lines.append(f"- Active Brand ID: {context.brand_id}")
        if context.customer_id:
            lines.append(f"- Customer ID: {context.customer_id}")
        if context.agency_id:
            lines.append(f"- Agency ID: {context.agency_id}")
        return "\n".join(lines)

    def _format_brands(self, brands: List[BrandSummary]) -> str:
        """Format brand information for context."""
        lines = ["## Available Brands"]
        for brand in brands[:10]:  # Limit to 10 brands
            lines.append(f"- **{brand.name}** (ID: {brand.id})")
            if brand.description:
                desc = brand.description[:200] + "..." if len(brand.description) > 200 else brand.description
                lines.append(f"  - Description: {desc}")
            lines.append(f"  - Campaigns: {brand.campaigns_count}, Content: {brand.contents_count}")
        return "\n".join(lines)

    def _format_brand_voice(self, voice: BrandVoiceSettings) -> str:
        """Format brand voice guidelines."""
        lines = ["## Brand Voice Guidelines"]
        if voice.tone:
            lines.append(f"- **Tone**: {voice.tone}")
        if voice.personality:
            lines.append(f"- **Personality**: {', '.join(voice.personality)}")
        if voice.target_audience:
            lines.append(f"- **Target Audience**: {voice.target_audience}")
        if voice.brand_values:
            lines.append(f"- **Brand Values**: {', '.join(voice.brand_values)}")
        if voice.vocabulary:
            lines.append(f"- **Vocabulary**: {', '.join(voice.vocabulary[:10])}")
        if voice.avoid_words:
            lines.append(f"- **Avoid**: {', '.join(voice.avoid_words)}")
        return "\n".join(lines)

    def _format_campaigns(self, campaigns: List[CampaignSummary]) -> str:
        """Format campaign information for context."""
        lines = ["## Active Campaigns"]
        for campaign in campaigns[:10]:  # Limit to 10 campaigns
            lines.append(f"- **{campaign.name}** (ID: {campaign.id}, Status: {campaign.status})")
            if campaign.goal:
                goal = campaign.goal[:150] + "..." if len(campaign.goal) > 150 else campaign.goal
                lines.append(f"  - Goal: {goal}")
            if campaign.target_audience:
                lines.append(f"  - Target Audience: {campaign.target_audience}")
            if campaign.channels:
                lines.append(f"  - Channels: {', '.join(campaign.channels)}")
            lines.append(f"  - Content Pieces: {campaign.contents_count}")
        return "\n".join(lines)

    def _format_contents(self, contents: List[ContentSummary]) -> str:
        """Format content information for context."""
        lines = ["## Recent Content"]
        for content in contents[:10]:  # Limit to 10 content items
            title = content.title or content.body[:50] + "..."
            lines.append(f"- **{title}** ({content.type}, {content.channel})")
            lines.append(f"  - Status: {content.status}")
            if content.engagements > 0 or content.impressions > 0:
                lines.append(f"  - Metrics: {content.impressions} impressions, {content.engagements} engagements, {content.clicks} clicks")
            if content.campaign_name:
                lines.append(f"  - Campaign: {content.campaign_name}")
        return "\n".join(lines)

    def _format_rag_context(self, retrieval_context: str) -> str:
        """Format RAG retrieval context."""
        return f"""## Knowledge Base Context
Use the following information from past campaigns and content to inform your response:

{retrieval_context}"""

    def build_minimal_context(self, context: EntityContext) -> str:
        """Build a minimal context with just tenant info and brand voice.

        Useful for token-constrained scenarios.
        """
        return self.build_context_prompt(
            context,
            include_brands=False,
            include_campaigns=False,
            include_content=False,
            include_brand_voice=True,
            include_rag=True,
        )
