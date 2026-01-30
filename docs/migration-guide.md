# Migration Guide: Integrating with BigRipple

This guide walks through migrating existing agents to use the wavemaker-agent-framework for BigRipple integration.

## Overview

The wavemaker-agent-framework provides:
- **Entity Context**: Structured data about brands, campaigns, and content from BigRipple
- **Tool Registry**: Pre-built BigRipple tools for creating/updating entities
- **Operation Extraction**: Automatic extraction of entity operations from agent output
- **Response Formatting**: BigRipple-compatible response format

## Migration Steps

### Step 1: Install the Framework

```bash
pip install wavemaker-agent-framework
# or with uv
uv add wavemaker-agent-framework
```

### Step 2: Update Your Agent Runtime

#### Before (Direct OpenAI calls)

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
)

output = response.choices[0].message.content
```

#### After (Using AgentRuntime)

```python
from openai import AsyncOpenAI
from wavemaker_agent_framework.core import create_default_runtime, AgentExecutionInput
from wavemaker_agent_framework.context import EntityContext

client = AsyncOpenAI()
runtime = create_default_runtime(client, include_bigripple_tools=True)

# Context comes from BigRipple
context = EntityContext(**bigripple_context_data)

result = await runtime.execute(AgentExecutionInput(
    input_data={"prompt": user_prompt},
    context=context,
    execution_id="exec_123",
    system_prompt=system_prompt,
    enabled_tools=["bigripple.campaign.create", "bigripple.content.create"],
))

output = result.output
entity_operations = result.entity_operations
```

### Step 3: Handle Entity Context

BigRipple sends entity context in camelCase JSON. The framework handles conversion automatically.

#### Receiving Context from BigRipple

```python
# BigRipple sends this JSON payload:
bigripple_payload = {
    "userId": "user_123",
    "brandId": "brand_456",
    "brands": [{"id": "brand_456", "name": "TechCorp"}],
    "brandVoice": {"tone": "professional", "style": "informative"},
    "campaigns": [],
    "recentContent": [],
    "retrievalContext": {
        "results": [{"content": "RAG content here", "metadata": {}}]
    }
}

# Convert to EntityContext
from wavemaker_agent_framework.context import EntityContext

context = EntityContext(**bigripple_payload)

# Access with snake_case
print(context.user_id)  # "user_123"
print(context.brand_voice.tone)  # "professional"
```

### Step 4: Replace Custom Tool Handling

#### Before (Custom tool implementation)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_campaign",
            "description": "Create a campaign",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "channels": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "channels"],
            },
        },
    }
]

# Manual tool execution
if tool_call.function.name == "create_campaign":
    # Custom handling...
    pass
```

#### After (Using ToolRegistry)

```python
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry

registry = create_bigripple_registry()

# Get OpenAI-formatted tools
tools = registry.to_openai_tools(enabled_tools=["bigripple.campaign.create"])

# AgentRuntime handles tool execution automatically
```

### Step 5: Extract Entity Operations

The framework automatically extracts entity operations from:
1. Tool call results
2. Explicit `entityOperations` in output
3. Inferred operations from output structure

#### Before (Manual extraction)

```python
# Manually parsing output for entities to create
if "campaigns" in output:
    for campaign in output["campaigns"]:
        if campaign.get("createInSystem"):
            # Send to BigRipple...
            pass
```

#### After (Using OperationExtractor)

```python
from wavemaker_agent_framework.operations import OperationExtractor

extractor = OperationExtractor()
cleaned_output, operations = extractor.extract(
    output=agent_output,
    tool_results=tool_results,
    brand_id=context.brand_id,
)

# Operations are ready for BigRipple
for op in operations:
    print(op["type"])  # "create_campaign"
    print(op["brandId"])  # "brand_456"
    print(op["data"])  # {"name": "...", "channels": [...]}
```

### Step 6: Format Response for BigRipple

```python
from wavemaker_agent_framework.operations import ResponseFormatter

formatter = ResponseFormatter()
response = formatter.format(
    output=cleaned_output,
    operations=operations,
    execution_id="exec_123",
)

# Send response back to BigRipple
# response = {
#     "success": True,
#     "output": {...},
#     "entityOperations": [...],
#     "executionId": "exec_123",
# }
```

## Entity Operation Types

The framework supports these BigRipple operation types:

| Operation | Description | Required Data |
|-----------|-------------|---------------|
| `create_campaign` | Create new campaign | name, channels |
| `update_campaign` | Update campaign | entityId, update fields |
| `create_content` | Create content | type, channel, body |
| `update_content` | Update content | entityId, update fields |
| `create_brand` | Create brand | name, industry |

### Operation Data Schemas

#### create_campaign

```python
{
    "type": "create_campaign",
    "brandId": "brand_123",
    "data": {
        "name": "Campaign Name",
        "channels": ["linkedin", "twitter"],
        "description": "Optional description",
        "goal": "Optional goal",
        "status": "DRAFT",  # DRAFT, ACTIVE, PAUSED, COMPLETED
    }
}
```

#### create_content

```python
{
    "type": "create_content",
    "brandId": "brand_123",
    "data": {
        "type": "SOCIAL_POST",  # SOCIAL_POST, BLOG_POST, EMAIL, etc.
        "channel": "linkedin",
        "body": "Content body",
        "title": "Optional title",
        "campaignId": "optional_campaign_id",
    }
}
```

## Testing Your Migration

### Using Mock Clients

```python
from wavemaker_agent_framework.testing.mocks import (
    create_mock_llm_client,
    create_mock_tool_call,
    MockBigRippleClient,
)
from wavemaker_agent_framework.testing.fixtures import sample_entity_context

# Create mock LLM
tool_call = create_mock_tool_call(
    call_id="call_1",
    name="create_campaign",
    arguments={"brand_id": "123", "name": "Test", "channels": ["linkedin"]},
)
mock_llm = create_mock_llm_client([
    {"content": None, "tool_calls": [tool_call]},
    {"content": "Done!", "tool_calls": None},
])

# Create mock BigRipple client
bigripple = MockBigRippleClient()

# Test execution
context = sample_entity_context()
# ... run your agent ...

# Verify operations
assert len(bigripple.created_campaigns) == 1
```

### Integration Test Example

```python
import pytest
from wavemaker_agent_framework.core import AgentRuntime, AgentExecutionInput
from wavemaker_agent_framework.tools.bigripple import create_bigripple_registry
from wavemaker_agent_framework.testing.mocks import create_mock_llm_client
from wavemaker_agent_framework.testing.fixtures import sample_entity_context

@pytest.mark.asyncio
async def test_campaign_creation():
    mock_llm = create_mock_llm_client([
        {"content": "I'll create a campaign for you.", "tool_calls": None}
    ])

    registry = create_bigripple_registry()
    runtime = AgentRuntime(mock_llm, registry)

    result = await runtime.execute(AgentExecutionInput(
        input_data={"prompt": "Create a test campaign"},
        context=sample_entity_context(),
        execution_id="test_001",
        system_prompt="You are a test agent.",
        enabled_tools=["bigripple.campaign.create"],
    ))

    assert result.success is True
```

## Common Migration Issues

### Issue: Context field names don't match

**Problem**: Your code uses different field names than BigRipple.

**Solution**: Use the EntityContext model which handles camelCase/snake_case conversion:

```python
# Both work:
context = EntityContext(userId="123")  # camelCase input
context = EntityContext(user_id="123")  # snake_case input

# Access is always snake_case:
print(context.user_id)
```

### Issue: Tool results not creating operations

**Problem**: Tool calls succeed but no entity operations are extracted.

**Solution**: Ensure your tool handlers return `entity_operation` in the result:

```python
async def my_tool_handler(brand_id, name, channels, context):
    return {
        "success": True,
        "data": {"id": "new_123"},
        "entity_operation": {
            "type": "create_campaign",
            "brandId": brand_id,
            "data": {"name": name, "channels": channels},
        },
    }
```

### Issue: Agent not using provided context

**Problem**: Agent responses don't reflect brand voice or context.

**Solution**: The ContextInjector builds context into the system prompt. Ensure you're using the runtime:

```python
# This automatically injects context into the prompt
result = await runtime.execute(AgentExecutionInput(
    context=context,  # This gets injected
    # ...
))
```

### Issue: Token usage not tracked

**Problem**: `result.tokens_used` is always zero.

**Solution**: Ensure your LLM client returns usage information:

```python
# OpenAI clients return this automatically
# For custom clients, ensure the response includes:
response.usage.prompt_tokens
response.usage.completion_tokens
response.usage.total_tokens
```

## Next Steps

1. Review the [API Reference](./api-reference.md) for detailed documentation
2. Check the [examples/](../examples/) directory for complete agent implementations
3. Run the test suite to verify your integration:
   ```bash
   pytest tests/ -v
   ```
