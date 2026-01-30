"""
Tool registry for managing agent tools.

Provides registration, lookup, and format conversion for tools.
"""

from typing import Any, Callable, Dict, List, Optional
from wavemaker_agent_framework.tools.definitions import (
    ToolDefinition,
    ToolResult,
    ToolCategory,
)


ToolHandler = Callable[..., ToolResult]


class ToolRegistry:
    """Central registry for all available tools.

    Supports registration, lookup, and conversion to LLM formats.
    Tools are registered with a definition and a handler function.
    """

    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._name_to_id: Dict[str, str] = {}  # Map function names to tool IDs

    def register(
        self,
        definition: ToolDefinition,
        handler: ToolHandler,
    ) -> None:
        """Register a tool with its handler.

        Args:
            definition: The tool definition with schema.
            handler: The callable that executes the tool.

        Raises:
            ValueError: If tool ID or function name already registered.
        """
        if definition.id in self._tools:
            raise ValueError(f"Tool '{definition.id}' already registered")
        if definition.name in self._name_to_id:
            raise ValueError(f"Function name '{definition.name}' already registered")

        self._tools[definition.id] = definition
        self._handlers[definition.id] = handler
        self._name_to_id[definition.name] = definition.id

    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool by ID.

        Args:
            tool_id: The tool ID to unregister.

        Returns:
            True if tool was unregistered, False if not found.
        """
        if tool_id not in self._tools:
            return False

        definition = self._tools[tool_id]
        del self._name_to_id[definition.name]
        del self._handlers[tool_id]
        del self._tools[tool_id]
        return True

    def get(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID.

        Args:
            tool_id: The tool ID to look up.

        Returns:
            The tool definition, or None if not found.
        """
        return self._tools.get(tool_id)

    def get_by_name(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by function name.

        Args:
            name: The function name to look up.

        Returns:
            The tool definition, or None if not found.
        """
        tool_id = self._name_to_id.get(name)
        if tool_id:
            return self._tools.get(tool_id)
        return None

    def get_handler(self, tool_id: str) -> Optional[ToolHandler]:
        """Get tool handler by ID.

        Args:
            tool_id: The tool ID to look up.

        Returns:
            The handler function, or None if not found.
        """
        return self._handlers.get(tool_id)

    def get_handler_by_name(self, name: str) -> Optional[ToolHandler]:
        """Get tool handler by function name.

        Args:
            name: The function name to look up.

        Returns:
            The handler function, or None if not found.
        """
        tool_id = self._name_to_id.get(name)
        if tool_id:
            return self._handlers.get(tool_id)
        return None

    def list_all(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """List all tools in a category.

        Args:
            category: The category to filter by.

        Returns:
            List of tool definitions in that category.
        """
        return [t for t in self._tools.values() if t.category == category]

    def list_ids(self) -> List[str]:
        """List all registered tool IDs."""
        return list(self._tools.keys())

    def to_openai_tools(self, tool_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Convert specified tools to OpenAI function calling format.

        Args:
            tool_ids: List of tool IDs to convert. If None, converts all tools.

        Returns:
            List of tools in OpenAI format.
        """
        if tool_ids is None:
            tool_ids = list(self._tools.keys())

        tools = []
        for tool_id in tool_ids:
            definition = self._tools.get(tool_id)
            if definition:
                tools.append(definition.to_openai_function())

        return tools

    def to_openai_tools_by_category(self, category: ToolCategory) -> List[Dict[str, Any]]:
        """Convert all tools in a category to OpenAI format.

        Args:
            category: The category to convert.

        Returns:
            List of tools in OpenAI format.
        """
        tool_ids = [t.id for t in self.list_by_category(category)]
        return self.to_openai_tools(tool_ids)

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __contains__(self, tool_id: str) -> bool:
        """Check if tool ID is registered."""
        return tool_id in self._tools
