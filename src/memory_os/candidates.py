from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable
from .conversation import Message, message_id
from .core import MemoryCandidateRecord, MemoryStore

@dataclass(frozen=True)
class MemoryCandidate:
    memory_type: str
    content: str
    source_message_sequence: int
    confidence: float = 0.5
    status: str = "candidate"
    metadata: dict[str, Any] | None = None

_PATTERNS = (("decision", ("we decided", "i decided", "decided to", "let's use", "we'll use", "we will use"), .8), ("preference", ("i prefer", "i want", "i don't want", "i do not want", "prefer to"), .75), ("task", ("todo", "to do", "next step", "need to", "should build", "should add"), .7), ("unresolved", ("not sure", "need to figure out", "still need to", "what if", "how do we"), .6))
_PERSONAL_TYPES = {"decision", "preference"}

def _normalize(raw: Message | dict[str, Any]) -> Message:
    if isinstance(raw, Message): return raw
    return Message(str(raw.get("role", "")), str(raw.get("content", "")), int(raw.get("sequence", 0)), raw.get("observed_at"), raw.get("external_id"), raw.get("metadata") or {}, raw.get("message_id"))

def extract_candidates(messages: Iterable[Message | dict[str, Any]], max_per_message: int = 2, project_id: str | None = None) -> list[MemoryCandidate]:
    if max_per_message < 1: raise ValueError("max_per_message must be at least 1")
    out = []
    for raw in messages:
        message = _normalize(raw); text = " ".join(message.content.strip().split())
        if not text: continue
        found = 0
        for kind, patterns, confidence in _PATTERNS:
            if not any(p in text.lower() for p in patterns): continue
            if message.role != "user" and kind in _PERSONAL_TYPES: confidence = max(0.0, confidence - .2)
            sid = message.message_id or message_id("unbound", message.sequence, message.role, message.content, message.external_id)
            meta = {"role": message.role, "observed_at": message.observed_at, "source_message_id": sid}
            if project_id: meta["project_id"] = project_id
            out.append(MemoryCandidate(kind, text, message.sequence, confidence, metadata=meta)); found += 1
            if found >= max_per_message: break
    return out

def persist_candidates(store: MemoryStore, conversation_id: str, messages: Iterable[Message | dict[str, Any]], max_per_message: int = 2, project_id: str | None = None) -> list[str]:
    ids = []
    for c in extract_candidates(messages, max_per_message, project_id):
        meta = c.metadata or {}
        ids.append(store.add_candidate(MemoryCandidateRecord(c.content, c.memory_type, f"conversation:{conversation_id}", meta.get("source_message_id"), c.confidence, "candidate", meta.get("observed_at") or "", metadata={**meta, "conversation_id": conversation_id, "source_message_sequence": c.source_message_sequence})))
    return ids

__all__ = ["MemoryCandidate", "extract_candidates", "persist_candidates"]
