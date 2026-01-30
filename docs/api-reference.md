# Wavemaker Agent Framework API Reference

This document provides comprehensive API documentation for the Wavemaker Agent Framework, designed for building BigRipple-compatible AI agents.

## Table of Contents

- [Core Module](#core-module)
- [Context Module](#context-module)
- [Tools Module](#tools-module)
- [Operations Module](#operations-module)
- [Testing Utilities](#testing-utilities)

---

## Core Module

### AgentRuntime

The main execution runtime for running agents with tool calling support.

```python
from wavemaker_agent_framework.core import AgentRuntime, AgentExecutionInput, AgentExecutionResult
```

#### Constructor

```python
AgentRuntime(
    llm_client: Any,
    tool_registry: Optional[ToolRegistry] = None,
    context_injector: Optional[ContextInjector] = None,
    operation_extractor: Optional[OperationExtractor] = None,
    max_iterations: int = 10,
)
```

**Parameters:**
- `llm_client`: OpenAI-compatible client for LLM calls
- `tool_registry`: Registry of available tools (optional)
- `context_injector`: Injector for entity context (optional, created if not provided)
- `operation_extractor`: Extractor for entity operations (optional, created if not provided)
- `max_iterations`: Maximum tool calling iterations (default: 10)

#### Methods

##### `execute(input_data: AgentExecutionInput) -> AgentExecutionResult`

Execute an agent with the given input.

```python
result = await runtime.execute(AgentExecutionInput(
    input_data={"prompt": "Create a marketing campaign"},
    context=entity_context,
    execution_id="exec_123",
    system_prompt="You are a marketing assistant.",
    enabled_tools=["bigripple.campaign.create"],
))
```

### AgentExecutionInput

Input configuration for agent execution.

```python
from wavemaker_agent_framework.core import AgentExecutionInput
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `input_data` | `Dict[str, Any]` | User input data containing prompt |
| `context` | `EntityContext` | Entity context from BigRipple |
| `execution_id` | `str` | Unique execution identifier |
| `system_prompt` | `str` | System prompt for the agent |
| `enabled_tools` | `List[str]` | List of enabled tool names (optional) |
| `model` | `str` | LLM model to use (default: "gpt-4o") |
| `temperature` | `float` | Temperature for generation (default: 0.7) |

### AgentExecutionResult

Result from agent execution.

```python
from wavemaker_agent_framework.core import AgentExecutionResult
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether execution succeeded |
| `output` | `Any` | Agent output (text or structured) |
| `entity_operations` | `List[Dict]` | Extracted entity operations |
| `tool_calls` | `List[Dict]` | Tool calls made during execution |
| `tokens_used` | `Dict[str, int]` | Token usage (prompt, completion, total) |
| `duration_ms` | `int` | Execution duration in milliseconds |
| `error` | `Optional[Dict]` | Error details if failed |

### create_default_runtime

Factory function to create a runtime with BigRipple tools.

```python
from wavemaker_agent_framework.core import create_default_runtime

runtime = create_default_runtime(
    llm_client=openai_client,
    include_bigripple_tools=True,
)
```

---

## Context Module

### EntityContext

Pydantic model representing BigRipple entity context.

```python
from wavemaker_agent_framework.context import EntityContext
```

**Fields:**
| Field | Type | Alias | Description |
|-------|------|-------|-------------|
| `user_id` | `str` | `userId` | Current user ID |
| `brand_id` | `Optional[str]` | `brandId` | Active brand ID |
| `organization_id` | `Optional[str]` | `organizationId` | Organization ID |
| `brands` | `List[BrandSummary]` | `brands` | Available brands |
| `brand_voice` | `Optional[BrandVoice]` | `brandVoice` | Brand voice guidelines |
| `campaigns` | `List[CampaignSummary]` | `campaigns` | Active campaigns |
| `recent_content` | `List[ContentSummary]` | `recentContent` | Recent content items |
| `retrieval_context` | `Optional[RetrievalContext]` | `retrievalContext` | RAG context |

**Example:**
```python
context = EntityContext(
    userId="user_123",
    brandId="brand_456",
    brands=[BrandSummary(id="brand_456", name="TechCorp", industry="Technology")],
    brandVoice=BrandVoice(tone="professional", style="informative"),
)
```

### BrandSummary

Summary of a brand entity.

```python
from wavemaker_agent_framework.context import BrandSummary
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Brand identifier |
| `name` | `str` | Brand name |
| `industry` | `Optional[str]` | Industry category |
| `description` | `Optional[str]` | Brand description |

### BrandVoice

Brand voice and style guidelines.

```python
from wavemaker_agent_framework.context import BrandVoice
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `tone` | `str` | Voice tone (e.g., "professional", "casual") |
| `style` | `Optional[str]` | Writing style |
| `vocabulary` | `Optional[List[str]]` | Preferred vocabulary |
| `avoid` | `Optional[List[str]]` | Terms to avoid |
| `examples` | `Optional[List[str]]` | Example content |

### CampaignSummary

Summary of an active campaign.

```python
from wavemaker_agent_framework.context import CampaignSummary
```

**Fields:**
| Field | Type | Alias | Description |
|-------|------|-------|-------------|
| `id` | `str` | - | Campaign identifier |
| `name` | `str` | - | Campaign name |
| `status` | `str` | - | Campaign status |
| `channels` | `List[str]` | - | Target channels |
| `start_date` | `Optional[str]` | `startDate` | Start date |
| `end_date` | `Optional[str]` | `endDate` | End date |

### ContextInjector

Builds context prompts for LLM injection.

```python
from wavemaker_agent_framework.context import ContextInjector

injector = ContextInjector()
prompt = injector.build_context_prompt(entity_context)
```

#### Methods

##### `build_context_prompt(context: EntityContext) -> str`

Build a complete context prompt from entity context.

##### `build_brand_section(brands: List[BrandSummary]) -> str`

Build the brands section of the context prompt.

##### `build_voice_section(voice: BrandVoice) -> str`

Build the brand voice section.

##### `build_campaigns_section(campaigns: List[CampaignSummary]) -> str`

Build the campaigns section.

---

## Tools Module

### ToolDefinition

Definition of an agent tool.

```python
from wavemaker_agent_framework.tools import ToolDefinition, ToolParameter, ToolCategory
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique tool identifier |
| `description` | `str` | Tool description |
| `parameters` | `List[ToolParameter]` | Tool parameters |
| `handler` | `Callable` | Async function to execute |
| `category` | `ToolCategory` | Tool category |
| `requires_confirmation` | `bool` | Requires user confirmation |

### ToolParameter

Parameter definition for a tool.

```python
from wavemaker_agent_framework.tools import ToolParameter
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Parameter name |
| `type` | `str` | Parameter type (string, number, array, etc.) |
| `description` | `str` | Parameter description |
| `required` | `bool` | Whether parameter is required |
| `default` | `Optional[Any]` | Default value |
| `enum` | `Optional[List[str]]` | Allowed values |

### ToolRegistry

Registry for managing tools.

```python
from wavemaker_agent_framework.tools import ToolRegistry

registry = ToolRegistry()
registry.register(tool_definition)
```

#### Methods

##### `register(tool: ToolDefinition) -> None`

Register a tool definition.

##### `get(name: str) -> Optional[ToolDefinition]`

Get a tool by name.

##### `list_tools(category: Optional[ToolCategory] = None) -> List[ToolDefinition]`

List all tools, optionally filtered by category.

##### `to_openai_tools(enabled_tools: Optional[List[str]] = None) -> List[Dict]`

Convert tools to OpenAI function calling format.

```python
tools = registry.to_openai_tools(enabled_tools=["bigripple.campaign.create"])
# Returns: [{"type": "function", "function": {...}}]
```

##### `__contains__(name: str) -> bool`

Check if a tool is registered.

```python
if "bigripple.campaign.create" in registry:
    print("Tool available")
```

### ToolExecutor

Executes tools from the registry.

```python
from wavemaker_agent_framework.tools import ToolExecutor

executor = ToolExecutor(registry)
result = await executor.execute(
    tool_name="create_campaign",
    arguments={"brand_id": "123", "name": "My Campaign", "channels": ["linkedin"]},
    context={"execution_id": "exec_123"},
)
```

### ToolResult

Result from tool execution.

```python
from wavemaker_agent_framework.tools import ToolResult
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether execution succeeded |
| `data` | `Optional[Any]` | Result data |
| `error` | `Optional[Dict]` | Error details |
| `entity_operation` | `Optional[Dict]` | Generated entity operation |

### BigRipple Tools

Pre-built tools for BigRipple integration.

```python
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry

registry = create_bigripple_registry()
```

**Available Tools:**

| Tool Name | Description |
|-----------|-------------|
| `bigripple.campaign.create` | Create a new campaign |
| `bigripple.campaign.update` | Update an existing campaign |
| `bigripple.content.create` | Create new content |
| `bigripple.content.update` | Update existing content |
| `bigripple.brand.create` | Create a new brand |
| `bigripple.knowledge.search` | Search knowledge base |
| `bigripple.knowledge.guidelines` | Get brand guidelines |

---

## Operations Module

### EntityOperation

Pydantic model for entity operations.

```python
from wavemaker_agent_framework.operations import EntityOperation, OperationType
```

**Fields:**
| Field | Type | Alias | Description |
|-------|------|-------|-------------|
| `type` | `OperationType` | - | Operation type |
| `brand_id` | `str` | `brandId` | Target brand ID |
| `data` | `Dict[str, Any]` | - | Operation data |
| `entity_id` | `Optional[str]` | `entityId` | Entity ID for updates |

### OperationType

Enum of supported operation types.

```python
from wavemaker_agent_framework.operations import OperationType

OperationType.CREATE_CAMPAIGN
OperationType.UPDATE_CAMPAIGN
OperationType.CREATE_CONTENT
OperationType.UPDATE_CONTENT
OperationType.CREATE_BRAND
```

### OperationExtractor

Extracts entity operations from agent output.

```python
from wavemaker_agent_framework.operations import OperationExtractor

extractor = OperationExtractor()
cleaned_output, operations = extractor.extract(
    output=agent_output,
    tool_results=tool_results,
    brand_id="brand_123",
)
```

#### Methods

##### `extract(output, tool_results=None, brand_id=None) -> Tuple[Dict, List[Dict]]`

Extract operations from output and tool results.

**Returns:**
- `cleaned_output`: Output with entityOperations removed
- `operations`: List of extracted entity operations

### ResponseFormatter

Formats agent responses for BigRipple.

```python
from wavemaker_agent_framework.operations import ResponseFormatter

formatter = ResponseFormatter()
response = formatter.format(
    output=cleaned_output,
    operations=operations,
    execution_id="exec_123",
)
```

---

## Testing Utilities

### MockBigRippleClient

Mock client for BigRipple API.

```python
from wavemaker_agent_framework.testing.mocks import MockBigRippleClient

client = MockBigRippleClient()
result = await client.process_operation(operation)

# Access created entities
print(client.created_campaigns)
print(client.created_contents)
print(client.created_brands)
```

### MockAgentFieldClient

Mock client for AgentField API.

```python
from wavemaker_agent_framework.testing.mocks import MockAgentFieldClient

client = MockAgentFieldClient()
result = await client.execute_capability(
    capability_id="cap_123",
    input_data={"prompt": "Test"},
    context=entity_context,
)
```

### create_mock_llm_client

Create a mock LLM client with predefined responses.

```python
from wavemaker_agent_framework.testing.mocks import create_mock_llm_client, create_mock_tool_call

# Simple text response
mock_llm = create_mock_llm_client([
    {"content": "Hello!", "tool_calls": None}
])

# Tool calling sequence
tool_call = create_mock_tool_call(
    call_id="call_1",
    name="create_campaign",
    arguments={"brand_id": "123", "name": "Test", "channels": ["linkedin"]},
)
mock_llm = create_mock_llm_client([
    {"content": None, "tool_calls": [tool_call]},
    {"content": "Campaign created!", "tool_calls": None},
])
```

### Context Fixtures

Pre-built fixtures for testing.

```python
from wavemaker_agent_framework.testing.fixtures import (
    sample_entity_context,
    sample_brand_voice,
    sample_entity_context_json,
    sample_execution_request_json,
)

# Create sample context
context = sample_entity_context()

# Get raw JSON (as BigRipple sends it)
json_data = sample_entity_context_json()
```

### Pytest Fixtures

```python
import pytest
from wavemaker_agent_framework.testing.fixtures import entity_context_fixture

# Use in tests
def test_something(entity_context_fixture):
    context = entity_context_fixture
    # ... test code
```

---

## Usage Examples

### Basic Agent Execution

```python
import asyncio
from openai import AsyncOpenAI
from wavemaker_agent_framework.core import create_default_runtime, AgentExecutionInput
from wavemaker_agent_framework.context import EntityContext

async def main():
    # Create OpenAI client
    client = AsyncOpenAI()

    # Create runtime with BigRipple tools
    runtime = create_default_runtime(client, include_bigripple_tools=True)

    # Create context (normally from BigRipple)
    context = EntityContext(
        userId="user_123",
        brandId="brand_456",
        brands=[],
    )

    # Execute agent
    result = await runtime.execute(AgentExecutionInput(
        input_data={"prompt": "Create a Q2 marketing campaign"},
        context=context,
        execution_id="exec_001",
        system_prompt="You are a marketing campaign planner.",
        enabled_tools=["bigripple.campaign.create", "bigripple.content.create"],
    ))

    if result.success:
        print(f"Output: {result.output}")
        print(f"Operations: {result.entity_operations}")
    else:
        print(f"Error: {result.error}")

asyncio.run(main())
```

### Custom Tool Registration

```python
from wavemaker_agent_framework.tools import ToolDefinition, ToolParameter, ToolCategory, ToolRegistry

async def my_custom_handler(brand_id: str, data: dict, context: dict) -> dict:
    return {
        "success": True,
        "data": {"processed": True},
    }

custom_tool = ToolDefinition(
    name="myapp.custom.process",
    description="Process data for a brand",
    parameters=[
        ToolParameter(name="brand_id", type="string", description="Brand ID", required=True),
        ToolParameter(name="data", type="object", description="Data to process", required=True),
    ],
    handler=my_custom_handler,
    category=ToolCategory.DATA,
)

registry = ToolRegistry()
registry.register(custom_tool)
```

### Processing Entity Operations

```python
from wavemaker_agent_framework.operations import OperationExtractor

extractor = OperationExtractor()

# Extract from agent output
agent_output = {
    "summary": "Created campaign",
    "entityOperations": [
        {"type": "create_campaign", "brandId": "123", "data": {"name": "Test"}}
    ]
}

cleaned, operations = extractor.extract(agent_output)
# cleaned = {"summary": "Created campaign"}
# operations = [{"type": "create_campaign", ...}]
```
