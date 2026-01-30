"""
Operation extractor for extracting entity operations from agent output.

Supports both explicit operations (in entityOperations array) and
inferred operations (from common output patterns like campaigns[], posts[], etc.).
"""

import logging
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


# Keys that indicate campaign suggestions in agent output
CAMPAIGN_KEYS = ["campaigns", "campaignOptions", "suggestedCampaigns", "campaignProposals"]

# Keys that indicate content suggestions in agent output
CONTENT_KEYS = ["contents", "contentItems", "suggestedContent", "posts", "socialPosts", "contentCalendar"]

# Flags that indicate an item should be created in the system
CREATE_FLAGS = ["createInSystem", "saveToDatabase", "autoCreate", "save", "create"]


class OperationExtractor:
    """Extracts entity operations from agent output and tool results.

    Supports two patterns:
    1. Explicit: Operations in an 'entityOperations' array
    2. Inferred: Operations derived from output structure (campaigns[], posts[], etc.)
    """

    def __init__(
        self,
        infer_operations: bool = True,
        require_create_flag: bool = True,
    ):
        """Initialize the extractor.

        Args:
            infer_operations: Whether to infer operations from output structure.
            require_create_flag: If True, only infer operations when a create flag is set.
        """
        self.infer_operations = infer_operations
        self.require_create_flag = require_create_flag

    def extract(
        self,
        agent_output: Any,
        tool_results: Optional[List[Dict[str, Any]]] = None,
        brand_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """Extract entity operations from output.

        Args:
            agent_output: The agent's raw output.
            tool_results: List of tool call results (may contain entity_operation).
            brand_id: Default brand ID for inferred operations.
            campaign_id: Default campaign ID for inferred content.
            execution_id: Execution ID for metadata.

        Returns:
            Tuple of (cleaned_output, operations_list).
            The cleaned output has entityOperations removed if present.
        """
        operations: List[Dict[str, Any]] = []

        # 1. Extract from tool results
        if tool_results:
            for result in tool_results:
                if isinstance(result, dict):
                    # Check for entity_operation (Python naming)
                    if result.get("entity_operation"):
                        operations.append(result["entity_operation"])
                    # Check for entityOperation (JS naming)
                    elif result.get("entityOperation"):
                        operations.append(result["entityOperation"])

        # 2. Extract from agent output if it's a dict
        if isinstance(agent_output, dict):
            # Check for explicit entityOperations key
            if "entityOperations" in agent_output:
                explicit_ops = agent_output.get("entityOperations", [])
                if isinstance(explicit_ops, list):
                    operations.extend(explicit_ops)
                # Remove from output after extraction
                agent_output = {k: v for k, v in agent_output.items() if k != "entityOperations"}

            # Infer operations from common patterns
            if self.infer_operations:
                # Get default IDs from output or parameters
                default_brand_id = brand_id or agent_output.get("brandId")
                default_campaign_id = campaign_id or agent_output.get("campaignId")

                # Check for campaign suggestions
                for key in CAMPAIGN_KEYS:
                    if key in agent_output:
                        campaign_ops = self._convert_campaigns_to_operations(
                            agent_output[key],
                            default_brand_id,
                            execution_id,
                        )
                        operations.extend(campaign_ops)

                # Check for content suggestions
                for key in CONTENT_KEYS:
                    if key in agent_output:
                        content_ops = self._convert_contents_to_operations(
                            agent_output[key],
                            default_brand_id,
                            default_campaign_id,
                            execution_id,
                        )
                        operations.extend(content_ops)

        return agent_output, operations

    def _should_create(self, item: Dict[str, Any]) -> bool:
        """Check if an item should be created based on flags."""
        if not self.require_create_flag:
            return True

        for flag in CREATE_FLAGS:
            if item.get(flag, False):
                return True
        return False

    def _convert_campaigns_to_operations(
        self,
        campaigns: Any,
        brand_id: Optional[str],
        execution_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Convert campaign suggestions to create operations."""
        if not isinstance(campaigns, list):
            return []

        operations = []
        for campaign in campaigns:
            if not isinstance(campaign, dict):
                continue

            if not self._should_create(campaign):
                continue

            # Get brand ID from item or default
            item_brand_id = campaign.get("brandId") or campaign.get("brand_id") or brand_id
            if not item_brand_id:
                logger.warning("Skipping campaign: no brandId available")
                continue

            # Map property names (handle both camelCase and snake_case)
            operation = {
                "type": "create_campaign",
                "brandId": item_brand_id,
                "data": {
                    "name": campaign.get("name"),
                    "description": campaign.get("description"),
                    "goal": campaign.get("goal"),
                    "targetAudience": campaign.get("targetAudience") or campaign.get("target_audience"),
                    "channels": campaign.get("channels", []),
                    "status": "DRAFT",
                },
                "metadata": {
                    "aiGenerated": True,
                    "sourceExecutionId": execution_id or "inferred",
                },
            }

            # Add dates if present
            if campaign.get("startDate") or campaign.get("start_date"):
                operation["data"]["startDate"] = campaign.get("startDate") or campaign.get("start_date")
            if campaign.get("endDate") or campaign.get("end_date"):
                operation["data"]["endDate"] = campaign.get("endDate") or campaign.get("end_date")

            # Clean up None values
            operation["data"] = {k: v for k, v in operation["data"].items() if v is not None}

            operations.append(operation)

        return operations

    def _convert_contents_to_operations(
        self,
        contents: Any,
        brand_id: Optional[str],
        campaign_id: Optional[str],
        execution_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Convert content suggestions to create operations."""
        if not isinstance(contents, list):
            return []

        operations = []
        for content in contents:
            if not isinstance(content, dict):
                continue

            if not self._should_create(content):
                continue

            # Get IDs from item or defaults
            item_brand_id = content.get("brandId") or content.get("brand_id") or brand_id
            if not item_brand_id:
                logger.warning("Skipping content: no brandId available")
                continue

            item_campaign_id = content.get("campaignId") or content.get("campaign_id") or campaign_id

            # Infer content type
            content_type = self._infer_content_type(content)

            # Get body from various possible keys
            body = (
                content.get("body")
                or content.get("content")
                or content.get("text")
                or content.get("message")
            )

            if not body:
                logger.warning("Skipping content: no body found")
                continue

            operation = {
                "type": "create_content",
                "brandId": item_brand_id,
                "data": {
                    "type": content_type,
                    "channel": content.get("channel", "linkedin"),
                    "title": content.get("title"),
                    "body": body,
                    "status": "DRAFT",
                },
                "metadata": {
                    "aiGenerated": True,
                    "sourceExecutionId": execution_id or "inferred",
                },
            }

            # Add campaign ID if present
            if item_campaign_id:
                operation["campaignId"] = item_campaign_id

            # Add optional fields
            if content.get("mediaUrls") or content.get("media_urls"):
                operation["data"]["mediaUrls"] = content.get("mediaUrls") or content.get("media_urls")
            if content.get("scheduledAt") or content.get("scheduled_at"):
                operation["data"]["scheduledAt"] = content.get("scheduledAt") or content.get("scheduled_at")

            # Clean up None values
            operation["data"] = {k: v for k, v in operation["data"].items() if v is not None}

            operations.append(operation)

        return operations

    def _infer_content_type(self, content: Dict[str, Any]) -> str:
        """Infer content type from content data."""
        # Check explicit type field
        explicit_type = content.get("type") or content.get("contentType")
        if explicit_type:
            # Map common variations to valid types
            type_map = {
                "blog": "BLOG_POST",
                "blog_post": "BLOG_POST",
                "blogpost": "BLOG_POST",
                "social": "SOCIAL_POST",
                "social_post": "SOCIAL_POST",
                "socialpost": "SOCIAL_POST",
                "post": "SOCIAL_POST",
                "email": "EMAIL",
                "ad": "AD_COPY",
                "ad_copy": "AD_COPY",
                "adcopy": "AD_COPY",
                "landing": "LANDING_PAGE",
                "landing_page": "LANDING_PAGE",
                "landingpage": "LANDING_PAGE",
            }
            normalized = explicit_type.lower().replace("-", "_")
            if normalized in type_map:
                return type_map[normalized]
            if explicit_type.upper() in ["BLOG_POST", "SOCIAL_POST", "EMAIL", "AD_COPY", "LANDING_PAGE"]:
                return explicit_type.upper()

        # Infer from channel
        channel = content.get("channel", "").lower()
        if channel in ["facebook", "instagram", "linkedin", "twitter"]:
            return "SOCIAL_POST"
        if channel == "blog":
            return "BLOG_POST"
        if channel == "email":
            return "EMAIL"

        # Default to social post
        return "SOCIAL_POST"
