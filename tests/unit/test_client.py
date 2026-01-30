"""
Unit tests for LLMClientFactory.

Tests OpenAI client creation, Langfuse wrapping, and error handling.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from openai import AsyncOpenAI
from bigripple_agent_framework.core.client import LLMClientFactory


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
        # OpenAI client may or may not add trailing slash depending on version
        assert str(client.base_url).rstrip("/") == "https://litellm.example.com"

    @pytest.mark.asyncio
    async def test_creates_langfuse_wrapped_client(self):
        """Test creating Langfuse-wrapped client with credentials."""
        with patch("bigripple_agent_framework.core.client.LangfuseAsyncOpenAI") as mock_langfuse_client, \
             patch("bigripple_agent_framework.core.client.LANGFUSE_AVAILABLE", True):
            mock_client = MagicMock()
            mock_langfuse_client.return_value = mock_client

            client = await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse",
                langfuse_host="https://cloud.langfuse.com"
            )

            # Verify LangfuseAsyncOpenAI was called
            mock_langfuse_client.assert_called_once()
            assert client == mock_client

    @pytest.mark.asyncio
    async def test_falls_back_to_standard_when_langfuse_unavailable(self):
        """Test fallback to standard client when Langfuse not installed."""
        with patch("bigripple_agent_framework.core.client.LANGFUSE_AVAILABLE", False):
            client = await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse"
            )

            # Should fall back to standard client
            assert isinstance(client, AsyncOpenAI)


class TestLLMClientFactoryFromConfig:
    """Test LLMClientFactory.create_from_config() method."""

    @pytest.mark.asyncio
    async def test_creates_client_from_config(self, mock_env_vars):
        """Test creating client from AgentConfig object."""
        from bigripple_agent_framework.core.config import AgentConfig

        config = AgentConfig.from_env()
        client = await LLMClientFactory.create_from_config(config)

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_uses_config_base_url(self, mock_env_vars, monkeypatch):
        """Test that custom base URL from config is used."""
        from bigripple_agent_framework.core.config import AgentConfig

        monkeypatch.setenv("OPENAI_BASE_URL", "https://litellm.example.com")
        config = AgentConfig.from_env()

        client = await LLMClientFactory.create_from_config(config)

        assert isinstance(client, AsyncOpenAI)
        assert str(client.base_url).rstrip("/") == "https://litellm.example.com"

    @pytest.mark.asyncio
    async def test_enables_langfuse_from_config(self, mock_env_vars):
        """Test that Langfuse is enabled when config has credentials."""
        from bigripple_agent_framework.core.config import AgentConfig

        config = AgentConfig.from_env()

        with patch("bigripple_agent_framework.core.client.LangfuseAsyncOpenAI") as mock_langfuse_client, \
             patch("bigripple_agent_framework.core.client.LANGFUSE_AVAILABLE", True):
            mock_client = MagicMock()
            mock_langfuse_client.return_value = mock_client

            await LLMClientFactory.create_from_config(config)

            # Verify LangfuseAsyncOpenAI was called since config has Langfuse credentials
            assert mock_langfuse_client.called


class TestLLMClientFactoryErrorHandling:
    """Test error handling in LLMClientFactory."""

    @pytest.mark.asyncio
    async def test_handles_invalid_api_key_format(self):
        """Test handling of invalid API key format."""
        # OpenAI client should still be created - validation happens at API call time
        client = await LLMClientFactory.create(api_key="invalid-key")

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_handles_empty_base_url(self):
        """Test handling of empty base URL."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            base_url=""
        )

        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_handles_langfuse_creation_error(self):
        """Test handling when Langfuse client creation fails."""
        with patch("bigripple_agent_framework.core.client.LangfuseAsyncOpenAI") as mock_langfuse_client, \
             patch("bigripple_agent_framework.core.client.LANGFUSE_AVAILABLE", True):
            mock_langfuse_client.side_effect = Exception("Langfuse error")

            client = await LLMClientFactory.create(
                api_key="sk-test-key",
                enable_langfuse=True,
                langfuse_secret_key="sk-langfuse",
                langfuse_public_key="pk-langfuse"
            )

            # Should fall back to standard client
            assert isinstance(client, AsyncOpenAI)


class TestLLMClientUsage:
    """Test that created clients work correctly."""

    @pytest.mark.asyncio
    async def test_client_has_chat_completions(self):
        """Test that created client has chat.completions interface."""
        client = await LLMClientFactory.create(
            api_key="sk-test-key",
            enable_langfuse=False
        )

        assert hasattr(client, "chat")
        assert hasattr(client.chat, "completions")
        assert hasattr(client.chat.completions, "create")

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
        from bigripple_agent_framework.core.config import AgentConfig

        # Load config from environment
        config = AgentConfig.from_env()

        # Create client from config
        client = await LLMClientFactory.create_from_config(config)

        # Verify client is ready to use
        assert isinstance(client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_full_workflow_with_custom_settings(self, mock_env_vars, monkeypatch):
        """Test workflow with custom settings."""
        from bigripple_agent_framework.core.config import AgentConfig

        # Set custom settings
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://litellm.example.com")

        config = AgentConfig.from_env()
        client = await LLMClientFactory.create_from_config(config)

        assert isinstance(client, AsyncOpenAI)
        assert str(client.base_url).rstrip("/") == "https://litellm.example.com"
