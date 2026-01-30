"""
Entity operation schemas matching BigRipple's Zod schemas.

These Pydantic models mirror the schemas defined in:
apps/web/lib/entities/entity-operations.ts

The schemas ensure that operations returned by agents are valid
and can be processed by BigRipple's EntityOperationProcessor.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class EntityOperationType(str, Enum):
    """Types of entity operations that can be performed."""
    CREATE_BRAND = "create_brand"
    CREATE_CAMPAIGN = "create_campaign"
    CREATE_CONTENT = "create_content"
    UPDATE_CAMPAIGN = "update_campaign"
    UPDATE_CONTENT = "update_content"


class OperationMetadata(BaseModel):
    """Metadata for AI-generated operations."""
    model_config = ConfigDict(populate_by_name=True)

    ai_generated: Literal[True] = Field(True, alias="aiGenerated")
    ai_prompt: Optional[str] = Field(None, alias="aiPrompt")
    ai_model: Optional[str] = Field(None, alias="aiModel")
    source_execution_id: str = Field(..., alias="sourceExecutionId")


# ==========================================
# Brand Operations
# ==========================================

class BrandVoiceSettingsData(BaseModel):
    """Brand voice settings for create_brand operation."""
    model_config = ConfigDict(populate_by_name=True)

    tone: Optional[str] = None
    personality: Optional[List[str]] = None
    vocabulary: Optional[List[str]] = None
    avoid_words: Optional[List[str]] = Field(None, alias="avoidWords")
    target_audience: Optional[str] = Field(None, alias="targetAudience")
    brand_values: Optional[List[str]] = Field(None, alias="brandValues")


class CreateBrandData(BaseModel):
    """Data for create_brand operation."""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    voice_settings: Optional[BrandVoiceSettingsData] = Field(None, alias="voiceSettings")
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    primary_color: Optional[str] = Field(None, alias="primaryColor")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v

    @field_validator("primary_color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Primary color must be hex format (e.g., #FF5733)")
        return v


class CreateBrandOperation(BaseModel):
    """Schema for create_brand operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["create_brand"]
    customer_id: str = Field(..., alias="customerId")
    data: CreateBrandData
    save_as_artifact: Optional[bool] = Field(None, alias="saveAsArtifact")
    metadata: Optional[OperationMetadata] = None


# ==========================================
# Campaign Operations
# ==========================================

class CampaignChannel(str, Enum):
    """Valid campaign channels."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    BLOG = "blog"
    EMAIL = "email"


class CampaignStatus(str, Enum):
    """Valid campaign statuses."""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class CreateCampaignData(BaseModel):
    """Data for create_campaign operation."""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    goal: Optional[str] = Field(None, max_length=500)
    target_audience: Optional[str] = Field(None, max_length=500, alias="targetAudience")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    channels: List[str]
    status: Optional[str] = "DRAFT"


class CreateCampaignOperation(BaseModel):
    """Schema for create_campaign operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["create_campaign"]
    brand_id: str = Field(..., alias="brandId")
    data: CreateCampaignData
    save_as_artifact: Optional[bool] = Field(None, alias="saveAsArtifact")
    metadata: Optional[OperationMetadata] = None


class UpdateCampaignData(BaseModel):
    """Data for update_campaign operation (all fields optional)."""
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    goal: Optional[str] = Field(None, max_length=500)
    target_audience: Optional[str] = Field(None, max_length=500, alias="targetAudience")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    channels: Optional[List[str]] = None
    status: Optional[str] = None


class UpdateCampaignOperation(BaseModel):
    """Schema for update_campaign operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["update_campaign"]
    campaign_id: str = Field(..., alias="campaignId")
    data: UpdateCampaignData


# ==========================================
# Content Operations
# ==========================================

class ContentType(str, Enum):
    """Valid content types."""
    BLOG_POST = "BLOG_POST"
    SOCIAL_POST = "SOCIAL_POST"
    EMAIL = "EMAIL"
    AD_COPY = "AD_COPY"
    LANDING_PAGE = "LANDING_PAGE"


class ContentStatus(str, Enum):
    """Valid content statuses."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class CreateContentData(BaseModel):
    """Data for create_content operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: str  # ContentType
    channel: str
    title: Optional[str] = Field(None, max_length=200)
    body: str = Field(..., min_length=1)
    media_urls: Optional[List[str]] = Field(None, alias="mediaUrls")
    scheduled_at: Optional[str] = Field(None, alias="scheduledAt")
    status: Optional[str] = "DRAFT"


class CreateContentOperation(BaseModel):
    """Schema for create_content operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["create_content"]
    brand_id: str = Field(..., alias="brandId")
    campaign_id: Optional[str] = Field(None, alias="campaignId")
    data: CreateContentData
    save_as_artifact: Optional[bool] = Field(None, alias="saveAsArtifact")
    metadata: Optional[OperationMetadata] = None


class UpdateContentData(BaseModel):
    """Data for update_content operation (all fields optional)."""
    model_config = ConfigDict(populate_by_name=True)

    type: Optional[str] = None
    channel: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = Field(None, min_length=1)
    media_urls: Optional[List[str]] = Field(None, alias="mediaUrls")
    scheduled_at: Optional[str] = Field(None, alias="scheduledAt")
    status: Optional[str] = None


class UpdateContentOperation(BaseModel):
    """Schema for update_content operation."""
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["update_content"]
    content_id: str = Field(..., alias="contentId")
    data: UpdateContentData


# ==========================================
# Union Type
# ==========================================

EntityOperation = Union[
    CreateBrandOperation,
    CreateCampaignOperation,
    UpdateCampaignOperation,
    CreateContentOperation,
    UpdateContentOperation,
]


def parse_entity_operation(data: Dict[str, Any]) -> EntityOperation:
    """Parse a dictionary into the appropriate EntityOperation type.

    Args:
        data: Dictionary with operation data.

    Returns:
        The parsed operation.

    Raises:
        ValueError: If operation type is unknown or data is invalid.
    """
    op_type = data.get("type")

    if op_type == "create_brand":
        return CreateBrandOperation(**data)
    elif op_type == "create_campaign":
        return CreateCampaignOperation(**data)
    elif op_type == "update_campaign":
        return UpdateCampaignOperation(**data)
    elif op_type == "create_content":
        return CreateContentOperation(**data)
    elif op_type == "update_content":
        return UpdateContentOperation(**data)
    else:
        raise ValueError(f"Unknown operation type: {op_type}")
