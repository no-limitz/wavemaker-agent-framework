"""
Tool executor for running registered tools.

Handles argument parsing, validation, and execution of tools
from LLM tool calls.
"""

import json
import logging
from typing import Any, Dict, Optional
from bigripple_agent_framework.tools.registry import ToolRegistry
from bigripple_agent_framework.tools.definitions import ToolResult


logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools from the registry based on LLM tool calls.

    Handles parsing arguments, validating against schema, and
    invoking the registered handler.
    """

    def __init__(self, registry: ToolRegistry):
        """Initialize the executor with a tool registry.

        Args:
            registry: The tool registry to use for lookups.
        """
        self.registry = registry

    async def execute(
        self,
        tool_name: str,
        arguments: str | Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Execute a tool by function name with given arguments.

        Args:
            tool_name: The function name of the tool to execute.
            arguments: The arguments as JSON string or dict.
            context: Optional execution context (execution_id, tenant_context, etc.).

        Returns:
            The result of tool execution.
        """
        # Parse arguments if string
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool arguments: {e}")
                return ToolResult.fail(
                    code="INVALID_ARGUMENTS",
                    message=f"Failed to parse arguments JSON: {e}",
                )
        else:
            args = arguments

        # Look up tool by function name
        definition = self.registry.get_by_name(tool_name)
        if not definition:
            logger.warning(f"Tool not found: {tool_name}")
            return ToolResult.fail(
                code="TOOL_NOT_FOUND",
                message=f"Tool '{tool_name}' is not registered",
            )

        handler = self.registry.get_handler_by_name(tool_name)
        if not handler:
            logger.error(f"Handler not found for tool: {tool_name}")
            return ToolResult.fail(
                code="HANDLER_NOT_FOUND",
                message=f"Handler for tool '{tool_name}' is not registered",
            )

        # Validate required parameters
        missing = []
        for param_name in definition.get_required_params():
            if param_name not in args:
                missing.append(param_name)

        if missing:
            logger.warning(f"Missing required parameters: {missing}")
            return ToolResult.fail(
                code="MISSING_PARAMETERS",
                message=f"Missing required parameters: {', '.join(missing)}",
                details={"missing": missing},
            )

        # Merge context into args if provided
        if context:
            args = {**args, **context}

        # Execute handler
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = handler(**args)

            # Handle both sync and async handlers
            if hasattr(result, "__await__"):
                result = await result

            logger.info(f"Tool {tool_name} completed: success={result.success}")
            return result

        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return ToolResult.fail(
                code="EXECUTION_ERROR",
                message=str(e),
            )

    def execute_sync(
        self,
        tool_name: str,
        arguments: str | Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Execute a tool synchronously.

        For use when async is not available. Handler must be synchronous.

        Args:
            tool_name: The function name of the tool to execute.
            arguments: The arguments as JSON string or dict.
            context: Optional execution context.

        Returns:
            The result of tool execution.
        """
        # Parse arguments if string
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError as e:
                return ToolResult.fail(
                    code="INVALID_ARGUMENTS",
                    message=f"Failed to parse arguments JSON: {e}",
                )
        else:
            args = arguments

        # Look up tool
        definition = self.registry.get_by_name(tool_name)
        if not definition:
            return ToolResult.fail(
                code="TOOL_NOT_FOUND",
                message=f"Tool '{tool_name}' is not registered",
            )

        handler = self.registry.get_handler_by_name(tool_name)
        if not handler:
            return ToolResult.fail(
                code="HANDLER_NOT_FOUND",
                message=f"Handler for tool '{tool_name}' is not registered",
            )

        # Validate required parameters
        missing = []
        for param_name in definition.get_required_params():
            if param_name not in args:
                missing.append(param_name)

        if missing:
            return ToolResult.fail(
                code="MISSING_PARAMETERS",
                message=f"Missing required parameters: {', '.join(missing)}",
                details={"missing": missing},
            )

        # Merge context
        if context:
            args = {**args, **context}

        # Execute
        try:
            result = handler(**args)
            return result
        except Exception as e:
            return ToolResult.fail(
                code="EXECUTION_ERROR",
                message=str(e),
            )
