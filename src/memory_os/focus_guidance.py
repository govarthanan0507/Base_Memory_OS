"""Proactive focus guidance, per E5_REQUIREMENTS.md.

Two composed, purely-read signals over data E1/E3 already produce:
idea-hop detection (recent cross-project switching in `project_events`)
and a cross-project completion rollup (E1's own
`project_completion_signal`, called once per known project). Neither
signal is cached or persisted — both are computed fresh every call,
per `idea.md`'s "maintained internally, never written back to disk"
constraint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .continuity import project_completion_signal
from .conversation import ensure_schema
from .core import MemoryStore

# Fraction of adjacent event pairs in the window that must belong to
# different projects for the window to count as idea-hopping. Named
# and fixed, not tuned per call, so the signal's basis stays
# inspectable rather than a hidden knob.
_HOP_SWITCH_RATIO_THRESHOLD = 0.5


@dataclass(frozen=True)
class IdeaHopSignal:
    available: bool
    detected: bool = False
    reason: str = ""
    window_size: int = 0
    switch_count: int = 0
    projects_involved: tuple[str, ...] = field(default_factory=tuple)


def _recent_project_events(store: MemoryStore, window: int) -> list[dict[str, Any]]:
    rows = store.conn.execute(
        "SELECT project_id, timestamp FROM project_events ORDER BY timestamp DESC LIMIT ?",
        (window,),
    ).fetchall()
    return [dict(r) for r in rows]


def detect_idea_hopping(store: MemoryStore, window: int = 8) -> IdeaHopSignal:
    """Flag rapid idea-hopping from the most recent `window` project
    events across ALL projects (unlike E1's own signal, which is
    scoped to one project). Never a forced guess: too little evidence
    is reported as `unavailable`, not as "not hopping".
    """
    if window < 2:
        raise ValueError("window must be at least 2")
    ensure_schema(store)
    events = _recent_project_events(store, window)
    if len(events) < 2:
        return IdeaHopSignal(available=False, reason="fewer than 2 recorded project events")

    distinct_projects = {e["project_id"] for e in events}
    if len(distinct_projects) < 2:
        return IdeaHopSignal(
            available=True, detected=False, reason="all recent activity is on one project",
            window_size=len(events), switch_count=0, projects_involved=tuple(distinct_projects),
        )

    switch_count = sum(
        1 for a, b in zip(events, events[1:]) if a["project_id"] != b["project_id"]
    )
    ratio = switch_count / (len(events) - 1)
    detected = ratio >= _HOP_SWITCH_RATIO_THRESHOLD
    reason = (
        f"{switch_count} project switch(es) across the last {len(events)} recorded event(s)"
    )
    return IdeaHopSignal(
        available=True, detected=detected, reason=reason, window_size=len(events),
        switch_count=switch_count, projects_involved=tuple(distinct_projects),
    )


def cross_project_completion(store: MemoryStore, limit: int = 50) -> list[dict[str, Any]]:
    """Every known project's own `project_completion_signal`, reused
    directly rather than reimplemented (Data-Architect's note in
    E5_REQUIREMENTS.md).
    """
    ensure_schema(store)
    out = []
    for row in store.list_projects(limit=limit):
        signal = project_completion_signal(store, row["project_id"])
        out.append({"project_id": row["project_id"], "name": row["name"], "signal": signal})
    return out


def render_focus_guidance(store: MemoryStore, window: int = 8, limit: int = 50) -> str:
    hop = detect_idea_hopping(store, window)
    projects = cross_project_completion(store, limit)

    lines = ["# Focus Guidance", "", "## Idea-hopping"]
    if not hop.available:
        lines.append(f"- Unavailable — {hop.reason}")
    elif hop.detected:
        lines.append(
            f"- **Detected** — {hop.reason}, across: {', '.join(sorted(hop.projects_involved))}"
        )
    else:
        lines.append(f"- Not detected — {hop.reason}")

    lines += ["", "## Project completion signals"]
    if not projects:
        lines.append("- No known projects recorded.")
    for entry in projects:
        signal = entry["signal"]
        if signal["available"]:
            lines.append(
                f"- **{entry['name']}**: {signal['label']} — "
                f"{signal['artifact_count']} artifact(s), "
                f"{signal['open_candidate_count']} open candidate(s)"
            )
        else:
            lines.append(f"- **{entry['name']}**: unavailable — {signal['reason']}")

    return "\n".join(lines)


__all__ = [
    "IdeaHopSignal",
    "cross_project_completion",
    "detect_idea_hopping",
    "render_focus_guidance",
]
