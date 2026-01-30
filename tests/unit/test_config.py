"""
Unit tests for AgentConfig configuration management.

Tests environment variable loading, validation, and helper properties.
"""

import pytest
from pydantic import ValidationError
from bigripple_agent_framework.core.config import AgentConfig


class TestAgentConfigFromEnv:
    """Test AgentConfig.from_env() method."""

    def test_loads_all_environment_variables(self, mock_env_vars):
        """Test that all environment variables are loaded correctly."""
        config = AgentConfig.from_env()

        assert config.openai_api_key == "sk-test-key-1234567890"
        assert config.langfuse_public_key == "pk-test-public-key"
        assert config.langfuse_secret_key == "sk-test-secret-key"
        assert config.langfuse_host == "https://test.langfuse.com"
        assert config.agentfield_control_plane_url == "http://test-control-plane:8000"
        assert config.port == 8001
        assert config.environment == "test"
        assert config.log_level == "DEBUG"

    def test_uses_default_values(self, monkeypatch):
        """Test that default values are used when env vars not set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        # Don't set other vars - should use defaults

        config = AgentConfig.from_env()

        assert config.openai_model == "gpt-4o-mini"
        assert config.openai_temperature == 0.3
        assert config.openai_max_tokens == 2000
        assert config.port == 8001
        assert config.environment == "development"
        assert config.log_level == "INFO"
        assert config.langfuse_host == "https://cloud.langfuse.com"

    def test_handles_missing_required_fields(self, monkeypatch):
        """Test that missing required fields raise validation error."""
        # Clear OPENAI_API_KEY
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "openai_api_key" in str(exc_info.value)

    def test_custom_base_url(self, mock_env_vars, monkeypatch):
        """Test custom OpenAI base URL for LiteLLM."""
        monkeypatch.setenv("OPENAI_BASE_URL", "https://litellm.example.com")

        config = AgentConfig.from_env()

        assert config.openai_base_url == "https://litellm.example.com"


class TestAgentConfigValidation:
    """Test Pydantic validation rules."""

    def test_invalid_log_level(self, mock_env_vars, monkeypatch):
        """Test that invalid log levels raise validation error."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "log_level" in str(exc_info.value)

    def test_invalid_port_number(self, mock_env_vars, monkeypatch):
        """Test that invalid port numbers raise validation error."""
        monkeypatch.setenv("PORT", "999999")  # Out of range

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "port" in str(exc_info.value)

    def test_negative_temperature(self, mock_env_vars, monkeypatch):
        """Test that negative temperature raises validation error."""
        monkeypatch.setenv("OPENAI_TEMPERATURE", "-0.5")

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "temperature" in str(exc_info.value).lower()

    def test_temperature_too_high(self, mock_env_vars, monkeypatch):
        """Test that temperature > 2.0 raises validation error."""
        monkeypatch.setenv("OPENAI_TEMPERATURE", "2.5")

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "temperature" in str(exc_info.value).lower()

    def test_negative_max_tokens(self, mock_env_vars, monkeypatch):
        """Test that negative max_tokens raises validation error."""
        monkeypatch.setenv("OPENAI_MAX_TOKENS", "-100")

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig.from_env()

        assert "max_tokens" in str(exc_info.value).lower()


class TestAgentConfigHelperProperties:
    """Test helper properties on AgentConfig."""

    def test_has_langfuse_true(self, mock_env_vars):
        """Test has_langfuse returns True when credentials present."""
        config = AgentConfig.from_env()

        assert config.has_langfuse is True

    def test_has_langfuse_false_missing_public_key(self, mock_env_vars, monkeypatch):
        """Test has_langfuse returns False when public key missing."""
        monkeypatch.delenv("LANGFUSE_PUBLIC_KEY")

        config = AgentConfig.from_env()

        assert config.has_langfuse is False

    def test_has_langfuse_false_missing_secret_key(self, mock_env_vars, monkeypatch):
        """Test has_langfuse returns False when secret key missing."""
        monkeypatch.delenv("LANGFUSE_SECRET_KEY")

        config = AgentConfig.from_env()

        assert config.has_langfuse is False

    def test_has_agentfield_true(self, mock_env_vars):
        """Test has_agentfield returns True when URL present."""
        config = AgentConfig.from_env()

        assert config.has_agentfield is True

    def test_has_agentfield_false(self, mock_env_vars, monkeypatch):
        """Test has_agentfield returns False when URL missing."""
        monkeypatch.delenv("AGENTFIELD_CONTROL_PLANE_URL")

        config = AgentConfig.from_env()

        assert config.has_agentfield is False

    def test_is_production_true(self, mock_env_vars, monkeypatch):
        """Test is_production returns True in production environment."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        config = AgentConfig.from_env()

        assert config.is_production is True

    def test_is_production_false(self, mock_env_vars):
        """Test is_production returns False in non-production environment."""
        config = AgentConfig.from_env()  # Uses "test" environment

        assert config.is_production is False


class TestAgentConfigLangfuseHostNormalization:
    """Test Langfuse host URL normalization."""

    def test_strips_trailing_slash(self, mock_env_vars, monkeypatch):
        """Test that trailing slash is removed from Langfuse host."""
        monkeypatch.setenv("LANGFUSE_HOST", "https://test.langfuse.com/")

        config = AgentConfig.from_env()

        assert config.langfuse_host == "https://test.langfuse.com"

    def test_handles_url_without_trailing_slash(self, mock_env_vars):
        """Test that URL without trailing slash remains unchanged."""
        config = AgentConfig.from_env()

        assert config.langfuse_host == "https://test.langfuse.com"


class TestAgentConfigDirectInstantiation:
    """Test creating AgentConfig directly (not from env)."""

    def test_minimal_config(self):
        """Test creating config with only required fields."""
        config = AgentConfig(openai_api_key="sk-test-key")

        assert config.openai_api_key == "sk-test-key"
        assert config.openai_model == "gpt-4o-mini"  # Default
        assert config.has_langfuse is False
        assert config.has_agentfield is False

    def test_full_config(self):
        """Test creating config with all fields."""
        config = AgentConfig(
            openai_api_key="sk-test-key",
            openai_base_url="https://litellm.example.com",
            openai_model="gpt-4o",
            openai_temperature=0.5,
            openai_max_tokens=1000,
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
            langfuse_host="https://langfuse.example.com",
            agentfield_control_plane_url="http://localhost:8000",
            port=8001,
            environment="production",
            log_level="WARNING",
        )

        assert config.openai_api_key == "sk-test-key"
        assert config.openai_base_url == "https://litellm.example.com"
        assert config.openai_model == "gpt-4o"
        assert config.openai_temperature == 0.5
        assert config.openai_max_tokens == 1000
        assert config.has_langfuse is True
        assert config.has_agentfield is True
        assert config.is_production is True
