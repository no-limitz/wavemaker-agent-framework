"""
Strands SDK integration for BigRipple agents.

Provides a simplified way to create agents that work with BigRipple's
entity context and operation system.
"""

from bigripple.strands.agent import (
    BigRippleAgent,
    create_agent,
    AgentResult,
)

__all__ = [
    "BigRippleAgent",
    "create_agent",
    "AgentResult",
]
