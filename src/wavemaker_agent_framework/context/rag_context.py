"""
RAG context handling utilities.

Provides utilities for formatting and managing retrieval-augmented generation
context passed from BigRipple's knowledge service.
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class RAGSource:
    """A single source from RAG retrieval."""
    content: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    relevance_score: Optional[float] = None


class RAGContextFormatter:
    """Formats RAG context for injection into prompts."""

    def __init__(self, max_chars: int = 4000):
        """Initialize the RAG context formatter.

        Args:
            max_chars: Maximum characters to include in formatted context.
        """
        self.max_chars = max_chars

    def format_sources(self, sources: List[RAGSource]) -> str:
        """Format multiple RAG sources into a context string.

        Args:
            sources: List of RAG sources to format.

        Returns:
            Formatted context string.
        """
        if not sources:
            return ""

        lines = []
        current_length = 0

        for i, source in enumerate(sources, 1):
            source_header = f"[Source {i}"
            if source.source_name:
                source_header += f": {source.source_name}"
            source_header += "]"

            source_text = f"{source_header}\n{source.content}\n"

            if current_length + len(source_text) > self.max_chars:
                # Truncate if we're over the limit
                remaining = self.max_chars - current_length
                if remaining > 100:  # Only add if meaningful space remains
                    truncated = source.content[:remaining - len(source_header) - 20] + "..."
                    lines.append(f"{source_header}\n{truncated}\n")
                break

            lines.append(source_text)
            current_length += len(source_text)

        return "\n".join(lines)

    def parse_retrieval_context(self, retrieval_context: str) -> List[RAGSource]:
        """Parse a retrieval context string into structured sources.

        BigRipple returns retrieval context as a formatted string.
        This attempts to parse it back into structured sources.

        Args:
            retrieval_context: Raw retrieval context from BigRipple.

        Returns:
            List of parsed RAG sources.
        """
        if not retrieval_context:
            return []

        sources = []
        # Simple parsing - split by source markers
        parts = retrieval_context.split("[Source ")

        for part in parts[1:]:  # Skip first empty part
            if "]" in part:
                header_end = part.index("]")
                header = part[:header_end]
                content = part[header_end + 1:].strip()

                # Extract source name if present
                source_name = None
                if ":" in header:
                    source_name = header.split(":", 1)[1].strip()

                sources.append(RAGSource(
                    content=content,
                    source_name=source_name,
                ))

        # If no structured sources found, treat whole context as single source
        if not sources and retrieval_context:
            sources.append(RAGSource(content=retrieval_context))

        return sources

    def summarize_context(self, retrieval_context: str, max_chars: int = 500) -> str:
        """Create a brief summary of the retrieval context.

        Useful for logging or debug output.

        Args:
            retrieval_context: The full retrieval context.
            max_chars: Maximum characters in summary.

        Returns:
            Summarized context string.
        """
        if not retrieval_context:
            return "(no RAG context)"

        if len(retrieval_context) <= max_chars:
            return retrieval_context

        return retrieval_context[:max_chars - 3] + "..."
