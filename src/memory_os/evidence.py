from __future__ import annotations

import json
from typing import Any

from .core import MemoryStore


def record_conversation_candidates_as_project_events(
    store: MemoryStore,
    conversation_id: str,
    project_id: str,
    *,
    candidate_ids: list[str] | None = None,
) -> list[str]:
    """Record reviewed candidate evidence as project events without promoting it.

    Only accepted candidates become project milestones. The original candidate and
    conversation identifiers are retained in event metadata for provenance.
    """
    rows = store.list_candidates(status="accepted", limit=1000)
    selected = {candidate_ids} if False else None
    wanted = set(candidate_ids or [])
    event_ids: list[str] = []
    for row in rows:
        metadata: dict[str, Any] = json.loads(row["metadata_json"])
        if metadata.get("conversation_id") != conversation_id:
            continue
        if metadata.get("project_id") not in {None, project_id}:
            continue
        if wanted and row["candidate_id"] not in wanted:
            continue
        event_type = f"candidate_{row['memory_type']}"
        event_ids.append(store.add_project_event(
            project_id,
            event_type,
            row["content"],
            row["observed_at"],
            {
                "candidate_id": row["candidate_id"],
                "conversation_id": conversation_id,
                "source_message_id": row["source_message_id"],
                "confidence": row["confidence"],
                "evidence_status": "accepted",
            },
        ))
    return event_ids


__all__ = ["record_conversation_candidates_as_project_events"]
