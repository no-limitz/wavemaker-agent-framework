"""
End-to-end tests for agent execution flow.

Tests the complete flow from receiving a request to returning
entity operations, simulating BigRipple integration.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock

from bigripple_agent_framework.context.entity_context import EntityContext
from bigripple_agent_framework.context.context_injector import ContextInjector
from bigripple_agent_framework.tools.registry import ToolRegistry
from bigripple_agent_framework.tools.bigripple import create_bigripple_registry
from bigripple_agent_framework.operations.extractor import OperationExtractor
from bigripple_agent_framework.core.agent_runtime import AgentRuntime, AgentExecutionInput
from bigripple_agent_framework.testing.mocks.bigripple import (
    MockBigRippleClient,
    create_mock_llm_client,
    create_mock_tool_call,
)
from bigripple_agent_framework.testing.fixtures.context_fixtures import (
    sample_entity_context,
    sample_entity_context_json,
    sample_execution_request_json,
)


class TestAgentExecutionE2E:
    """End-to-end tests for agent execution."""

    @pytest.fixture
    def bigripple_client(self):
        """Create a mock BigRipple client."""
        return MockBigRippleClient()

    @pytest.fixture
    def tool_registry(self):
        """Create registry with BigRipple tools."""
        return create_bigripple_registry()

    @pytest.fixture
    def context(self):
        """Create sample entity context."""
        return sample_entity_context()

    @pytest.mark.asyncio
    async def test_simple_response_without_tools(self, tool_registry, context):
        """Test agent execution with simple text response (no tool calls)."""
        # Create mock LLM that returns simple text
        mock_llm = create_mock_llm_client([
            {"content": "Based on your brand voice and goals, I recommend focusing on thought leadership content.", "tool_calls": None}
        ])

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "What content strategy do you recommend?"},
            context=context,
            execution_id="exec_test_001",
            system_prompt="You are a marketing strategist.",
            enabled_tools=[],
        )

        result = await runtime.execute(input_data)

        assert result.success is True
        assert "thought leadership" in result.output.lower()
        assert len(result.entity_operations) == 0
        assert result.tokens_used["total"] > 0

    @pytest.mark.asyncio
    async def test_tool_calling_creates_campaign(self, tool_registry, context):
        """Test agent execution that creates a campaign via tool call."""
        # Create mock tool call
        tool_call = create_mock_tool_call(
            call_id="call_001",
            name="create_campaign",
            arguments={
                "brand_id": "brand_test123",
                "name": "Q2 Social Media Push",
                "channels": ["linkedin", "twitter"],
                "description": "Increase social presence",
                "goal": "Generate 1000 leads",
            }
        )

        # LLM first calls tool, then gives final response
        mock_llm = create_mock_llm_client([
            {"content": None, "tool_calls": [tool_call]},
            {"content": "I've created the Q2 Social Media Push campaign for you.", "tool_calls": None},
        ])

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Create a social media campaign for Q2"},
            context=context,
            execution_id="exec_test_002",
            system_prompt="You are a campaign planner.",
            enabled_tools=["bigripple.campaign.create"],
        )

        result = await runtime.execute(input_data)

        assert result.success is True
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["name"] == "create_campaign"

        # Should have extracted entity operation from tool result
        assert len(result.entity_operations) >= 1
        campaign_op = next(
            (op for op in result.entity_operations if op["type"] == "create_campaign"),
            None
        )
        assert campaign_op is not None
        assert campaign_op["data"]["name"] == "Q2 Social Media Push"

    @pytest.mark.asyncio
    async def test_tool_calling_creates_content(self, tool_registry, context):
        """Test agent execution that creates content via tool call."""
        tool_call = create_mock_tool_call(
            call_id="call_002",
            name="create_content",
            arguments={
                "brand_id": "brand_test123",
                "content_type": "SOCIAL_POST",
                "channel": "linkedin",
                "body": "Excited to announce our new product! #innovation #tech",
                "title": "Product Announcement",
            }
        )

        mock_llm = create_mock_llm_client([
            {"content": None, "tool_calls": [tool_call]},
            {"content": "I've drafted a LinkedIn post for the product announcement.", "tool_calls": None},
        ])

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Create a LinkedIn post announcing our new product"},
            context=context,
            execution_id="exec_test_003",
            system_prompt="You are a content writer.",
            enabled_tools=["bigripple.content.create"],
        )

        result = await runtime.execute(input_data)

        assert result.success is True
        assert len(result.entity_operations) >= 1
        content_op = next(
            (op for op in result.entity_operations if op["type"] == "create_content"),
            None
        )
        assert content_op is not None
        assert content_op["data"]["channel"] == "linkedin"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, tool_registry, context):
        """Test agent execution with multiple tool calls."""
        # Agent creates both a campaign and content
        campaign_call = create_mock_tool_call(
            call_id="call_003",
            name="create_campaign",
            arguments={
                "brand_id": "brand_test123",
                "name": "Product Launch",
                "channels": ["linkedin", "twitter", "email"],
            }
        )
        content_call = create_mock_tool_call(
            call_id="call_004",
            name="create_content",
            arguments={
                "brand_id": "brand_test123",
                "content_type": "SOCIAL_POST",
                "channel": "linkedin",
                "body": "Big news coming soon! Stay tuned.",
            }
        )

        mock_llm = create_mock_llm_client([
            {"content": None, "tool_calls": [campaign_call, content_call]},
            {"content": "I've created a campaign and initial teaser content.", "tool_calls": None},
        ])

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Plan a product launch campaign with teaser content"},
            context=context,
            execution_id="exec_test_004",
            system_prompt="You are a marketing strategist.",
            enabled_tools=["bigripple.campaign.create", "bigripple.content.create"],
        )

        result = await runtime.execute(input_data)

        assert result.success is True
        assert len(result.tool_calls) == 2
        assert len(result.entity_operations) >= 2

    @pytest.mark.asyncio
    async def test_context_injection_includes_brand_voice(self, tool_registry, context):
        """Test that brand voice is properly injected into context."""
        # Track what gets sent to LLM
        captured_messages = []

        async def capture_create(**kwargs):
            captured_messages.append(kwargs.get("messages", []))
            mock_message = MagicMock()
            mock_message.content = "Response acknowledging brand voice."
            mock_message.tool_calls = None
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_response.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
            return mock_response

        mock_llm = MagicMock()
        mock_llm.chat.completions.create = AsyncMock(side_effect=capture_create)

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Write content for our brand"},
            context=context,
            execution_id="exec_test_005",
            system_prompt="You are a content writer.",
            enabled_tools=[],
        )

        await runtime.execute(input_data)

        # Check that system prompt includes brand voice
        assert len(captured_messages) > 0
        system_message = captured_messages[0][0]["content"]
        assert "Brand Voice" in system_message or "professional" in system_message

    @pytest.mark.asyncio
    async def test_bigripple_processes_operations(self, bigripple_client, tool_registry, context):
        """Test that BigRipple mock correctly processes operations."""
        # Create some operations
        operations = [
            {
                "type": "create_campaign",
                "brandId": "brand_test123",
                "data": {
                    "name": "Test Campaign",
                    "channels": ["linkedin"],
                    "status": "DRAFT",
                },
            },
            {
                "type": "create_content",
                "brandId": "brand_test123",
                "data": {
                    "type": "SOCIAL_POST",
                    "channel": "linkedin",
                    "body": "Test content",
                },
            },
        ]

        # Process operations through mock BigRipple
        results = []
        for op in operations:
            result = await bigripple_client.process_operation(op)
            results.append(result)

        # Verify all succeeded
        assert all(r["success"] for r in results)

        # Verify entities were created
        assert len(bigripple_client.created_campaigns) == 1
        assert len(bigripple_client.created_contents) == 1

        # Verify entity IDs were generated
        assert bigripple_client.created_campaigns[0]["id"].startswith("campaign_")
        assert bigripple_client.created_contents[0]["id"].startswith("content_")

    @pytest.mark.asyncio
    async def test_error_handling(self, tool_registry, context):
        """Test that errors are properly handled."""
        # Create mock LLM that raises an error
        mock_llm = MagicMock()
        mock_llm.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        runtime = AgentRuntime(mock_llm, tool_registry)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Test prompt"},
            context=context,
            execution_id="exec_test_006",
            system_prompt="Test system prompt.",
            enabled_tools=[],
        )

        result = await runtime.execute(input_data)

        assert result.success is False
        assert result.error is not None
        assert "API Error" in result.error["message"]


class TestEntityContextParsing:
    """Test parsing entity context from JSON (as BigRipple sends it)."""

    def test_parse_from_camelcase_json(self):
        """Test parsing EntityContext from camelCase JSON."""
        json_data = sample_entity_context_json()
        context = EntityContext(**json_data)

        assert context.user_id == "user_test123"
        assert context.brand_id == "brand_test123"
        assert len(context.brands) == 1
        assert context.brands[0].name == "TechCorp"
        assert context.brand_voice.tone == "professional"
        assert context.retrieval_context is not None

    def test_parse_execution_request(self):
        """Test parsing a full execution request."""
        request = sample_execution_request_json()

        # Parse context
        context = EntityContext(**request["context"])
        assert context.user_id == "user_test123"

        # Verify input data
        assert request["input"]["goal"] == "Create a social media campaign for product launch"
        assert request["executionId"] == "exec_test123"
