"""
Unit tests for LLMClientFactory.

Tests OpenAI client creation, Langfuse wrapping, and error handling.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from openai import AsyncOpenAI
from wavemaker_agent_framework.core.client import LLMClientFactory


class TestLLMClientFactoryCreate:
    """Test LLMClientFactory.create() method."""

    @pytest.mark.asyncio
    async def test_creates_standard_client_without_langfuse(self):
        """Test creating standard OpenAI client when Langfuse disabled."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=False
        )

        assert isinstance(client, AsyncOpenAI)
        assert client.api_key == "sk-test-key"

    @pytest.mark.asyncio
    async def test_creates_standard_client_missing_langfuse_credentials(self):
        """Test creating standard client when Langfuse credentials missing."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=True,
            # Missing langfuse_secret_key and langfuse_public_key
        )

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_custom_base_url(self):
        """Test creating client with custom base URL (LiteLLM)."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            base_url="https://litellm.example.com",
            enable_langfuse=False
        )

        assert isinstance(client, AsyncOpenAI)
        assert str(client.base_url) == "https://litellm.example.com/"

    @pytest.mark.asyncio
    async def test_creates_langfuse_wrapped_client(self):
        """Test creating Langfuse-wrapped client with credentials."""
        with patch("wavemaker_agent_framework.core.client.openai") as mock_openai_module:
            # Mock the Langfuse class
            mock_langfuse_class = MagicMock()
            mock_langfuse_instance = MagicMock()
            mock_langfuse_class.return_value = mock_langfuse_instance
            mock_openai_module.Langfuse = mock_langfuse_class

            client = await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse",
                langfuse_host="https://cloud.langfuse.com"
            )

            # Verify Langfuse was initialized with correct params
            mock_langfuse_class.assert_called_once_with(
                secret_key="sk-langfuse",
                public_key="pk-langfuse",
                host="https://cloud.langfuse.com"
            )

    @pytest.mark.asyncio
    async def test_logs_langfuse_initialization(self, caplog):
        """Test that Langfuse initialization is logged."""
        with patch("wavemaker_agent_framework.core.client.openai") as mock_openai_module:
            mock_langfuse_class = MagicMock()
            mock_openai_module.Langfuse = mock_langfuse_class

            await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse"
            )

            assert "Langfuse observability enabled" in caplog.text

    @pytest.mark.asyncio
    async def test_logs_standard_client_creation(self, caplog):
        """Test that standard client creation is logged."""
        await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=False
        )

        assert "Creating standard OpenAI client" in caplog.text


class TestLLMClientFactoryFromConfig:
    """Test LLMClientFactory.from_config() method."""

    @pytest.mark.asyncio
    async def test_creates_client_from_config(self, mock_env_vars):
        """Test creating client from AgentConfig object."""
        from wavemaker_agent_framework.core.config import AgentConfig

        config = AgentConfig.from_env()
        client = await LLMClientFactory.from_config(config)

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_uses_config_base_url(self, mock_env_vars, monkeypatch):
        """Test that custom base URL from config is used."""
        from wavemaker_agent_framework.core.config import AgentConfig

        monkeypatch.setenv("OPENAI_BASE_URL", "https://litellm.example.com")
        config = AgentConfig.from_env()

        client = await LLMClientFactory.from_config(config)

        assert isinstance(client, AsyncOpenAI)
        assert str(client.base_url) == "https://litellm.example.com/"

    @pytest.mark.asyncio
    async def test_enables_langfuse_from_config(self, mock_env_vars):
        """Test that Langfuse is enabled when config has credentials."""
        from wavemaker_agent_framework.core.config import AgentConfig

        config = AgentConfig.from_env()

        with patch("wavemaker_agent_framework.core.client.openai") as mock_openai_module:
            mock_langfuse_class = MagicMock()
            mock_openai_module.Langfuse = mock_langfuse_class

            await LLMClientFactory.from_config(config)

            # Verify Langfuse was initialized
            assert mock_langfuse_class.called


class TestLLMClientFactoryErrorHandling:
    """Test error handling in LLMClientFactory."""

    @pytest.mark.asyncio
    async def test_handles_invalid_api_key_format(self):
        """Test handling of invalid API key format."""
        # OpenAI client should still be created - validation happens at API call time
        client = await LLMClientFactory.create(api_key="invalid-key")

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_handles_invalid_base_url(self):
        """Test handling of invalid base URL."""
        # OpenAI client validates base URL format
        with pytest.raises(Exception):  # OpenAI will raise validation error
            await LLMClientFactory.create(
                api_key="sk-test-key",
                base_url="not-a-valid-url"
            )

    @pytest.mark.asyncio
    async def test_handles_langfuse_import_error(self, caplog):
        """Test handling when Langfuse library not available."""
        with patch("wavemaker_agent_framework.core.client.openai") as mock_openai_module:
            # Simulate Langfuse not being available
            mock_openai_module.Langfuse = None

            client = await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse"
            )

            # Should fall back to standard client
            assert isinstance(client, AsyncOpenAI)
            assert "Langfuse not available" in caplog.text


class TestLLMClientUsage:
    """Test that created clients work correctly."""

    @pytest.mark.asyncio
    async def test_client_can_make_api_calls(self, mock_openai_client):
        """Test that created client can make API calls."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=False
        )

        # This will be mocked by mock_openai_client fixture
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}]
        )

        assert response.choices[0].message.content == '{"result": "test response"}'

    @pytest.mark.asyncio
    async def test_client_respects_model_setting(self):
        """Test that client can use different models."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=False
        )

        # Client should accept any model parameter
        assert hasattr(client.chat.completions, "create")


class TestLLMClientFactoryIntegration:
    """Integration tests combining config and client creation."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_config(self, mock_env_vars):
        """Test complete workflow: env vars -> config -> client."""
        from wavemaker_agent_framework.core.config import AgentConfig

        # Load config from environment
        config = AgentConfig.from_env()

        # Create client from config
        client = await LLMClientFactory.from_config(config)

        # Verify client is ready to use
        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_full_workflow_with_custom_settings(self, mock_env_vars, monkeypatch):
        """Test workflow with custom settings."""
        from wavemaker_agent_framework.core.config import AgentConfig

        # Set custom settings
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://litellm.example.com")

        config = AgentConfig.from_env()
        client = await LLMClientFactory.from_config(config)

        assert isinstance(client, AsyncOpenAI)
        assert str(client.base_url) == "https://litellm.example.com/"
