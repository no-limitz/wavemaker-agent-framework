"""Tests for ToolRegistry."""

import sys
import os

# Add src to path to import directly without triggering package __init__
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest

# Import directly from modules to avoid langfuse import in main __init__
from wavemaker_agent_framework.tools.definitions import (
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
)
from wavemaker_agent_framework.tools.registry import ToolRegistry


class TestToolRegistry:
    """Tests for ToolRegistry."""

    @pytest.fixture
    def registry(self):
        """Create an empty registry."""
        return ToolRegistry()

    @pytest.fixture
    def sample_tool(self):
        """Create a sample tool definition."""
        return ToolDefinition(
            id="test.greet",
            name="greet_user",
            description="Greet a user by name",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="name",
                    type="string",
                    description="The name to greet",
                    required=True,
                ),
                ToolParameter(
                    name="formal",
                    type="boolean",
                    description="Use formal greeting",
                    required=False,
                    default=False,
                ),
            ],
        )

    def test_register_tool(self, registry, sample_tool):
        """Can register a tool."""
        def handler(name: str, formal: bool = False) -> ToolResult:
            return ToolResult.ok({"greeting": f"Hello, {name}!"})

        registry.register(sample_tool, handler)

        assert len(registry) == 1
        assert "test.greet" in registry
        assert registry.get("test.greet") == sample_tool

    def test_register_duplicate_id_fails(self, registry, sample_tool):
        """Cannot register duplicate tool ID."""
        handler = lambda: ToolResult.ok()
        registry.register(sample_tool, handler)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(sample_tool, handler)

    def test_register_duplicate_name_fails(self, registry, sample_tool):
        """Cannot register duplicate function name."""
        handler = lambda: ToolResult.ok()
        registry.register(sample_tool, handler)

        # Create another tool with different ID but same name
        duplicate = ToolDefinition(
            id="test.other",
            name="greet_user",  # Same name!
            description="Another tool",
            category=ToolCategory.UTILITY,
            parameters=[],
        )

        with pytest.raises(ValueError, match="already registered"):
            registry.register(duplicate, handler)

    def test_get_by_name(self, registry, sample_tool):
        """Can get tool by function name."""
        handler = lambda: ToolResult.ok()
        registry.register(sample_tool, handler)

        tool = registry.get_by_name("greet_user")
        assert tool is not None
        assert tool.id == "test.greet"

    def test_get_handler(self, registry, sample_tool):
        """Can get handler by ID."""
        def my_handler(name: str) -> ToolResult:
            return ToolResult.ok({"name": name})

        registry.register(sample_tool, my_handler)

        handler = registry.get_handler("test.greet")
        assert handler == my_handler

    def test_get_handler_by_name(self, registry, sample_tool):
        """Can get handler by function name."""
        def my_handler(name: str) -> ToolResult:
            return ToolResult.ok({"name": name})

        registry.register(sample_tool, my_handler)

        handler = registry.get_handler_by_name("greet_user")
        assert handler == my_handler

    def test_unregister(self, registry, sample_tool):
        """Can unregister a tool."""
        handler = lambda: ToolResult.ok()
        registry.register(sample_tool, handler)

        assert registry.unregister("test.greet")
        assert len(registry) == 0
        assert "test.greet" not in registry

    def test_list_by_category(self, registry):
        """Can list tools by category."""
        entity_tool = ToolDefinition(
            id="test.entity",
            name="do_entity",
            description="Entity tool",
            category=ToolCategory.ENTITY,
            parameters=[],
        )
        utility_tool = ToolDefinition(
            id="test.utility",
            name="do_utility",
            description="Utility tool",
            category=ToolCategory.UTILITY,
            parameters=[],
        )

        handler = lambda: ToolResult.ok()
        registry.register(entity_tool, handler)
        registry.register(utility_tool, handler)

        entity_tools = registry.list_by_category(ToolCategory.ENTITY)
        assert len(entity_tools) == 1
        assert entity_tools[0].id == "test.entity"

    def test_to_openai_tools(self, registry, sample_tool):
        """Converts tools to OpenAI format."""
        handler = lambda: ToolResult.ok()
        registry.register(sample_tool, handler)

        openai_tools = registry.to_openai_tools()

        assert len(openai_tools) == 1
        tool = openai_tools[0]
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "greet_user"
        assert tool["function"]["description"] == "Greet a user by name"
        assert "name" in tool["function"]["parameters"]["properties"]
        assert "name" in tool["function"]["parameters"]["required"]

    def test_to_openai_tools_specific_ids(self, registry):
        """Can convert specific tools to OpenAI format."""
        tool1 = ToolDefinition(
            id="t1", name="tool_one", description="One",
            category=ToolCategory.UTILITY, parameters=[]
        )
        tool2 = ToolDefinition(
            id="t2", name="tool_two", description="Two",
            category=ToolCategory.UTILITY, parameters=[]
        )

        handler = lambda: ToolResult.ok()
        registry.register(tool1, handler)
        registry.register(tool2, handler)

        # Only get tool1
        tools = registry.to_openai_tools(["t1"])
        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "tool_one"
