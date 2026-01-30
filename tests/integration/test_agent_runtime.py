"""
Integration tests for AgentRuntime.

Tests the integration between context injection, tool execution,
and operation extraction.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from wavemaker_agent_framework.context.entity_context import EntityContext
from wavemaker_agent_framework.context.context_injector import ContextInjector
from wavemaker_agent_framework.tools.registry import ToolRegistry
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry
from wavemaker_agent_framework.tools.executor import ToolExecutor
from wavemaker_agent_framework.operations.extractor import OperationExtractor
from wavemaker_agent_framework.core.agent_runtime import (
    AgentRuntime,
    AgentExecutionInput,
    create_default_runtime,
)
from wavemaker_agent_framework.testing.mocks.bigripple import (
    create_mock_llm_client,
    create_mock_tool_call,
)
from wavemaker_agent_framework.testing.fixtures.context_fixtures import (
    sample_entity_context,
    sample_brand_voice,
)


class TestContextInjectionIntegration:
    """Test context injection in the runtime."""

    @pytest.fixture
    def context(self):
        """Create sample context."""
        return sample_entity_context()

    @pytest.fixture
    def injector(self):
        """Create context injector."""
        return ContextInjector()

    def test_full_context_prompt_generation(self, context, injector):
        """Test generating full context prompt."""
        prompt = injector.build_context_prompt(context)

        # Should contain all sections
        assert "## Current Context" in prompt
        assert "## Available Brands" in prompt
        assert "## Brand Voice Guidelines" in prompt
        assert "## Active Campaigns" in prompt
        assert "## Recent Content" in prompt
        assert "## Knowledge Base Context" in prompt

        # Should contain actual data
        assert "TechCorp" in prompt
        assert "professional" in prompt
        assert "Q1 Product Launch" in prompt

    def test_context_prompt_with_rag(self, context, injector):
        """Test that RAG context is included."""
        prompt = injector.build_context_prompt(context)

        # Should include RAG content
        assert "Q4 2024 Campaign Analysis" in prompt or "Knowledge Base Context" in prompt


class TestToolExecutionIntegration:
    """Test tool execution integration."""

    @pytest.fixture
    def registry(self):
        """Create BigRipple registry."""
        return create_bigripple_registry()

    @pytest.fixture
    def executor(self, registry):
        """Create tool executor."""
        return ToolExecutor(registry)

    @pytest.mark.asyncio
    async def test_execute_create_campaign(self, executor):
        """Test executing create_campaign tool."""
        result = await executor.execute(
            tool_name="create_campaign",
            arguments={
                "brand_id": "brand_123",
                "name": "Test Campaign",
                "channels": ["linkedin", "twitter"],
                "description": "A test campaign",
            },
            context={"execution_id": "exec_123"},
        )

        assert result.success is True
        assert result.entity_operation is not None
        assert result.entity_operation["type"] == "create_campaign"
        assert result.entity_operation["brandId"] == "brand_123"
        assert result.entity_operation["data"]["name"] == "Test Campaign"

    @pytest.mark.asyncio
    async def test_execute_create_content(self, executor):
        """Test executing create_content tool."""
        result = await executor.execute(
            tool_name="create_content",
            arguments={
                "brand_id": "brand_123",
                "content_type": "SOCIAL_POST",
                "channel": "linkedin",
                "body": "Check out our latest product!",
                "title": "Product Update",
            },
            context={"execution_id": "exec_123"},
        )

        assert result.success is True
        assert result.entity_operation is not None
        assert result.entity_operation["type"] == "create_content"
        assert result.entity_operation["data"]["type"] == "SOCIAL_POST"

    @pytest.mark.asyncio
    async def test_execute_with_missing_required_param(self, executor):
        """Test tool execution with missing required parameter."""
        result = await executor.execute(
            tool_name="create_campaign",
            arguments={
                "brand_id": "brand_123",
                # Missing 'name' and 'channels'
            },
        )

        assert result.success is False
        assert result.error["code"] == "MISSING_PARAMETERS"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self, executor):
        """Test executing unknown tool."""
        result = await executor.execute(
            tool_name="unknown_tool",
            arguments={},
        )

        assert result.success is False
        assert result.error["code"] == "TOOL_NOT_FOUND"


class TestOperationExtractionIntegration:
    """Test operation extraction integration."""

    @pytest.fixture
    def extractor(self):
        """Create operation extractor."""
        return OperationExtractor()

    def test_extract_from_tool_results(self, extractor):
        """Test extracting operations from tool results."""
        tool_results = [
            {
                "success": True,
                "entity_operation": {
                    "type": "create_campaign",
                    "brandId": "brand_123",
                    "data": {"name": "Campaign", "channels": []},
                },
            },
            {
                "success": True,
                "entity_operation": {
                    "type": "create_content",
                    "brandId": "brand_123",
                    "data": {"type": "SOCIAL_POST", "channel": "linkedin", "body": "Hello"},
                },
            },
        ]

        _, operations = extractor.extract({}, tool_results=tool_results)

        assert len(operations) == 2
        assert operations[0]["type"] == "create_campaign"
        assert operations[1]["type"] == "create_content"

    def test_extract_from_output_with_explicit_operations(self, extractor):
        """Test extracting explicit entityOperations from output."""
        output = {
            "summary": "Created a campaign",
            "entityOperations": [
                {
                    "type": "create_campaign",
                    "brandId": "brand_123",
                    "data": {"name": "Explicit Campaign", "channels": ["linkedin"]},
                }
            ],
        }

        cleaned, operations = extractor.extract(output)

        assert len(operations) == 1
        assert operations[0]["data"]["name"] == "Explicit Campaign"
        assert "entityOperations" not in cleaned

    def test_extract_inferred_from_campaigns_key(self, extractor):
        """Test inferring operations from campaigns key."""
        output = {
            "campaigns": [
                {
                    "name": "Inferred Campaign",
                    "channels": ["twitter"],
                    "createInSystem": True,
                }
            ],
        }

        _, operations = extractor.extract(output, brand_id="brand_123")

        assert len(operations) == 1
        assert operations[0]["type"] == "create_campaign"
        assert operations[0]["data"]["name"] == "Inferred Campaign"


class TestRuntimeIntegration:
    """Test full runtime integration."""

    @pytest.fixture
    def context(self):
        """Create sample context."""
        return sample_entity_context()

    @pytest.mark.asyncio
    async def test_create_default_runtime(self):
        """Test creating default runtime with BigRipple tools."""
        mock_llm = create_mock_llm_client([
            {"content": "Hello!", "tool_calls": None}
        ])

        runtime = create_default_runtime(mock_llm, include_bigripple_tools=True)

        # Should have BigRipple tools registered
        assert "bigripple.campaign.create" in runtime.tool_registry
        assert "bigripple.content.create" in runtime.tool_registry
        assert "bigripple.brand.create" in runtime.tool_registry

    @pytest.mark.asyncio
    async def test_runtime_tracks_token_usage(self, context):
        """Test that runtime properly tracks token usage."""
        mock_llm = create_mock_llm_client([
            {"content": "Response text", "tool_calls": None}
        ])

        runtime = create_default_runtime(mock_llm)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Test"},
            context=context,
            execution_id="exec_001",
            system_prompt="Test prompt",
        )

        result = await runtime.execute(input_data)

        assert result.tokens_used["prompt"] == 100
        assert result.tokens_used["completion"] == 50
        assert result.tokens_used["total"] == 150

    @pytest.mark.asyncio
    async def test_runtime_tracks_duration(self, context):
        """Test that runtime properly tracks duration."""
        mock_llm = create_mock_llm_client([
            {"content": "Response", "tool_calls": None}
        ])

        runtime = create_default_runtime(mock_llm)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Test"},
            context=context,
            execution_id="exec_001",
            system_prompt="Test prompt",
        )

        result = await runtime.execute(input_data)

        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_runtime_with_tool_loop(self, context):
        """Test runtime with multiple tool calling iterations."""
        # First call returns tool, second returns final response
        tool_call = create_mock_tool_call(
            call_id="call_1",
            name="create_campaign",
            arguments={
                "brand_id": "brand_123",
                "name": "Test",
                "channels": ["linkedin"],
            },
        )

        mock_llm = create_mock_llm_client([
            {"content": None, "tool_calls": [tool_call]},
            {"content": "Done!", "tool_calls": None},
        ])

        runtime = create_default_runtime(mock_llm)

        input_data = AgentExecutionInput(
            input_data={"prompt": "Create a campaign"},
            context=context,
            execution_id="exec_001",
            system_prompt="You are a planner.",
            enabled_tools=["bigripple.campaign.create"],
        )

        result = await runtime.execute(input_data)

        assert result.success is True
        assert len(result.tool_calls) == 1
        assert len(result.entity_operations) >= 1
