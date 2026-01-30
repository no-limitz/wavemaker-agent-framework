"""
Entity context models matching BigRipple's EntityContext interface.

These Pydantic models mirror the TypeScript interfaces in:
apps/web/lib/entities/entity-context-service.ts
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class BrandVoiceSettings(BaseModel):
    """Brand voice configuration for content generation.

    Matches BigRipple's BrandVoiceSettings interface.
    """
    model_config = ConfigDict(populate_by_name=True)

    tone: Optional[str] = None
    personality: Optional[List[str]] = None
    vocabulary: Optional[List[str]] = None
    avoid_words: Optional[List[str]] = Field(None, alias="avoidWords")
    target_audience: Optional[str] = Field(None, alias="targetAudience")
    brand_values: Optional[List[str]] = Field(None, alias="brandValues")


class BrandSummary(BaseModel):
    """Summary of a brand for context injection.

    Matches BigRipple's BrandSummary interface.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    voice_settings: Optional[BrandVoiceSettings] = Field(None, alias="voiceSettings")
    primary_color: Optional[str] = Field(None, alias="primaryColor")
    campaigns_count: int = Field(0, alias="campaignsCount")
    contents_count: int = Field(0, alias="contentsCount")


class CampaignSummary(BaseModel):
    """Summary of a campaign for context injection.

    Matches BigRipple's CampaignSummary interface.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    status: str
    goal: Optional[str] = None
    target_audience: Optional[str] = Field(None, alias="targetAudience")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    channels: List[str] = []
    contents_count: int = Field(0, alias="contentsCount")


class ContentSummary(BaseModel):
    """Summary of content for context injection.

    Matches BigRipple's ContentSummary interface.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: str
    channel: str
    title: Optional[str] = None
    body: str
    status: str
    scheduled_at: Optional[datetime] = Field(None, alias="scheduledAt")
    published_at: Optional[datetime] = Field(None, alias="publishedAt")
    campaign_id: Optional[str] = Field(None, alias="campaignId")
    campaign_name: Optional[str] = Field(None, alias="campaignName")
    ai_generated: bool = Field(False, alias="aiGenerated")
    impressions: int = 0
    engagements: int = 0
    clicks: int = 0


class EntityContext(BaseModel):
    """Full entity context passed from BigRipple to agents.

    Matches BigRipple's EntityContext interface from:
    apps/web/lib/entities/entity-context-service.ts

    This context is sent by BigRipple when invoking an agent and contains:
    - Tenant scope (userId, agencyId, customerId, brandId)
    - Entity awareness (brands, campaigns, contents)
    - Knowledge context (knowledgeBases, brandVoice, retrievalContext)
    """
    model_config = ConfigDict(populate_by_name=True)

    # Tenant scope (from auth) - userId is required
    user_id: str = Field(..., alias="userId")
    agency_id: Optional[str] = Field(None, alias="agencyId")
    customer_id: Optional[str] = Field(None, alias="customerId")
    brand_id: Optional[str] = Field(None, alias="brandId")

    # Entity awareness
    brands: Optional[List[BrandSummary]] = None
    campaigns: Optional[List[CampaignSummary]] = None
    contents: Optional[List[ContentSummary]] = None

    # Knowledge context
    knowledge_bases: Optional[List[str]] = Field(None, alias="knowledgeBases")
    brand_voice: Optional[BrandVoiceSettings] = Field(None, alias="brandVoice")

    # RAG context (pre-retrieved by BigRipple)
    retrieval_context: Optional[str] = Field(None, alias="retrievalContext")

    def get_active_brand(self) -> Optional[BrandSummary]:
        """Get the active brand based on brand_id, if present in brands list."""
        if not self.brand_id or not self.brands:
            return None
        for brand in self.brands:
            if brand.id == self.brand_id:
                return brand
        return None

    def get_active_campaigns(self, status: Optional[str] = None) -> List[CampaignSummary]:
        """Get campaigns, optionally filtered by status."""
        if not self.campaigns:
            return []
        if status:
            return [c for c in self.campaigns if c.status == status]
        return self.campaigns

    def has_rag_context(self) -> bool:
        """Check if RAG retrieval context is available."""
        return bool(self.retrieval_context)
