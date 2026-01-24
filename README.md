# Wavemaker Agent Framework

A framework for building AgentField-compatible AI agents with **reduced code duplication** across hundreds of agents.

## Why This Framework?

When building 100+ agents, you would duplicate **60-70% of boilerplate code** across every agent. This framework eliminates that duplication by extracting common patterns into reusable utilities.

### Impact

| Metric | Without Framework | With Framework | Savings |
|--------|------------------|----------------|---------|
| Setup time per agent | 8-12 hours | 0.5-1 hour | **90%** |
| Core development | 30-40 hours | 8-12 hours | **70%** |
| Testing setup | 8-12 hours | 1-2 hours | **85%** |
| **Total per agent** | **40-60 hours** | **10-15 hours** | **75%** |

### For 100 Agents

- **Time:** 4,000-6,000 hours → 1,500-2,000 hours (**60-75% reduction**)
- **Cost:** ~$400K-600K → ~$150K-200K (**$250K-400K savings**)
- **Lines of code:** 200K → 80K (**60% reduction**)

## Features

- **Configuration Management:** Environment variable loading with validation
- **LLM Client Factory:** OpenAI client creation with Langfuse integration
- **Response Wrappers:** Standardized success/error responses
- **Test Utilities:** Reusable pytest fixtures and OpenAI mocks
- **CLI Tools:** Agent scaffold generator (coming soon)
- **Type Safety:** Full Pydantic validation throughout

## Installation

### From Private PyPI (Production)

```bash
# Configure access to private PyPI first
pip install wavemaker-agent-framework
```

### From Source (Development)

```bash
git clone https://github.com/yourusername/wavemaker-agent-framework.git
cd wavemaker-agent-framework
pip install -e .
```

## Quick Start

### 1. Configuration

```python
from wavemaker_agent_framework.core import AgentConfig

# Load configuration from environment variables
config = AgentConfig.from_env()

# Access configuration
print(f"Using model: {config.openai_model}")
print(f"Temperature: {config.openai_temperature}")
print(f"Langfuse enabled: {config.has_langfuse}")
```

### 2. LLM Client

```python
from wavemaker_agent_framework.core import LLMClientFactory

# Create OpenAI client (automatically wraps with Langfuse if credentials available)
client = await LLMClientFactory.from_config(config)

# Use standard OpenAI client interface
response = await client.chat.completions.create(
    model=config.openai_model,
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=config.openai_temperature,
)
```

### 3. API Responses

```python
from wavemaker_agent_framework.api import (
    create_success_response,
    create_error_response,
    ErrorCodes,
)

# Success response
return create_success_response(
    data={"result": "analysis complete"},
    message="Website analyzed successfully"
)

# Error response
return create_error_response(
    error_code=ErrorCodes.VALIDATION_ERROR,
    message="Invalid URL provided",
    details={"field": "url", "issue": "Must start with http or https"},
    http_status=400
)
```

### 4. Testing

```python
# In your agent's conftest.py
from wavemaker_agent_framework.testing.fixtures import *

# All fixtures are now available
def test_my_agent(mock_openai_client, mock_env_vars):
    config = AgentConfig.from_env()
    assert config.openai_api_key == "sk-test-key-1234567890"
```

```python
# Use OpenAI mocks in tests
from wavemaker_agent_framework.testing.mocks import (
    create_mock_openai_client,
    MockOpenAIClientBuilder,
)

# Simple mock
mock_client = create_mock_openai_client(
    response_content='{"result": "success"}'
)

# Complex multi-step mock
mock_client = (MockOpenAIClientBuilder()
    .with_json_response({"step": "analysis", "status": "in_progress"})
    .with_json_response({"step": "extraction", "status": "complete"})
    .with_json_response({"result": "final output"})
    .build())
```

## Architecture

### Framework is 100% Agent-Agnostic

The framework knows **nothing** about specific agents. It provides infrastructure; agents provide domain logic.

```
wavemaker-agent-framework (this repo)
├── Generic utilities (config, LLM client, Langfuse)
├── Abstract base classes (coming soon)
├── Reusable test fixtures
└── CLI scaffold tool (coming soon)

your-agent (separate repo)
├── Imports framework utilities
└── Focuses ONLY on domain-specific logic
```

### Code Ownership

| Component | Framework | Your Agent |
|-----------|-----------|------------|
| AgentConfig | ✅ Owns | Uses |
| LLMClientFactory | ✅ Owns | Uses |
| Test fixtures | ✅ Owns | Imports |
| OpenAI mocks | ✅ Owns | Imports |
| **Domain Logic** | ❌ None | ✅ Owns |
| **Reasoners** | ❌ None | ✅ Owns |
| **Models** | Generic wrappers only | ✅ Owns |

## Environment Variables

The framework reads these environment variables:

### Required

- `OPENAI_API_KEY` - Your OpenAI API key

### Optional

**OpenAI Configuration:**
- `OPENAI_BASE_URL` - Custom OpenAI base URL (for LiteLLM)
- `OPENAI_MODEL` - LLM model to use (default: `gpt-4o-mini`)
- `OPENAI_TEMPERATURE` - Temperature for LLM calls (default: `0.3`)
- `OPENAI_MAX_TOKENS` - Max tokens per LLM call (default: `2000`)

**Langfuse Configuration (for observability):**
- `LANGFUSE_SECRET_KEY` - Langfuse secret key
- `LANGFUSE_PUBLIC_KEY` - Langfuse public key
- `LANGFUSE_HOST` - Langfuse host URL (default: `https://cloud.langfuse.com`)

**AgentField Configuration:**
- `AGENTFIELD_CONTROL_PLANE_URL` - AgentField control plane URL
- `AGENT_CALLBACK_URL` - Agent callback URL

**Server Configuration:**
- `PORT` - Server port (default: `8001`)
- `ENVIRONMENT` - Environment (`development`/`production`, default: `development`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

## API Reference

### Core Module

#### `AgentConfig`

Configuration management with Pydantic validation.

```python
from wavemaker_agent_framework.core import AgentConfig

# Load from environment
config = AgentConfig.from_env()

# Or create directly
config = AgentConfig(
    openai_api_key="sk-...",
    openai_model="gpt-4o",
    openai_temperature=0.5,
)

# Helper properties
config.has_langfuse       # bool: True if Langfuse credentials present
config.has_agentfield     # bool: True if AgentField URL present
config.is_production      # bool: True if environment == "production"
```

#### `LLMClientFactory`

Factory for creating OpenAI clients with optional Langfuse wrapping.

```python
from wavemaker_agent_framework.core import LLMClientFactory

# From config
client = await LLMClientFactory.from_config(config)

# Or with explicit parameters
client = await LLMClientFactory.create(
    api_key="sk-...",
    base_url="https://litellm.example.com",  # Optional
    enable_langfuse=True,
    langfuse_secret_key="sk-...",
    langfuse_public_key="pk-...",
)
```

### API Module

#### Response Models

```python
from wavemaker_agent_framework.api import (
    SuccessResponse,
    ErrorResponse,
    ErrorCodes,
    create_success_response,
    create_error_response,
)

# Success response
response = create_success_response(
    data={"id": "123", "status": "completed"},
    message="Operation successful"  # Optional
)

# Error response
response = create_error_response(
    error_code=ErrorCodes.VALIDATION_ERROR,
    message="Invalid input",
    details={"field": "email", "issue": "Invalid format"},  # Optional
    http_status=400
)
```

#### Error Codes

Standard error codes to use across all agents:

```python
# Client errors (4xx)
ErrorCodes.VALIDATION_ERROR
ErrorCodes.INVALID_INPUT
ErrorCodes.NOT_FOUND
ErrorCodes.UNAUTHORIZED
ErrorCodes.FORBIDDEN
ErrorCodes.RATE_LIMIT_EXCEEDED

# Server errors (5xx)
ErrorCodes.INTERNAL_ERROR
ErrorCodes.SERVICE_UNAVAILABLE
ErrorCodes.TIMEOUT
ErrorCodes.LLM_ERROR
ErrorCodes.API_ERROR
```

### Testing Module

#### Fixtures

All fixtures are available by importing from `wavemaker_agent_framework.testing.fixtures`:

```python
# In your agent's conftest.py
from wavemaker_agent_framework.testing.fixtures import *

# Available fixtures:
# - event_loop: Event loop for async tests
# - mock_aiohttp: Mock HTTP responses
# - mock_openai_client: Mock OpenAI client
# - mock_openai_response: Mock OpenAI response structure
# - mock_env_vars: Mock environment variables
# - sample_html_simple: Simple HTML for testing
# - sample_html_complex: Complex HTML with meta tags
# - sample_html_malformed: Malformed HTML for error testing
# - sample_html_minimal: Minimal HTML
```

#### OpenAI Mocks

```python
from wavemaker_agent_framework.testing.mocks import (
    create_mock_openai_client,
    create_mock_openai_error,
    MockOpenAIClientBuilder,
    mock_json_response,
)

# Simple mock client
client = create_mock_openai_client('{"result": "success"}')

# Error mock
client = create_mock_openai_error("rate_limit")  # Raises RateLimitError

# Complex multi-step mock
client = (MockOpenAIClientBuilder()
    .with_response('{"step": 1}')
    .with_response('{"step": 2}')
    .with_error("rate_limit")  # Third call raises error
    .with_response('{"step": 3}')  # Fourth call succeeds
    .build())

# JSON response formatting
plain_json = mock_json_response({"status": "ok"}, format_type="plain")
markdown_json = mock_json_response({"status": "ok"}, format_type="markdown")
mixed_json = mock_json_response({"status": "ok"}, format_type="mixed")
```

## Examples

### Complete Agent Example

```python
# your_agent/main.py
from fastapi import FastAPI
from wavemaker_agent_framework.core import AgentConfig, LLMClientFactory
from wavemaker_agent_framework.api import create_success_response, create_error_response, ErrorCodes

app = FastAPI()

# Load configuration
config = AgentConfig.from_env()

# Create LLM client
client = None

@app.on_event("startup")
async def startup():
    global client
    client = await LLMClientFactory.from_config(config)

@app.post("/analyze")
async def analyze(request: dict):
    try:
        # Your agent-specific logic here
        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=[{"role": "user", "content": request["prompt"]}],
        )

        return create_success_response(
            data={"result": response.choices[0].message.content},
            message="Analysis completed"
        )
    except Exception as e:
        return create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message=str(e),
            http_status=500
        )

@app.get("/health")
async def health():
    return create_success_response(data={"status": "healthy"})
```

### Testing Example

```python
# your_agent/tests/test_analyze.py
import pytest
from wavemaker_agent_framework.testing.mocks import MockOpenAIClientBuilder

@pytest.mark.asyncio
async def test_analyze_endpoint(fastapi_client, mock_env_vars):
    # Mock OpenAI to return specific response
    mock_client = (MockOpenAIClientBuilder()
        .with_json_response({"analysis": "complete"})
        .build())

    # Test your endpoint
    response = await fastapi_client.post("/analyze", json={"prompt": "test"})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

## Contributing

This is a proprietary framework for internal use. Contact the maintainers for contribution guidelines.

## License

Proprietary - All Rights Reserved

## Support

For issues or questions, contact:
- Email: bobby@nolimitz.com
- GitHub Issues: https://github.com/NoLimitzLab/wavemaker-agent-framework/issues

---

**Version:** 0.1.0
**Last Updated:** 2026-01-23
