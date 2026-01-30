"""
BigRipple mock client for testing.

Provides mock implementations of BigRipple API responses for testing
agents without connecting to the actual BigRipple platform.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import uuid


class MockBigRippleClient:
    """Mock client for BigRipple API interactions.

    Simulates BigRipple API responses for testing purposes.
    Tracks created entities and operations for verification.
    """

    def __init__(self):
        """Initialize the mock client."""
        self.created_brands: List[Dict[str, Any]] = []
        self.created_campaigns: List[Dict[str, Any]] = []
        self.created_contents: List[Dict[str, Any]] = []
        self.updated_campaigns: List[Dict[str, Any]] = []
        self.updated_contents: List[Dict[str, Any]] = []
        self.operation_results: List[Dict[str, Any]] = []

    def reset(self):
        """Reset all tracked entities."""
        self.created_brands.clear()
        self.created_campaigns.clear()
        self.created_contents.clear()
        self.updated_campaigns.clear()
        self.updated_contents.clear()
        self.operation_results.clear()

    async def process_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Process an entity operation and return the result.

        Args:
            operation: The entity operation to process.

        Returns:
            Operation result with created/updated entity.
        """
        op_type = operation.get("type")

        if op_type == "create_brand":
            return await self._create_brand(operation)
        elif op_type == "create_campaign":
            return await self._create_campaign(operation)
        elif op_type == "create_content":
            return await self._create_content(operation)
        elif op_type == "update_campaign":
            return await self._update_campaign(operation)
        elif op_type == "update_content":
            return await self._update_content(operation)
        else:
            return {
                "success": False,
                "operation": operation,
                "error": {
                    "code": "UNKNOWN_OPERATION",
                    "message": f"Unknown operation type: {op_type}",
                },
            }

    async def _create_brand(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Mock brand creation."""
        brand_id = f"brand_{uuid.uuid4().hex[:8]}"
        data = operation.get("data", {})

        brand = {
            "id": brand_id,
            "customerId": operation.get("customerId"),
            "name": data.get("name"),
            "slug": data.get("slug"),
            "description": data.get("description"),
            "voiceSettings": data.get("voiceSettings"),
            "primaryColor": data.get("primaryColor"),
            "logoUrl": data.get("logoUrl"),
            "aiGenerated": True,
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.created_brands.append(brand)
        result = {
            "success": True,
            "operation": operation,
            "result": {
                "entityType": "brand",
                "entityId": brand_id,
                "entity": brand,
            },
        }
        self.operation_results.append(result)
        return result

    async def _create_campaign(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Mock campaign creation."""
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        data = operation.get("data", {})

        campaign = {
            "id": campaign_id,
            "brandId": operation.get("brandId"),
            "name": data.get("name"),
            "description": data.get("description"),
            "goal": data.get("goal"),
            "targetAudience": data.get("targetAudience"),
            "channels": data.get("channels", []),
            "status": data.get("status", "DRAFT"),
            "startDate": data.get("startDate"),
            "endDate": data.get("endDate"),
            "aiGenerated": True,
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.created_campaigns.append(campaign)
        result = {
            "success": True,
            "operation": operation,
            "result": {
                "entityType": "campaign",
                "entityId": campaign_id,
                "entity": campaign,
            },
        }
        self.operation_results.append(result)
        return result

    async def _create_content(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Mock content creation."""
        content_id = f"content_{uuid.uuid4().hex[:8]}"
        data = operation.get("data", {})

        content = {
            "id": content_id,
            "brandId": operation.get("brandId"),
            "campaignId": operation.get("campaignId"),
            "type": data.get("type"),
            "channel": data.get("channel"),
            "title": data.get("title"),
            "body": data.get("body"),
            "mediaUrls": data.get("mediaUrls", []),
            "status": data.get("status", "DRAFT"),
            "scheduledAt": data.get("scheduledAt"),
            "aiGenerated": True,
            "createdAt": datetime.utcnow().isoformat(),
        }

        self.created_contents.append(content)
        result = {
            "success": True,
            "operation": operation,
            "result": {
                "entityType": "content",
                "entityId": content_id,
                "entity": content,
            },
        }
        self.operation_results.append(result)
        return result

    async def _update_campaign(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Mock campaign update."""
        campaign_id = operation.get("campaignId")
        data = operation.get("data", {})

        update_record = {
            "campaignId": campaign_id,
            "updates": data,
            "updatedAt": datetime.utcnow().isoformat(),
        }

        self.updated_campaigns.append(update_record)
        result = {
            "success": True,
            "operation": operation,
            "result": {
                "entityType": "campaign",
                "entityId": campaign_id,
                "entity": {"id": campaign_id, **data},
            },
        }
        self.operation_results.append(result)
        return result

    async def _update_content(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Mock content update."""
        content_id = operation.get("contentId")
        data = operation.get("data", {})

        update_record = {
            "contentId": content_id,
            "updates": data,
            "updatedAt": datetime.utcnow().isoformat(),
        }

        self.updated_contents.append(update_record)
        result = {
            "success": True,
            "operation": operation,
            "result": {
                "entityType": "content",
                "entityId": content_id,
                "entity": {"id": content_id, **data},
            },
        }
        self.operation_results.append(result)
        return result


class MockAgentFieldClient:
    """Mock AgentField client for testing agent invocations."""

    def __init__(self, mock_response: Optional[Dict[str, Any]] = None):
        """Initialize with optional mock response.

        Args:
            mock_response: The response to return from invoke calls.
        """
        self.mock_response = mock_response or {
            "success": True,
            "output": {"message": "Mock response"},
            "entityOperations": [],
        }
        self.invocations: List[Dict[str, Any]] = []

    def set_response(self, response: Dict[str, Any]):
        """Set the mock response."""
        self.mock_response = response

    async def invoke(
        self,
        agent: str,
        method: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mock agent invocation.

        Args:
            agent: Agent name.
            method: Method to call.
            input_data: Input data for the agent.
            context: Optional entity context.

        Returns:
            Mock response.
        """
        self.invocations.append({
            "agent": agent,
            "method": method,
            "input": input_data,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return self.mock_response

    async def invoke_direct(
        self,
        endpoint: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Mock direct agent invocation."""
        self.invocations.append({
            "endpoint": endpoint,
            "input": input_data,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return self.mock_response

    def reset(self):
        """Reset invocation history."""
        self.invocations.clear()


def create_mock_llm_client(responses: Optional[List[Dict[str, Any]]] = None) -> MagicMock:
    """Create a mock LLM client for testing.

    Args:
        responses: List of responses to return in sequence.
                  Each response should have 'content' and optionally 'tool_calls'.

    Returns:
        Mock AsyncOpenAI client.
    """
    if responses is None:
        responses = [{"content": "Mock LLM response", "tool_calls": None}]

    response_iter = iter(responses)

    def get_next_response():
        try:
            return next(response_iter)
        except StopIteration:
            # Return last response if we run out
            return responses[-1] if responses else {"content": "", "tool_calls": None}

    mock_client = MagicMock()

    async def mock_create(**kwargs):
        response_data = get_next_response()

        # Build mock message
        mock_message = MagicMock()
        mock_message.content = response_data.get("content", "")
        mock_message.tool_calls = response_data.get("tool_calls")

        # Build mock choice
        mock_choice = MagicMock()
        mock_choice.message = mock_message

        # Build mock response
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        return mock_response

    mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)

    return mock_client


def create_mock_tool_call(
    call_id: str,
    name: str,
    arguments: Dict[str, Any],
) -> MagicMock:
    """Create a mock tool call object.

    Args:
        call_id: The tool call ID.
        name: Function name.
        arguments: Function arguments.

    Returns:
        Mock tool call object.
    """
    import json

    mock_call = MagicMock()
    mock_call.id = call_id
    mock_call.function = MagicMock()
    mock_call.function.name = name
    mock_call.function.arguments = json.dumps(arguments)

    return mock_call
