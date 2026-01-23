"""
Wavemaker Agent Framework

A framework for building AgentField-compatible AI agents with reduced code duplication.
Provides core utilities, testing infrastructure, and templates for rapid agent development.
"""

__version__ = "0.1.0"

from wavemaker_agent_framework.core import AgentConfig, LLMClientFactory

__all__ = [
    "__version__",
    "AgentConfig",
    "LLMClientFactory",
]
