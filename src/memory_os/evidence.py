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
    """Project explicitly accepted conversation candidates into project history.

    Candidate records remain the evidence source; this function does not promote
    them to durable memories. Project-event identity is delegated to MemoryStore,
    making repeated projection idempotent.
    """
    rows = store.list_candidates(status="accepted", limit=1000)
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
        event_ids.append(
            store.add_project_event(
                project_id,
                f"candidate_{row['memory_type']}",
                row["content"],
                row["observed_at"],
                {
                    "candidate_id": row["candidate_id"],
                    "conversation_id": conversation_id,
                    "source_message_id": row["source_message_id"],
                    "confidence": row["confidence"],
                    "evidence_status": "accepted",
                },
            )
        )
    return event_ids


__all__ = ["record_conversation_candidates_as_project_events"]
