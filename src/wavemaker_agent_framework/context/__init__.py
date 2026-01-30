"""
Context module for BigRipple entity context handling.

Provides models and utilities for injecting entity context (brands, campaigns, content)
into agent prompts, matching BigRipple's EntityContext interface.
"""

from wavemaker_agent_framework.context.entity_context import (
    BrandVoiceSettings,
    BrandSummary,
    CampaignSummary,
    ContentSummary,
    EntityContext,
)
from wavemaker_agent_framework.context.context_injector import ContextInjector

__all__ = [
    "BrandVoiceSettings",
    "BrandSummary",
    "CampaignSummary",
    "ContentSummary",
    "EntityContext",
    "ContextInjector",
]
