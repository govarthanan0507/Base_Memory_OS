from __future__ import annotations

import json
from typing import Any

from .conversation import ensure_schema
from .core import MemoryStore


def related_records(store: MemoryStore, source_id: str, limit: int = 50) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return [
        dict(r)
        for r in store.conn.execute(
            "SELECT relation_id, source_id, relation, target_id, created_at, metadata_json "
            "FROM relations WHERE source_id=? OR target_id=? ORDER BY created_at DESC LIMIT ?",
            (source_id, source_id, limit),
        )
    ]


def _entity(store: MemoryStore, entity_id: str):
    queries = [
        ("SELECT project_id AS id, name, root, status, summary FROM projects WHERE project_id=?", "project"),
        ("SELECT artifact_id AS id, name, artifact_type, location FROM artifacts WHERE artifact_id=?", "artifact"),
        ("SELECT conversation_id AS id, title, source, started_at, ended_at FROM conversations WHERE conversation_id=?", "conversation"),
        ("SELECT memory_id AS id, content, memory_type, source, observed_at FROM memories WHERE memory_id=?", "memory"),
    ]
    for sql, kind in queries:
        row = store.conn.execute(sql, (entity_id,)).fetchone()
        if row is not None:
            item = dict(row)
            item["entity_id"] = item["id"]
            if kind == "memory":
                item["memory_id"] = item["id"]
                item["name"] = item["content"]
            elif kind == "conversation":
                item["name"] = item["title"]
            return kind, item
    return None


def _linked_entities(store: MemoryStore, entity_id: str, limit: int = 50):
    out = []
    for link in related_records(store, entity_id, limit):
        other = link["target_id"] if link["source_id"] == entity_id else link["source_id"]
        found = _entity(store, other)
        if found is None:
            continue
        kind, item = found
        item.update(kind=kind, relation=link["relation"], relation_id=link["relation_id"])
        out.append(item)
    return out


def conversation_context(store: MemoryStore, conversation_id: str, limit: int = 50):
    ensure_schema(store)
    row = store.conn.execute(
        "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"conversation not found: {conversation_id}")
    messages = [
        dict(r)
        for r in store.conn.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence LIMIT ?",
            (conversation_id, limit),
        )
    ]
    linked = _linked_entities(store, conversation_id, limit)
    seen = {x["id"] for x in linked}
    expanded = list(linked)
    for item in linked:
        if item["kind"] == "project":
            for child in _linked_entities(store, item["id"], limit):
                if child["id"] == conversation_id or child["id"] in seen:
                    continue
                child["via_project"] = item["id"]
                seen.add(child["id"])
                expanded.append(child)
    return {"conversation": dict(row), "messages": messages, "related": expanded}


def _open_project_candidates(store: MemoryStore, project_id: str, limit: int) -> list[dict[str, Any]]:
    """Return candidate memories explicitly tagged with this project in metadata."""
    rows = store.list_candidates("candidate", limit=max(limit * 3, limit))
    output = []
    for row in rows:
        metadata = json.loads(row["metadata_json"] or "{}")
        if metadata.get("project_id") != project_id:
            continue
        item = dict(row)
        item["metadata"] = metadata
        output.append(item)
        if len(output) >= limit:
            break
    return output


def project_context(store: MemoryStore, project_id: str, limit: int = 50):
    ensure_schema(store)
    if limit < 1:
        raise ValueError("limit must be at least 1")
    row = store.conn.execute(
        "SELECT * FROM projects WHERE project_id=?", (project_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"project not found: {project_id}")
    linked = _linked_entities(store, project_id, limit)
    events = [
        dict(item)
        for item in store.conn.execute(
            "SELECT event_id, timestamp, event_type, summary, metadata_json "
            "FROM project_events WHERE project_id=? ORDER BY timestamp DESC LIMIT ?",
            (project_id, limit),
        )
    ]
    conversations = [x for x in linked if x["kind"] == "conversation"]
    latest_conversation = None
    if conversations:
        latest_conversation = max(
            conversations,
            key=lambda x: x.get("ended_at") or x.get("started_at") or "",
        )
    return {
        "project": dict(row),
        "conversations": conversations,
        "artifacts": [x for x in linked if x["kind"] == "artifact"],
        "memories": [x for x in linked if x["kind"] == "memory"],
        "open_candidates": _open_project_candidates(store, project_id, limit),
        "events": events,
        "latest_conversation": latest_conversation,
    }


def render_reentry_brief(store: MemoryStore, conversation_id: str, limit: int = 50) -> str:
    packet = conversation_context(store, conversation_id, limit)
    conversation = packet["conversation"]
    lines = [
        f"# Re-entry: {conversation['title']}",
        "",
        f"Conversation ID: {conversation_id}",
        f"Source: {conversation['source']}",
        "",
        "## Known related work",
    ]
    lines += [
        f"- {x['kind']}: {x.get('name', x.get('title', x.get('content', x['id'])))} ({x['relation']})"
        for x in packet["related"]
    ] or ["- No linked project or artifact yet."]
    lines += ["", "## Conversation"] + [
        f"**{m['role']}**: {m['content']}" for m in packet["messages"]
    ]
    return "\n".join(lines)


def render_project_reentry_brief(store: MemoryStore, project_id: str, limit: int = 50) -> str:
    packet = project_context(store, project_id, limit)
    project = packet["project"]
    lines = [
        f"# Project Re-entry: {project['name']}",
        "",
        f"Project ID: {project_id}",
        f"Status: {project['status']}",
        f"Root: {project['root']}",
    ]
    if project.get("summary"):
        lines.append(f"Summary: {project['summary']}")

    latest = packet["latest_conversation"]
    lines += ["", "## Last known conversation"]
    lines.append(
        f"- {latest['title']} [{latest['source']}] — {latest['id']}"
        if latest else "- No linked conversation recorded."
    )

    lines += ["", "## Recent recorded activity"]
    if packet["events"]:
        lines.extend(
            f"- {event['timestamp']} — **{event['event_type']}** — {event['summary']}"
            for event in packet["events"][:3]
        )
    else:
        lines.append("- No project event recorded.")

    lines += ["", "## Open unresolved candidates"]
    if packet["open_candidates"]:
        lines.extend(
            f"- [{c['memory_type']}] {c['content']} (confidence={c['confidence']:.2f})"
            for c in packet["open_candidates"]
        )
    else:
        lines.append("- None recorded.")

    lines += ["", "## Artifacts"]
    lines += [
        f"- {a['name']} ({a.get('artifact_type', 'unknown')}) — {a.get('location', '')}"
        for a in packet["artifacts"]
    ] or ["- No linked artifacts."]
    lines += ["", "## Linked memories"]
    lines += [
        f"- [{m['memory_type']}] {m['content']} — {m['memory_id']}"
        for m in packet["memories"]
    ] or ["- No linked memories."]
    return "\n".join(lines)


__all__ = [
    "conversation_context",
    "project_context",
    "related_records",
    "render_project_reentry_brief",
    "render_reentry_brief",
]
