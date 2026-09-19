"""Application service layer — the one place both the CLI and the
desktop GUI call into. Neither talks to `core.py`/`continuity.py`/etc.
directly any more; both go through `MemoryOSService`.

This exists because the GUI must not shell out to the CLI
(`GUI -> subprocess -> memory-os command`), and the CLI must not
duplicate logic the GUI also needs — both call the same functions
here, which in turn call the existing, unchanged core modules. No
core logic is rewritten by this file; it is a thin façade.

Two kinds of return value, deliberately:
- Methods ending in `_text` return the exact same rendered markdown
  strings the CLI has always printed (via the existing `render_*`
  functions) — nothing about that behavior changes.
- Other methods return plain dicts/lists/dataclasses, for a GUI to
  format however its own presentation layer wants (human-phrased
  labels, no raw IDs by default) without re-deriving the underlying
  query itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .candidates import persist_candidates
from .continuity import (
    project_completion_signal,
    project_context,
    render_project_reentry_brief,
    render_reentry_brief,
    submit_query,
)
from .continuity_os import render_continuity_dashboard
from .conversation import get_messages, list_conversations
from .core import Memory, MemoryStore
from .discovery import scan_workspace
from .emotional_signal import extract_behavioral_signal, render_behavioral_signal
from .evidence import link_conversation_to_project, record_conversation_candidates_as_project_events
from .focus_guidance import cross_project_completion, detect_idea_hopping, render_focus_guidance
from .importers import import_chatgpt_export as _import_chatgpt_export
from .importers import import_json, import_markdown
from .logging_setup import get_logger
from .project_classification import classify_artifacts_against_projects, list_candidate_details
from .project_evidence import render_project_evidence
from .timeline import render_project_timeline

logger = get_logger(__name__)


def default_data_dir() -> Path:
    """Per-user application-data directory, OS-appropriate. Windows:
    %LOCALAPPDATA%\\BaseMemoryOS; other platforms: ~/.local/share or
    ~/.memory-os as a sane fallback. Used when no explicit --db path
    is given, so a packaged desktop app never needs the user to name
    a file location on first launch.
    """
    import os

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "BaseMemoryOS"
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / "BaseMemoryOS"
    return Path.home() / ".local" / "share" / "BaseMemoryOS"


@dataclass(frozen=True)
class ProjectSummary:
    project_id: str
    name: str
    status: str
    confidence: float


class MemoryOSService:
    """Owns one `MemoryStore` and exposes every operation the CLI or
    GUI needs. Constructing this also runs `init` implicitly (
    `MemoryStore.__init__` already creates the schema if missing) —
    no separate manual init step for a caller to remember.
    """

    def __init__(self, db_path: str | Path | None = None, store: MemoryStore | None = None) -> None:
        # `store` lets a caller (tests, mainly) wrap an already-open
        # MemoryStore instead of this class opening its own — the
        # rest of this class behaves identically either way.
        if store is not None:
            self.store = store
            self.db_path = store.db_path
        else:
            self.db_path = Path(db_path) if db_path is not None else default_data_dir() / "memory.db"
            self.store = MemoryStore(self.db_path)

    def close(self) -> None:
        self.store.close()

    def __enter__(self) -> "MemoryOSService":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- Projects -----------------------------------------------------

    def list_projects(self, limit: int = 200) -> list[ProjectSummary]:
        return [
            ProjectSummary(row["project_id"], row["name"], row["status"], row["confidence"])
            for row in self.store.list_projects(limit=limit)
        ]

    def project_brief_text(self, project_id: str, limit: int = 50) -> str:
        return render_project_reentry_brief(self.store, project_id, limit)

    def project_completion(self, project_id: str) -> dict[str, Any]:
        return project_completion_signal(self.store, project_id)

    def project_context(self, project_id: str, limit: int = 50) -> dict[str, Any]:
        return project_context(self.store, project_id, limit)

    def scan_projects(self, root: str | Path) -> list[Any]:
        return scan_workspace(Path(root), self.store)

    # -- Conversations --------------------------------------------------

    def import_conversation(self, path: str | Path, *, fmt: str | None = None,
                             source: str = "local", title: str | None = None) -> str:
        path = Path(path)
        resolved_fmt = fmt or ("json" if path.suffix.lower() == ".json" else "markdown")
        if resolved_fmt == "json":
            return import_json(self.store, path)
        return import_markdown(self.store, path, source=source, title=title)

    def import_chatgpt_export(self, path: str | Path) -> int:
        return _import_chatgpt_export(self.store, Path(path))

    def list_conversations(self, limit: int = 50) -> list[Any]:
        return list_conversations(self.store, limit)

    def get_messages(self, conversation_id: str) -> list[Any]:
        return get_messages(self.store, conversation_id)

    def reentry_text(self, conversation_id: str, limit: int = 50) -> str:
        return render_reentry_brief(self.store, conversation_id, limit)

    def link_project_conversation(self, project_id: str, conversation_id: str) -> Any:
        return link_conversation_to_project(self.store, conversation_id, project_id)

    # -- Memories / candidates ------------------------------------------

    def add_memory(self, content: str, memory_type: str = "episodic",
                    source: str = "manual", confidence: float = 1.0) -> str:
        return self.store.add_memory(Memory(content, memory_type, source, confidence))

    def search_memories(self, query: str, limit: int = 20) -> list[Any]:
        return self.store.search(query, limit)

    def extract_candidates(self, conversation_id: str, project_id: str | None = None) -> list[str]:
        messages = get_messages(self.store, conversation_id)
        return persist_candidates(self.store, conversation_id, messages, project_id=project_id)

    def list_candidates(self, status: str = "candidate", limit: int = 50) -> list[Any]:
        return self.store.list_candidates(status, limit)

    def review_candidate(self, candidate_id: str, decision: str) -> Any:
        return self.store.review_candidate(candidate_id, decision)

    def project_evidence(self, conversation_id: str, project_id: str,
                          candidate_ids: list[str] | None = None) -> list[str]:
        return record_conversation_candidates_as_project_events(
            self.store, conversation_id, project_id, candidate_ids=candidate_ids
        )

    # -- Artifact/project classification (E2) ---------------------------

    def classify_folder(self, folder: str | Path) -> Any:
        return classify_artifacts_against_projects(Path(folder), self.store)

    def list_artifact_candidates(self, status: str = "candidate", limit: int = 50) -> list[Any]:
        return list_candidate_details(self.store, status=status, limit=limit)

    def review_artifact_candidate(self, candidate_id: str, decision: str) -> Any:
        return self.store.review_artifact_project_candidate(candidate_id, decision)

    # -- Chat routing (GUI's primary interaction) ------------------------

    def ask(self, text: str, *, project_id: str | None = None) -> str:
        """Route one chat message. If a project is scoped, the text is
        logged as a project event and the reply is that project's
        freshly-recomputed brief (so the reply visibly reflects the
        note just logged) — unchanged from the GUI's existing
        behavior, just relocated here so the CLI can use it too.
        Otherwise, routes through the existing name-matching
        `submit_query` — a text-match router, not semantic
        understanding; see `SEMANTIC_RETRIEVAL_DECISION.md` for why
        that boundary is honest, not glossed over.
        """
        if project_id:
            self.store.add_project_event(project_id, "chat_note", text)
            logger.info("service.ask: chat_note logged for project %s", project_id)
            return render_project_reentry_brief(self.store, project_id)
        logger.info("service.ask: submit_query(%r)", text)
        return submit_query(self.store, text)

    # -- Relations --------------------------------------------------------

    def relate(self, source_id: str, relation: str, target_id: str) -> None:
        self.store.relate(source_id, relation, target_id)

    # -- E4 / E5 ------------------------------------------------------------

    def emotional_signal(self, conversation_id: str) -> Any:
        return extract_behavioral_signal(self.store, conversation_id)

    def emotional_signal_text(self, conversation_id: str) -> str:
        return render_behavioral_signal(self.store, conversation_id)

    def focus_guidance(self, window: int = 8, limit: int = 50) -> tuple[Any, list[Any]]:
        return detect_idea_hopping(self.store, window), cross_project_completion(self.store, limit)

    def focus_guidance_text(self, window: int = 8, limit: int = 50) -> str:
        return render_focus_guidance(self.store, window=window, limit=limit)

    # -- Misc renders / dashboards ------------------------------------------

    def dashboard_text(self) -> str:
        return render_continuity_dashboard(self.store)

    def project_evidence_text(self, project_id: str, limit: int = 50) -> str:
        return render_project_evidence(self.store, project_id, limit)

    def project_timeline_text(self, project_id: str, limit: int = 100) -> str:
        return render_project_timeline(self.store, project_id, limit)


__all__ = ["MemoryOSService", "ProjectSummary", "default_data_dir"]
