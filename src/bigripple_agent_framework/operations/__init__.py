"""
Operations module for entity operation handling.

Provides schemas, extraction, and formatting for entity operations
that can be returned to BigRipple for processing.
"""

from bigripple_agent_framework.operations.schemas import (
    EntityOperationType,
    OperationMetadata,
    CreateBrandOperation,
    CreateCampaignOperation,
    UpdateCampaignOperation,
    CreateContentOperation,
    UpdateContentOperation,
    EntityOperation,
)
from bigripple_agent_framework.operations.extractor import OperationExtractor
from bigripple_agent_framework.operations.formatter import ResponseFormatter

__all__ = [
    "EntityOperationType",
    "OperationMetadata",
    "CreateBrandOperation",
    "CreateCampaignOperation",
    "UpdateCampaignOperation",
    "CreateContentOperation",
    "UpdateContentOperation",
    "EntityOperation",
    "OperationExtractor",
    "ResponseFormatter",
]
