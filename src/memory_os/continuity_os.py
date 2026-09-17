from __future__ import annotations

from typing import Any

from .continuity import project_context
from .core import MemoryStore


def continuity_snapshot(store: MemoryStore, limit: int = 20) -> list[dict[str, Any]]:
    """Return a compact, read-only snapshot of known project continuity state."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    output: list[dict[str, Any]] = []
    for project in store.list_projects(limit):
        packet = project_context(store, project["project_id"], limit)
        latest = packet["latest_conversation"]
        output.append({
            "project_id": project["project_id"],
            "name": project["name"],
            "status": project["status"],
            "root": project["root"],
            "latest_conversation_id": latest["id"] if latest else None,
            "latest_conversation_title": latest["title"] if latest else None,
            "open_candidate_count": len(packet["open_candidates"]),
            "artifact_count": len(packet["artifacts"]),
            "memory_count": len(packet["memories"]),
        })
    return output


def render_continuity_dashboard(store: MemoryStore, limit: int = 20) -> str:
    """Render a deterministic human-readable continuity dashboard."""
    snapshot = continuity_snapshot(store, limit)
    lines = ["# Personal Work Continuity", "", f"Projects: {len(snapshot)}"]
    if not snapshot:
        lines += ["", "No projects recorded."]
        return "\n".join(lines)
    lines += ["", "## Projects"]
    for item in snapshot:
        conversation = item["latest_conversation_title"] or "none"
        lines.append(
            f"- **{item['name']}** [{item['status']}] — last conversation: {conversation}; "
            f"open threads: {item['open_candidate_count']}; artifacts: {item['artifact_count']}"
        )
    return "\n".join(lines)


__all__ = ["continuity_snapshot", "render_continuity_dashboard"]
