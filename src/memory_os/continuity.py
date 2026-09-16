from __future__ import annotations

import json
from typing import Any

from .core import MemoryStore
from .conversation import ensure_schema


def related_records(store: MemoryStore, source_id: str, limit: int = 50) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    rows = store.conn.execute(
        """
        SELECT relation_id, source_id, relation, target_id, created_at, metadata_json
        FROM relations
        WHERE source_id = ? OR target_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (source_id, source_id, limit)
    )
    return [dict(row) for row in rows]


def conversation_context(store: MemoryStore, conversation_id: str, limit: int = 50) -> dict[str, Any]:
    """Return a compact context packet for a conversation and its known graph links."""
    ensure_schema(store)
    conversation = store.conn.execute(
        "SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,)
    ).fetchone()
    if conversation is None:
        raise KeyError(f"conversation not found: {conversation_id}")

    messages = [dict(row) for row in store.conn.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY sequence LIMIT ?",
        (conversation_id, limit)
    )]
    links = related_records(store, conversation_id, limit)

    linked = []
    for link in links:
        target = link["target_id"] if link["source_id"] == conversation_id else link["source_id"]
        row = store.conn.execute(
            "SELECT project_id AS id, name, root, status, summary FROM projects WHERE project_id = ?",
            (target,),
        ).fetchone()
        kind = "project"
        if row is None:
            row = store.conn.execute(
                "SELECT artifact_id AS id, name, artifact_type, location FROM artifacts WHERE artifact_id = ?",
                (target,),
            ).fetchone()
            kind = "artifact"
        if row is not None:
            item = dict(row)
            item["kind"] = kind
            item["relation"] = link["relation"]
            linked.append(item)

    return {
        "conversation": dict(conversation),
        "messages": messages,
        "related": linked,
    }


def render_reentry_brief(store: MemoryStore, conversation_id: str, limit: int = 50) -> str:
    packet = conversation_context(store, conversation_id, limit)
    conversation = packet["conversation"]
    lines = [f"# Re-entry: {conversation['title']}", "", f"Source: {conversation['source']}"]
    if conversation.get("started_at"):
        lines.append(f"Started: {conversation['started_at']}")
    if conversation.get("ended_at"):
        lines.append(f"Ended: {conversation['ended_at']}")
    lines += ["", "## Known related work"]
    if packet["related"]:
        for item in packet["related"]:
            label = item.get("name", item["id"])
            lines.append(f"- {item['kind']}: {label} ({item['relation']})")
    else:
        lines.append("- No linked project or artifact yet.")
    lines += ["", "## Conversation"]
    for message in packet["messages"]:
        lines.append(f"**{message['role']}**: {message['content']}")
    return "\n".join(lines)


__all__ = ["conversation_context", "related_records", "render_reentry_brief"]
