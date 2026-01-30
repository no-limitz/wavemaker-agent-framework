"""
Context module for BigRipple entity context handling.

Provides models and utilities for injecting entity context (brands, campaigns, content)
into agent prompts, matching BigRipple's EntityContext interface.
"""

from bigripple_agent_framework.context.entity_context import (
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    EntityContext,
)
from bigripple_agent_framework.context.context_injector import ContextInjector

# Alias for convenience
BrandVoice = BrandVoiceSettings

__all__ = [
    "BrandVoiceSettings",
    "BrandVoice",  # Alias for BrandVoiceSettings
    "BrandSummary",
    "CampaignSummary",
    "ContentSummary",
    "EntityContext",
    "ContextInjector",
]
