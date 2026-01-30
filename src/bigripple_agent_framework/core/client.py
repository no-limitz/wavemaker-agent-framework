"""
LLM Client Factory for wavemaker agents.

This module provides a factory for creating LLM clients with optional Langfuse
integration for automatic observability and tracing.
"""

import logging
from typing import Optional, Union
from openai import AsyncOpenAI

# Optional Langfuse integration
try:
    from langfuse import Langfuse
    from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI
    LANGFUSE_AVAILABLE = True
except ImportError:
    Langfuse = None
    LangfuseAsyncOpenAI = None
    LANGFUSE_AVAILABLE = False


logger = logging.getLogger(__name__)


class LLMClientFactory:
    """
    Factory for creating LLM clients with optional Langfuse integration.

    This factory handles:
    - Creating standard AsyncOpenAI clients
    - Wrapping clients with Langfuse for automatic tracing
    - LiteLLM base URL support (custom endpoints)
    - Proper error handling and logging
    """

    @classmethod
    async def create(
        cls,
        api_key: str,
        base_url: Optional[str] = None,
        enable_langfuse: bool = True,
        langfuse_secret_key: Optional[str] = None,
        langfuse_public_key: Optional[str] = None,
        langfuse_host: str = "https://cloud.langfuse.com",
    ) -> Union[AsyncOpenAI, "LangfuseAsyncOpenAI"]:
        """
        Create an LLM client with optional Langfuse wrapping.

        Args:
            api_key: OpenAI API key (required)
            base_url: Custom OpenAI base URL (for LiteLLM, optional)
            enable_langfuse: Whether to enable Langfuse wrapping (default: True)
            langfuse_secret_key: Langfuse secret key (optional, will use config if not provided)
            langfuse_public_key: Langfuse public key (optional, will use config if not provided)
            langfuse_host: Langfuse host URL (default: https://cloud.langfuse.com)

        Returns:
            AsyncOpenAI or LangfuseAsyncOpenAI: Configured LLM client

        Example:
            ```python
            from bigripple_agent_framework.core import AgentConfig, LLMClientFactory

            config = AgentConfig.from_env()
            client = await LLMClientFactory.create(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url,
                enable_langfuse=config.has_langfuse,
                langfuse_secret_key=config.langfuse_secret_key,
                langfuse_public_key=config.langfuse_public_key,
                langfuse_host=config.langfuse_host,
            )

            # Use standard OpenAI interface
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello!"}]
            )
            ```
        """
        logger.info("=" * 80)
        logger.info("[LLMClientFactory] Initializing LLM client")

        # Determine if we should use Langfuse
        use_langfuse = (
            enable_langfuse
            and LANGFUSE_AVAILABLE
            and langfuse_secret_key
            and langfuse_public_key
        )

        if use_langfuse:
            logger.info("[LLMClientFactory] Using Langfuse-wrapped client")
            logger.info(f"[LLMClientFactory]   - Langfuse host: {langfuse_host}")

            # Normalize Langfuse host (ensure protocol)
            if langfuse_host and not langfuse_host.startswith(("http://", "https://")):
                langfuse_host = f"https://{langfuse_host}"
                logger.info(f"[LLMClientFactory]   - Normalized host: {langfuse_host}")

            # Create Langfuse-wrapped client
            try:
                if base_url and base_url.strip():
                    logger.info(f"[LLMClientFactory]   - Custom base URL: {base_url}")
                    client = LangfuseAsyncOpenAI(
                        api_key=api_key,
                        base_url=base_url,
                    )
                else:
                    logger.info("[LLMClientFactory]   - Using default OpenAI endpoint")
                    client = LangfuseAsyncOpenAI(api_key=api_key)

                logger.info("[LLMClientFactory] ✓ Langfuse-wrapped client created")
                logger.info(f"[LLMClientFactory]   - Client type: {type(client).__name__}")
                logger.info("[LLMClientFactory]   - Automatic tracing enabled")

            except Exception as e:
                logger.error(f"[LLMClientFactory] ✗ Failed to create Langfuse client: {e}")
                logger.warning("[LLMClientFactory] Falling back to standard OpenAI client")
                use_langfuse = False

        if not use_langfuse:
            # Create standard OpenAI client
            logger.info("[LLMClientFactory] Using standard OpenAI client")

            if not enable_langfuse:
                logger.info("[LLMClientFactory]   - Reason: Langfuse disabled")
            elif not LANGFUSE_AVAILABLE:
                logger.info("[LLMClientFactory]   - Reason: Langfuse not installed")
            elif not (langfuse_secret_key and langfuse_public_key):
                logger.info("[LLMClientFactory]   - Reason: Langfuse credentials missing")

            if base_url and base_url.strip():
                logger.info(f"[LLMClientFactory]   - Custom base URL: {base_url}")
                client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            else:
                logger.info("[LLMClientFactory]   - Using default OpenAI endpoint")
                client = AsyncOpenAI(api_key=api_key)

            logger.info("[LLMClientFactory] ✓ Standard client created")
            logger.info(f"[LLMClientFactory]   - Client type: {type(client).__name__}")

        logger.info("=" * 80)
        return client

    @classmethod
    async def create_from_config(cls, config: "AgentConfig") -> Union[AsyncOpenAI, "LangfuseAsyncOpenAI"]:
        """
        Create an LLM client from AgentConfig.

        This is a convenience method that extracts all necessary
        configuration from an AgentConfig instance.

        Args:
            config: AgentConfig instance

        Returns:
            AsyncOpenAI or LangfuseAsyncOpenAI: Configured LLM client

        Example:
            ```python
            from bigripple_agent_framework.core import AgentConfig, LLMClientFactory

            config = AgentConfig.from_env()
            client = await LLMClientFactory.create_from_config(config)
            ```
        """
        return await cls.create(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            enable_langfuse=config.has_langfuse,
            langfuse_secret_key=config.langfuse_secret_key,
            langfuse_public_key=config.langfuse_public_key,
            langfuse_host=config.langfuse_host,
        )
