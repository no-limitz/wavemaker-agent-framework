"""
BigRipple Agent wrapper around Strands SDK.

Provides context injection and operation extraction on top of Strands Agent.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from strands import Agent
from strands.models.openai import OpenAIModel

from bigripple_agent_framework.context import EntityContext, ContextInjector
from bigripple_agent_framework.operations import OperationExtractor
from bigripple_agent_framework.tools.strands_tools import ALL_TOOLS, ENTITY_TOOLS


logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from BigRipple agent execution."""

    success: bool
    output: Any
    entity_operations: list[dict] = field(default_factory=list)
    duration_ms: int = 0
    error: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary with camelCase keys for BigRipple."""
        result = {
            "success": self.success,
            "output": self.output,
            "entityOperations": self.entity_operations,
            "durationMs": self.duration_ms,
        }
        if self.error:
            result["error"] = self.error
        return result


class BigRippleAgent:
    """Agent wrapper that handles BigRipple context and operations.

    This wraps a Strands Agent with:
    - Context injection from EntityContext
    - Entity operation extraction from tool results
    - Standardized response format for BigRipple

    Example:
        ```python
        agent = BigRippleAgent(
            system_prompt="You are a campaign planning assistant.",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        result = agent.run(
            prompt="Create a Q1 marketing campaign",
            context=EntityContext(userId="user_123", brandId="brand_456", ...),
        )

        print(result.entity_operations)  # List of operations to process
        ```
    """

    def __init__(
        self,
        system_prompt: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[list] = None,
        include_entity_tools: bool = True,
    ):
        """Initialize the BigRipple agent.

        Args:
            system_prompt: Base system prompt for the agent.
            api_key: OpenAI API key (or compatible). Uses OPENAI_API_KEY env var if not provided.
            base_url: Optional custom base URL (for LiteLLM proxy, etc.).
            model_id: Model to use (default: gpt-4o).
            temperature: Temperature for generation (default: 0.7).
            max_tokens: Max tokens for response (default: 4096).
            tools: List of tools to use. If None, uses default BigRipple tools.
            include_entity_tools: If True and tools is None, include entity creation tools.
        """
        self.base_system_prompt = system_prompt
        self.context_injector = ContextInjector()
        self.operation_extractor = OperationExtractor()

        # Configure model
        client_args = {}
        if api_key:
            client_args["api_key"] = api_key
        if base_url:
            client_args["base_url"] = base_url

        model = OpenAIModel(
            client_args=client_args if client_args else None,
            model_id=model_id,
            params={
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        # Select tools
        if tools is None:
            tools = ALL_TOOLS if include_entity_tools else []

        # Store for later - we'll create agent per execution with context
        self._model = model
        self._tools = tools
        self._model_id = model_id

    def run(
        self,
        prompt: str,
        context: Optional[EntityContext] = None,
        execution_id: Optional[str] = None,
    ) -> AgentResult:
        """Run the agent with the given prompt and context.

        Args:
            prompt: The user's request/prompt.
            context: Optional EntityContext from BigRipple.
            execution_id: Optional execution ID for tracking.

        Returns:
            AgentResult with output and entity operations.
        """
        start_time = time.time()

        try:
            # Build context-enhanced system prompt
            if context:
                context_str = self.context_injector.build_context_prompt(context)
                full_system_prompt = f"{self.base_system_prompt}\n\n{context_str}"
            else:
                full_system_prompt = self.base_system_prompt

            # Create agent with context-enhanced prompt
            agent = Agent(
                model=self._model,
                system_prompt=full_system_prompt,
                tools=self._tools,
                callback_handler=None,  # Disable console output
            )

            # Run agent
            logger.info(f"Running agent with prompt: {prompt[:100]}...")
            result = agent(prompt)

            # Extract message content
            output = result.message if hasattr(result, 'message') else str(result)

            # Try to parse JSON output
            if isinstance(output, str) and output.strip().startswith("{"):
                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    pass

            # Extract entity operations from output
            brand_id = context.brand_id if context else None
            cleaned_output, operations = self.operation_extractor.extract(
                agent_output=output,
                tool_results=[],  # Strands handles tool results internally
                brand_id=brand_id,
                execution_id=execution_id,
            )

            # Also extract any entity operations embedded in the response
            if isinstance(output, dict):
                for key in list(output.keys()):
                    if key == "entityOperation":
                        operations.append(output.pop(key))
                    elif key == "entityOperations":
                        operations.extend(output.pop(key))

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Agent completed: {len(operations)} operations, {duration_ms}ms")

            return AgentResult(
                success=True,
                output=cleaned_output,
                entity_operations=operations,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.exception("Agent execution failed")

            return AgentResult(
                success=False,
                output=None,
                entity_operations=[],
                duration_ms=duration_ms,
                error={"code": type(e).__name__, "message": str(e)},
            )


def create_agent(
    system_prompt: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_id: str = "gpt-4o",
    tools: Optional[list] = None,
) -> BigRippleAgent:
    """Create a BigRipple agent with default configuration.

    This is a convenience function for creating agents.

    Args:
        system_prompt: The system prompt for the agent.
        api_key: OpenAI API key.
        base_url: Optional custom base URL.
        model_id: Model to use (default: gpt-4o).
        tools: Optional list of tools.

    Returns:
        Configured BigRippleAgent.

    Example:
        ```python
        agent = create_agent(
            system_prompt="You are a campaign planning assistant.",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        result = agent.run("Create a marketing campaign", context=entity_context)
        ```
    """
    return BigRippleAgent(
        system_prompt=system_prompt,
        api_key=api_key,
        base_url=base_url,
        model_id=model_id,
        tools=tools,
    )
