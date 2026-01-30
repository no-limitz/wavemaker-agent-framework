"""
Response formatter for BigRipple agent responses.

Formats agent execution output into the standard response format
expected by BigRipple's ExecutionOutputParser.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AgentResponse(BaseModel):
    """Standard response format for BigRipple agents.

    This matches the expected response format in:
    apps/web/lib/entities/execution-output-parser.ts
    """
    # Use camelCase for JSON serialization to match BigRipple expectations
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    output: Any
    entity_operations: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    tokens_used: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}
    duration_ms: int = 0
    error: Optional[Dict[str, Any]] = None

    def to_bigripple_format(self) -> Dict[str, Any]:
        """Convert to BigRipple's expected JSON format with camelCase keys."""
        result = {
            "success": self.success,
            "output": self.output,
            "entityOperations": self.entity_operations,
            "toolCalls": self.tool_calls,
            "tokensUsed": self.tokens_used,
            "durationMs": self.duration_ms,
        }
        if self.error:
            result["error"] = self.error
        return result


class ResponseFormatter:
    """Formats agent execution results for BigRipple.

    Handles conversion from internal Python formats to the JSON
    format expected by BigRipple's execution output parser.
    """

    def format_success(
        self,
        output: Any,
        entity_operations: Optional[List[Dict[str, Any]]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        duration_ms: int = 0,
    ) -> Dict[str, Any]:
        """Format a successful execution result.

        Args:
            output: The agent's primary output.
            entity_operations: List of entity operations to process.
            tool_calls: List of tool calls made during execution.
            tokens_used: Token usage statistics.
            duration_ms: Execution duration in milliseconds.

        Returns:
            Formatted response dict for BigRipple.
        """
        response = AgentResponse(
            success=True,
            output=output,
            entity_operations=entity_operations or [],
            tool_calls=tool_calls or [],
            tokens_used=tokens_used or {"prompt": 0, "completion": 0, "total": 0},
            duration_ms=duration_ms,
        )
        return response.to_bigripple_format()

    def format_error(
        self,
        code: str,
        message: str,
        details: Any = None,
        partial_output: Any = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        duration_ms: int = 0,
    ) -> Dict[str, Any]:
        """Format an error execution result.

        Args:
            code: Error code (e.g., "EXECUTION_ERROR", "TIMEOUT").
            message: Human-readable error message.
            details: Additional error details.
            partial_output: Any partial output before the error.
            tool_calls: List of tool calls made before error.
            tokens_used: Token usage statistics.
            duration_ms: Execution duration in milliseconds.

        Returns:
            Formatted error response dict for BigRipple.
        """
        response = AgentResponse(
            success=False,
            output=partial_output,
            entity_operations=[],
            tool_calls=tool_calls or [],
            tokens_used=tokens_used or {"prompt": 0, "completion": 0, "total": 0},
            duration_ms=duration_ms,
            error={
                "code": code,
                "message": message,
                "details": details,
            },
        )
        return response.to_bigripple_format()

    def format_tool_call(
        self,
        call_id: str,
        name: str,
        arguments: Any,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format a single tool call for the response.

        Args:
            call_id: The tool call ID from the LLM.
            name: The function name called.
            arguments: The arguments passed to the tool.
            result: The result returned by the tool.

        Returns:
            Formatted tool call dict.
        """
        return {
            "id": call_id,
            "name": name,
            "arguments": arguments if isinstance(arguments, str) else str(arguments),
            "result": result,
        }

    def merge_token_usage(
        self,
        usages: List[Dict[str, int]],
    ) -> Dict[str, int]:
        """Merge multiple token usage dicts into one.

        Args:
            usages: List of token usage dicts.

        Returns:
            Combined token usage dict.
        """
        total = {"prompt": 0, "completion": 0, "total": 0}
        for usage in usages:
            if isinstance(usage, dict):
                total["prompt"] += usage.get("prompt", 0)
                total["completion"] += usage.get("completion", 0)
                total["total"] += usage.get("total", 0)
        return total
