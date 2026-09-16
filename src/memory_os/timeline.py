from __future__ import annotations

import json
from typing import Any


def project_timeline(store: Any, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """Return a deterministic activity timeline for a project and its recorded evidence."""
    if limit < 1:
        return []

    events: list[dict[str, Any]] = []
    project = store.conn.execute(
        "SELECT * FROM projects WHERE project_id = ?", (project_id,)
    ).fetchone()
    if project is None:
        return []

    for event in store.list_project_events(project_id, limit=limit):
        events.append({
            "event_type": event["event_type"],
            "timestamp": event["timestamp"],
            "entity_id": project_id,
            "summary": event["summary"],
            "metadata": json.loads(event["metadata_json"] or "{}"),
        })

    relations = store.conn.execute(
        "SELECT * FROM relations WHERE source_id = ? OR target_id = ? ORDER BY created_at ASC",
        (project_id, project_id),
    ).fetchall()
    for relation in relations:
        other_id = relation["target_id"] if relation["source_id"] == project_id else relation["source_id"]
        direction = "outgoing" if relation["source_id"] == project_id else "incoming"
        events.append({
            "event_type": "relation",
            "timestamp": relation["created_at"],
            "entity_id": other_id,
            "summary": f"{direction} relation: {relation['relation']} → {other_id}",
            "metadata": json.loads(relation["metadata_json"] or "{}"),
        })

    artifact_relations = [
        r for r in relations if r["relation"] == "contains" and r["source_id"] == project_id
    ]
    for relation in artifact_relations:
        artifact = store.conn.execute(
            "SELECT * FROM artifacts WHERE artifact_id = ?", (relation["target_id"],)
        ).fetchone()
        if artifact is not None and artifact["modified_at"]:
            events.append({
                "event_type": "artifact_modified",
                "timestamp": artifact["modified_at"],
                "entity_id": artifact["artifact_id"],
                "summary": f"Artifact modified: {artifact['name']}",
                "metadata": json.loads(artifact["metadata_json"] or "{}"),
            })

    events.sort(key=lambda item: (item["timestamp"] is not None, item["timestamp"] or ""), reverse=True)
    return events[:limit]


def render_project_timeline(store: Any, project_id: str, limit: int = 100) -> str:
    project = store.conn.execute(
        "SELECT name, root, status FROM projects WHERE project_id = ?", (project_id,)
    ).fetchone()
    if project is None:
        return f"# Project Timeline\n\nProject not found: `{project_id}`"

    lines = [
        f"# Project Timeline: {project['name']}",
        "",
        f"- Root: `{project['root']}`",
        f"- Status: `{project['status']}`",
        "",
        "## Activity",
        "",
    ]
    events = project_timeline(store, project_id, limit)
    if not events:
        lines.append("No recorded activity yet.")
        return "\n".join(lines)
    for event in events:
        timestamp = event["timestamp"] or "undated"
        lines.append(f"- **{timestamp}** — {event['summary']}")
    return "\n".join(lines)


__all__ = ["project_timeline", "render_project_timeline"]
