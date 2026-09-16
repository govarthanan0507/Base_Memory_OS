from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .conversation import Message
from .core import MemoryCandidateRecord, MemoryStore


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
    """Extract conservative, reviewable candidates from explicit language."""
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
                    metadata={"role": message.role, "observed_at": message.observed_at,
                              "source_message_id": message.message_id},
                ))
                found += 1
                if found >= max_per_message:
                    break
    return candidates


def persist_candidates(store: MemoryStore, conversation_id: str,
                       messages: Iterable[Message], max_per_message: int = 2) -> list[str]:
    """Persist extracted candidates without promoting them to durable memory."""
    ids: list[str] = []
    for candidate in extract_candidates(messages, max_per_message=max_per_message):
        source_message_id = (candidate.metadata or {}).get("source_message_id")
        record = MemoryCandidateRecord(
            content=candidate.content,
            memory_type=candidate.memory_type,
            source=f"conversation:{conversation_id}",
            source_message_id=source_message_id,
            confidence=candidate.confidence,
            status="candidate",
            observed_at=(candidate.metadata or {}).get("observed_at") or "",
            metadata={**(candidate.metadata or {}), "conversation_id": conversation_id,
                      "source_message_sequence": candidate.source_message_sequence},
        )
        ids.append(store.add_candidate(record))
    return ids


__all__ = ["MemoryCandidate", "extract_candidates", "persist_candidates"]
