from __future__ import annotations

import sqlite3
from typing import Any

from .conversation import ensure_schema, get_messages
from .core import MemoryStore


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


def _entity(store: MemoryStore, entity_id: str) -> tuple[str, dict[str, Any]] | None:
    row = store.conn.execute(
        "SELECT project_id AS id, name, root, status, summary FROM projects WHERE project_id = ?",
        (entity_id,),
    ).fetchone()
    if row is not None:
        return "project", dict(row)
    row = store.conn.execute(
        "SELECT artifact_id AS id, name, artifact_type, location FROM artifacts WHERE artifact_id = ?",
        (entity_id,),
    ).fetchone()
    if row is not None:
        return "artifact", dict(row)
    row = store.conn.execute(
        "SELECT conversation_id AS id, title, source, started_at, ended_at FROM conversations WHERE conversation_id = ?",
        (entity_id,),
    ).fetchone()
    if row is not None:
        return "conversation", dict(row)
    return None


def _linked_entities(store: MemoryStore, entity_id: str, limit: int = 50) -> list[dict[str, Any]]:
    output = []
    for link in related_records(store, entity_id, limit):
        other_id = link["target_id"] if link["source_id"] == entity_id else link["source_id"]
        found = _entity(store, other_id)
        if found is None:
            continue
        kind, item = found
        item["kind"] = kind
        item["relation"] = link["relation"]
        item["relation_id"] = link["relation_id"]
        output.append(item)
    return output


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
    linked = _linked_entities(store, conversation_id, limit)

    # A conversation may point to a project whose artifacts are not directly linked
    # to the conversation. Include one graph hop through each linked project.
    seen = {item["id"] for item in linked}
    expanded = list(linked)
    for item in linked:
        if item["kind"] != "project":
            continue
        for child in _linked_entities(store, item["id"], limit):
            if child["id"] not in seen:
                seen.add(child["id"])
                child["via_project"] = item["id"]
                expanded.append(child)

    return {
        "conversation": dict(conversation),
        "messages": messages,
        "related": expanded,
    }


def project_context(store: MemoryStore, project_id: str, limit: int = 50) -> dict[str, Any]:
    """Return project state plus linked conversations, artifacts, and recent memories."""
    ensure_schema(store)
    if limit < 1:
        raise ValueError("limit must be at least 1")
    project = store.conn.execute(
        "SELECT * FROM projects WHERE project_id = ?", (project_id,)
    ).fetchone()
    if project is None:
        raise KeyError(f"project not found: {project_id}")

    linked = _linked_entities(store, project_id, limit)
    conversations = [item for item in linked if item["kind"] == "conversation"]
    artifacts = [item for item in linked if item["kind"] == "artifact"]

    memories = [dict(row) for row in store.conn.execute(
        """SELECT m.* FROM memories m
           JOIN relations r ON r.source_id = m.memory_id OR r.target_id = m.memory_id
           WHERE r.source_id = ? OR r.target_id = ?
           ORDER BY m.observed_at DESC LIMIT ?""",
        (project_id, project_id, limit),
    )]
    return {
        "project": dict(project),
        "conversations": conversations,
        "artifacts": artifacts,
        "memories": memories,
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


def render_project_reentry_brief(store: MemoryStore, project_id: str, limit: int = 50) -> str:
    packet = project_context(store, project_id, limit)
    project = packet["project"]
    lines = [f"# Project Re-entry: {project['name']}", "", f"Status: {project['status']}", f"Root: {project['root']}"]
    if project.get("summary"):
        lines += ["", "## Summary", project["summary"]]
    lines += ["", "## Artifacts"]
    if packet["artifacts"]:
        for item in packet["artifacts"]:
            lines.append(f"- {item['name']} ({item.get('artifact_type', 'unknown')}) — {item.get('location', '')}")
    else:
        lines.append("- No linked artifacts.")
    lines += ["", "## Conversations"]
    if packet["conversations"]:
        for item in packet["conversations"]:
            lines.append(f"- {item['title']} [{item['source']}] ({item.get('relation', 'related')})")
    else:
        lines.append("- No linked conversations.")
    lines += ["", "## Linked memories"]
    if packet["memories"]:
        for memory in packet["memories"]:
            lines.append(f"- [{memory['memory_type']}] {memory['content']}")
    else:
        lines.append("- No linked memories.")
    return "\n".join(lines)


__all__ = ["conversation_context", "project_context", "related_records", "render_project_reentry_brief", "render_reentry_brief"]
