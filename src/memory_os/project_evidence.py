from __future__ import annotations

import json
from .core import MemoryStore


def render_project_evidence(store: MemoryStore, project_id: str, limit: int = 50) -> str:
    """Render a compact, evidence-labelled project state view.

    Structural signals are deliberately presented as evidence, not as claims of
    intent, quality, production readiness, or completion.
    """
    if limit < 1:
        return ""
    project = store.conn.execute(
        "SELECT * FROM projects WHERE project_id=?", (project_id,)
    ).fetchone()
    if project is None:
        raise KeyError(project_id)

    metadata = json.loads(project["metadata_json"])
    state = metadata.get("state_evidence", {})
    git = metadata.get("git", {})
    artifacts = store.conn.execute(
        "SELECT a.* FROM artifacts a JOIN relations r ON r.target_id=a.artifact_id "
        "WHERE r.source_id=? AND r.relation='contains' ORDER BY a.location LIMIT ?",
        (project_id, limit),
    ).fetchall()
    conversations = store.conn.execute(
        "SELECT r.target_id FROM relations r WHERE r.source_id=? "
        "AND r.relation='has_conversation' ORDER BY r.created_at LIMIT ?",
        (project_id, limit),
    ).fetchall()
    events = store.list_project_events(project_id, limit=limit)

    lines = [
        f"# Project Evidence — {project['name']}",
        "",
        f"- Project ID: `{project_id}`",
        f"- Root: `{project['root']}`",
        f"- Current recorded status: **{project['status']}**",
        f"- Discovery confidence: {project['confidence']:.2f}",
        "",
        "> This is an evidence view. Structural signals do not prove project intent, code quality, production readiness, or completion.",
        "",
        "## Current snapshot",
        "",
        f"- Files: {metadata.get('file_count', 0)}; code files: {metadata.get('code_file_count', 0)}",
        f"- Tests detected: {state.get('test_file_count', 0)}",
        f"- TODO/FIXME markers: {state.get('todo_fixme_count', 0)}",
        f"- Recent code activity (30d): {state.get('recent_code_file_count_30d', 0)} files",
        f"- Entry points detected: {len(metadata.get('likely_entrypoints', []))}",
        f"- Git: {git.get('git_branch', 'unknown branch')} @ {git.get('git_head', 'unknown head')}",
        "",
        "## Historical evidence",
        "",
    ]
    if events:
        lines.extend(
            f"- {row['timestamp']} — **{row['event_type']}** — {row['summary']}"
            for row in events
        )
    else:
        lines.append("- No recorded project events.")

    lines += ["", "## Explicit continuity", ""]
    if conversations:
        lines.extend(f"- conversation `{row['target_id']}`" for row in conversations)
    else:
        lines.append("- No explicitly linked conversations.")

    lines += ["", "## Current artifacts", ""]
    if artifacts:
        lines.extend(
            f"- `{row['location']}` [{row['artifact_type']}] hash={row['content_hash'] or 'unhashed'}"
            for row in artifacts
        )
    else:
        lines.append("- No registered artifacts.")
    return "\n".join(lines)


__all__ = ["render_project_evidence"]
