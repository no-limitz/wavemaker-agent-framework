"""
Strands SDK integration for BigRipple agents.

Provides a simplified way to create agents that work with BigRipple's
entity context and operation system.
"""

from bigripple_agent_framework.strands.agent import (
    BigRippleAgent,
    create_agent,
    AgentResult,
)

__all__ = [
    "BigRippleAgent",
    "create_agent",
    "AgentResult",
]
