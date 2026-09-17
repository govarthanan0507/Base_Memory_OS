from __future__ import annotations
import json
from typing import Any
from .core import MemoryStore
from .conversation import ensure_schema

def link_conversation_to_project(store: MemoryStore, conversation_id: str, project_id: str) -> str:
    ensure_schema(store)
    conversation = store.conn.execute("SELECT conversation_id FROM conversations WHERE conversation_id=?", (conversation_id,)).fetchone()
    project = store.conn.execute("SELECT project_id FROM projects WHERE project_id=?", (project_id,)).fetchone()
    if conversation is None: raise KeyError(f"conversation not found: {conversation_id}")
    if project is None: raise KeyError(f"project not found: {project_id}")
    store.relate(project_id, "has_conversation", conversation_id, {"evidence_status": "explicit"})
    return conversation_id

def record_conversation_candidates_as_project_events(store: MemoryStore, conversation_id: str, project_id: str, *, candidate_ids: list[str] | None = None) -> list[str]:
    rows = store.list_candidates(status="accepted", limit=1000); wanted=set(candidate_ids or []); event_ids=[]
    for row in rows:
        metadata: dict[str, Any] = json.loads(row["metadata_json"])
        if metadata.get("conversation_id") != conversation_id or metadata.get("project_id") not in {None, project_id}: continue
        if wanted and row["candidate_id"] not in wanted: continue
        link_conversation_to_project(store, conversation_id, project_id)
        event_ids.append(store.add_project_event(project_id, f"candidate_{row['memory_type']}", row["content"], row["observed_at"], {"candidate_id":row["candidate_id"],"conversation_id":conversation_id,"source_message_id":row["source_message_id"],"confidence":row["confidence"],"evidence_status":"accepted"}))
    return event_ids

__all__=["link_conversation_to_project","record_conversation_candidates_as_project_events"]
