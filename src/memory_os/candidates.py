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

# User-authored statements are stronger evidence for personal decisions/preferences.
# Assistant statements remain candidates only when they contain explicit decision/task language.
_PERSONAL_TYPES = {"decision", "preference"}


def extract_candidates(
    messages: Iterable[Message],
    max_per_message: int = 2,
    project_id: str | None = None,
) -> list[MemoryCandidate]:
    """Extract conservative, reviewable candidates from explicit language.

    Candidates remain evidence, not durable memory. Role is used as a confidence
    signal rather than as an absolute filter so useful task/decision evidence is not lost.
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
            if not any(pattern in lowered for pattern in patterns):
                continue
            adjusted = confidence
            if message.role != "user" and memory_type in _PERSONAL_TYPES:
                adjusted = max(0.0, confidence - 0.2)
            metadata = {
                "role": message.role,
                "observed_at": message.observed_at,
                "source_message_id": message.message_id,
            }
            if project_id:
                metadata["project_id"] = project_id
            candidates.append(MemoryCandidate(
                memory_type=memory_type,
                content=text,
                source_message_sequence=message.sequence,
                confidence=adjusted,
                metadata=metadata,
            ))
            found += 1
            if found >= max_per_message:
                break
    return candidates


def persist_candidates(
    store: MemoryStore,
    conversation_id: str,
    messages: Iterable[Message],
    max_per_message: int = 2,
    project_id: str | None = None,
) -> list[str]:
    """Persist extracted candidates without promoting them to durable memory."""
    ids: list[str] = []
    for candidate in extract_candidates(
        messages, max_per_message=max_per_message, project_id=project_id
    ):
        source_message_id = (candidate.metadata or {}).get("source_message_id")
        record = MemoryCandidateRecord(
            content=candidate.content,
            memory_type=candidate.memory_type,
            source=f"conversation:{conversation_id}",
            source_message_id=source_message_id,
            confidence=candidate.confidence,
            status="candidate",
            observed_at=(candidate.metadata or {}).get("observed_at") or "",
            metadata={
                **(candidate.metadata or {}),
                "conversation_id": conversation_id,
                "source_message_sequence": candidate.source_message_sequence,
            },
        )
        ids.append(store.add_candidate(record))
    return ids


__all__ = ["MemoryCandidate", "extract_candidates", "persist_candidates"]
