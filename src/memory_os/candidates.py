from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .conversation import Message


@dataclass(frozen=True)
class MemoryCandidate:
    memory_type: str
    content: str
    source_message_sequence: int
    confidence: float = 0.5
    status: str = "candidate"
    metadata: dict[str, Any] | None = None


_PATTERNS: tuple[tuple[str, tuple[str, ...], float], ...] = (
    ("decision", ("we decided", "i decided", "decided to", "let's use", "we'll use", "we will use"), 0.8),
    ("preference", ("i prefer", "i want", "i don't want", "i do not want", "prefer to"), 0.75),
    ("task", ("todo", "to do", "next step", "need to", "should build", "should add"), 0.7),
    ("unresolved", ("not sure", "need to figure out", "still need to", "what if", "how do we"), 0.6),
)


def extract_candidates(messages: Iterable[Message], max_per_message: int = 2) -> list[MemoryCandidate]:
    """Extract conservative, reviewable candidates from explicit language.

    This is deliberately heuristic. Candidates are never persisted or promoted here.
    """
    if max_per_message < 1:
        raise ValueError("max_per_message must be at least 1")
    candidates: list[MemoryCandidate] = []
    for message in messages:
        text = " ".join(message.content.strip().split())
        lowered = text.lower()
        if not text:
            continue
        found = 0
        for memory_type, patterns, confidence in _PATTERNS:
            if any(pattern in lowered for pattern in patterns):
                candidates.append(MemoryCandidate(
                    memory_type=memory_type,
                    content=text,
                    source_message_sequence=message.sequence,
                    confidence=confidence,
                    metadata={"role": message.role, "observed_at": message.observed_at},
                ))
                found += 1
                if found >= max_per_message:
                    break
    return candidates


__all__ = ["MemoryCandidate", "extract_candidates"]
