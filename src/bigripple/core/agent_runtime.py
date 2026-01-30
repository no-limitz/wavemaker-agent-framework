"""
Agent runtime for executing agents with context and tools.

Provides the main execution loop that:
1. Injects entity context into the system prompt
2. Handles LLM calls with tool support
3. Executes tool calls and collects results
4. Extracts entity operations from output
5. Formats response for BigRipple
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from bigripple.context.entity_context import EntityContext
from bigripple.context.context_injector import ContextInjector
from bigripple.tools.registry import ToolRegistry
from bigripple.tools.executor import ToolExecutor
from bigripple.operations.extractor import OperationExtractor
from bigripple.operations.formatter import ResponseFormatter


logger = logging.getLogger(__name__)


class AgentExecutionInput(BaseModel):
    """Input for agent execution."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    input_data: Dict[str, Any] = Field(
        description="The input data from BigRipple (user prompt, goal, etc.)"
    )
    context: EntityContext = Field(
        description="The EntityContext from BigRipple with tenant scope and entities"
    )
    execution_id: str = Field(
        description="Unique execution ID for tracking"
    )
    system_prompt: str = Field(
        description="The base system prompt for the agent"
    )
    enabled_tools: List[str] = Field(
        default_factory=list,
        description="List of tool IDs to enable for this execution"
    )
    max_iterations: int = Field(
        default=10,
        description="Maximum tool-calling iterations before stopping"
    )
    model: str = Field(
        default="gpt-4o",
        description="LLM model to use"
    )


class AgentExecutionOutput(BaseModel):
    """Output from agent execution."""
    success: bool
    output: Any
    entity_operations: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    tokens_used: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}
    duration_ms: int
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with camelCase keys for BigRipple."""
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


class AgentRuntime:
    """Executes agents with context injection and tool calling support.

    The runtime handles the complete execution flow:
    1. Build context-enhanced system prompt
    2. Call LLM with tools
    3. Execute any tool calls
    4. Loop until final response
    5. Extract entity operations
    6. Format response for BigRipple
    """

    def __init__(
        self,
        llm_client: Any,
        tool_registry: ToolRegistry,
        context_injector: Optional[ContextInjector] = None,
        operation_extractor: Optional[OperationExtractor] = None,
        response_formatter: Optional[ResponseFormatter] = None,
    ):
        """Initialize the agent runtime.

        Args:
            llm_client: AsyncOpenAI or Langfuse-wrapped client.
            tool_registry: Registry of available tools.
            context_injector: Injector for building context prompts.
            operation_extractor: Extractor for entity operations.
            response_formatter: Formatter for response output.
        """
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.context_injector = context_injector or ContextInjector()
        self.operation_extractor = operation_extractor or OperationExtractor()
        self.response_formatter = response_formatter or ResponseFormatter()
        self.tool_executor = ToolExecutor(tool_registry)

    async def execute(self, input: AgentExecutionInput) -> AgentExecutionOutput:
        """Execute an agent with the given input and context.

        Args:
            input: The execution input with context and configuration.

        Returns:
            The execution output with result and operations.
        """
        start_time = time.time()
        total_tokens = {"prompt": 0, "completion": 0, "total": 0}
        all_tool_calls: List[Dict[str, Any]] = []

        try:
            # 1. Build context-enhanced system prompt
            context_str = self.context_injector.build_context_prompt(input.context)
            full_system_prompt = f"{input.system_prompt}\n\n{context_str}"

            logger.debug(f"Built system prompt with {len(context_str)} chars of context")

            # 2. Build initial messages
            messages = [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": self._format_user_input(input.input_data)},
            ]

            # 3. Get tools in OpenAI format
            tools = None
            if input.enabled_tools:
                tools = self.tool_registry.to_openai_tools(input.enabled_tools)
                logger.debug(f"Enabled {len(tools)} tools")

            # 4. LLM + Tool calling loop
            for iteration in range(input.max_iterations):
                logger.debug(f"Iteration {iteration + 1}/{input.max_iterations}")

                # Call LLM
                response = await self.llm_client.chat.completions.create(
                    model=input.model,
                    messages=messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                )

                # Track tokens
                if response.usage:
                    total_tokens["prompt"] += response.usage.prompt_tokens
                    total_tokens["completion"] += response.usage.completion_tokens
                    total_tokens["total"] += response.usage.total_tokens

                assistant_msg = response.choices[0].message

                # Check for tool calls
                if assistant_msg.tool_calls:
                    # Add assistant message with tool calls
                    messages.append(assistant_msg)

                    # Execute each tool call
                    for tool_call in assistant_msg.tool_calls:
                        logger.info(f"Executing tool: {tool_call.function.name}")

                        # Execute tool
                        result = await self.tool_executor.execute(
                            tool_name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                            context={
                                "execution_id": input.execution_id,
                                "tenant_context": input.context.model_dump(by_alias=True),
                            }
                        )

                        # Track tool call
                        all_tool_calls.append(
                            self.response_formatter.format_tool_call(
                                call_id=tool_call.id,
                                name=tool_call.function.name,
                                arguments=tool_call.function.arguments,
                                result=result.model_dump(by_alias=True),
                            )
                        )

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result.model_dump_json(by_alias=True),
                        })
                else:
                    # No tool calls - we have final response
                    final_output = assistant_msg.content

                    # Try to parse as JSON if it looks like JSON
                    if final_output and final_output.strip().startswith("{"):
                        try:
                            final_output = json.loads(final_output)
                        except json.JSONDecodeError:
                            pass  # Keep as string

                    # Extract entity operations
                    cleaned_output, operations = self.operation_extractor.extract(
                        agent_output=final_output,
                        tool_results=[tc.get("result", {}) for tc in all_tool_calls],
                        brand_id=input.context.brand_id,
                        execution_id=input.execution_id,
                    )

                    duration_ms = int((time.time() - start_time) * 1000)

                    logger.info(
                        f"Execution complete: {len(operations)} operations, "
                        f"{total_tokens['total']} tokens, {duration_ms}ms"
                    )

                    return AgentExecutionOutput(
                        success=True,
                        output=cleaned_output,
                        entity_operations=operations,
                        tool_calls=all_tool_calls,
                        tokens_used=total_tokens,
                        duration_ms=duration_ms,
                    )

            # Max iterations reached without final response
            duration_ms = int((time.time() - start_time) * 1000)
            logger.warning(f"Max iterations ({input.max_iterations}) reached")

            return AgentExecutionOutput(
                success=False,
                output=None,
                entity_operations=[],
                tool_calls=all_tool_calls,
                tokens_used=total_tokens,
                duration_ms=duration_ms,
                error={
                    "code": "MAX_ITERATIONS",
                    "message": f"Agent exceeded maximum tool calling iterations ({input.max_iterations})",
                },
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.exception("Execution failed")

            return AgentExecutionOutput(
                success=False,
                output=None,
                entity_operations=[],
                tool_calls=all_tool_calls,
                tokens_used=total_tokens,
                duration_ms=duration_ms,
                error={
                    "code": type(e).__name__,
                    "message": str(e),
                },
            )

    def _format_user_input(self, input_data: Dict[str, Any]) -> str:
        """Format user input for the LLM.

        If input_data has a single 'prompt' key, return just that.
        Otherwise, format as JSON.
        """
        if len(input_data) == 1 and "prompt" in input_data:
            return input_data["prompt"]
        return json.dumps(input_data, indent=2)


def create_default_runtime(
    llm_client: Any,
    include_bigripple_tools: bool = True,
) -> AgentRuntime:
    """Create a runtime with default configuration.

    Args:
        llm_client: The LLM client to use.
        include_bigripple_tools: Whether to register BigRipple tools.

    Returns:
        Configured AgentRuntime.
    """
    from bigripple.tools.bigripple import create_bigripple_registry

    if include_bigripple_tools:
        registry = create_bigripple_registry()
    else:
        registry = ToolRegistry()

    return AgentRuntime(llm_client, registry)
