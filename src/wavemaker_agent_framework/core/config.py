"""
Configuration management for wavemaker agents.

This module provides a centralized configuration class that loads and validates
environment variables for AgentField-compatible agents.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    """
    Centralized configuration for AgentField agents.

    Loads configuration from environment variables with sensible defaults.
    All agents should use this class to manage their configuration.
    """

    # OpenAI / LLM Configuration
    openai_api_key: str = Field(..., description="OpenAI API key (required)")
    openai_base_url: Optional[str] = Field(None, description="Custom OpenAI base URL (for LiteLLM)")
    openai_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    openai_temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="LLM temperature")
    openai_max_tokens: int = Field(default=2000, gt=0, description="Max tokens per LLM call")

    # Langfuse Configuration (optional)
    langfuse_secret_key: Optional[str] = Field(None, description="Langfuse secret key")
    langfuse_public_key: Optional[str] = Field(None, description="Langfuse public key")
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com", description="Langfuse host URL"
    )

    # AgentField Configuration
    agentfield_control_plane_url: Optional[str] = Field(
        None, description="AgentField control plane URL"
    )
    agent_callback_url: Optional[str] = Field(None, description="Agent callback URL")

    # Server Configuration
    port: int = Field(default=8001, gt=0, le=65535, description="Server port")
    environment: str = Field(default="development", description="Environment (development/production)")
    log_level: str = Field(default="INFO", description="Logging level")

    # Agent-Specific Configuration (can be extended by subclasses)
    max_content_length: int = Field(default=5000, gt=0, description="Max content length to process")
    crawler_timeout: int = Field(default=30, gt=0, description="HTTP crawler timeout in seconds")

    @field_validator("langfuse_host")
    @classmethod
    def normalize_langfuse_host(cls, v: str) -> str:
        """Ensure Langfuse host has protocol prefix."""
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create configuration from environment variables.

        Environment variables are automatically mapped to config fields:
        - OPENAI_API_KEY -> openai_api_key
        - OPENAI_BASE_URL -> openai_base_url
        - etc.

        Returns:
            AgentConfig: Configured instance loaded from environment.

        Raises:
            ValueError: If required environment variables are missing.
        """
        return cls(
            # OpenAI configuration
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            # Langfuse configuration
            langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            # AgentField configuration
            agentfield_control_plane_url=os.getenv("AGENTFIELD_CONTROL_PLANE_URL"),
            agent_callback_url=os.getenv("AGENT_CALLBACK_URL"),
            # Server configuration
            port=int(os.getenv("PORT", "8001")),
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            # Agent-specific configuration
            max_content_length=int(os.getenv("MAX_CONTENT_LENGTH", "5000")),
            crawler_timeout=int(os.getenv("CRAWLER_TIMEOUT", "30")),
        )

    @property
    def has_langfuse(self) -> bool:
        """Check if Langfuse credentials are configured."""
        return bool(self.langfuse_secret_key and self.langfuse_public_key)

    @property
    def has_agentfield(self) -> bool:
        """Check if AgentField control plane is configured."""
        return bool(self.agentfield_control_plane_url)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def __repr__(self) -> str:
        """String representation with masked sensitive fields."""
        api_key_masked = f"{self.openai_api_key[:8]}..." if self.openai_api_key else "None"
        return (
            f"AgentConfig(openai_api_key={api_key_masked}, "
            f"model={self.openai_model}, "
            f"environment={self.environment}, "
            f"has_langfuse={self.has_langfuse}, "
            f"has_agentfield={self.has_agentfield})"
        )
