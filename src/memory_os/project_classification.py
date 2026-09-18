from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .core import Artifact, ArtifactProjectCandidateRecord, MemoryStore
from .discovery import CODE_EXTENSIONS, IGNORED_DIRS, MAX_ANALYSIS_BYTES, MAX_HASH_BYTES, file_hash
from .logging_setup import get_logger

logger = get_logger(__name__)

# Text-readable extensions eligible for a content-snippet signal, per
# E2_TRD.md's security requirement: never read binary content, and only
# under MAX_HASH_BYTES (reused from discovery.py's own cap).
TEXT_EXTENSIONS = CODE_EXTENSIONS | {".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".csv", ".cfg", ".ini"}

# Below this, a project match is not proposed at all (E2_FRD.md #6 —
# "unclassified", never a forced low-confidence guess).
FLOOR_CONFIDENCE = 0.3

_TOKEN_RE = re.compile(r"[^a-zA-Z0-9]+")


def _tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.split(text.lower()) if len(t) > 2}


def _project_tokens(store: MemoryStore, project_row) -> set[str]:
    tokens = _tokenize(project_row["name"]) | _tokenize(Path(project_row["root"]).name)
    for row in store.conn.execute(
        "SELECT a.name FROM artifacts a JOIN relations r ON r.target_id = a.artifact_id "
        "WHERE r.source_id = ? AND r.relation = 'contains'",
        (project_row["project_id"],),
    ):
        tokens |= _tokenize(row["name"])
    return tokens


def _score(filename_tokens: set[str], parent_tokens: set[str], content_tokens: set[str],
           project_tokens: set[str]) -> float:
    score = 0.0
    if filename_tokens & project_tokens:
        score += 0.4
    if parent_tokens & project_tokens:
        score += 0.3
    if content_tokens & project_tokens:
        score += 0.3
    return min(score, 0.95)


def _resolves_within(path: Path, root: Path) -> Path | None:
    """Resolve a symlink and return the target only if it stays within root."""
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if resolved == root or root in resolved.parents:
        return resolved
    return None


@dataclass(frozen=True)
class ClassificationResult:
    candidates_created: int = 0
    artifacts_registered: int = 0
    unclassified_count: int = 0
    skipped: list[str] = field(default_factory=list)


def classify_artifacts_against_projects(folder: str | Path, store: MemoryStore) -> ClassificationResult:
    """Scan a user-designated folder and propose artifact-project candidates.

    Per E2_FRD.md/E2_TRD.md: read-only, folder-scoped (never a blanket
    scan), propose-then-confirm only (no `relate()` call happens here —
    that's `MemoryStore.review_artifact_project_candidate`'s job, only
    after explicit user acceptance).
    """
    root = Path(folder).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"not a directory: {root}")

    projects = list(store.conn.execute("SELECT * FROM projects"))
    candidates_created = 0
    artifacts_registered = 0
    unclassified_count = 0
    skipped: list[str] = []

    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)

        kept_dirs = []
        for d in dirs:
            if d in IGNORED_DIRS:
                continue
            dir_path = current_path / d
            if dir_path.is_symlink() and _resolves_within(dir_path, root) is None:
                logger.warning("classify-folder: skipping symlink escaping scan root: %s", dir_path)
                skipped.append(str(dir_path))
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for name in names:
            path = current_path / name
            if path.is_symlink() and _resolves_within(path, root) is None:
                logger.warning("classify-folder: skipping symlink escaping scan root: %s", path)
                skipped.append(str(path))
                continue
            try:
                stat = path.stat()
                content_hash = file_hash(path) if stat.st_size <= MAX_HASH_BYTES else None
            except OSError as exc:
                logger.warning("classify-folder: skipping unreadable file %s: %s", path, exc)
                skipped.append(str(path))
                continue

            artifact = Artifact(
                name,
                "code" if path.suffix.lower() in CODE_EXTENSIONS else "file",
                str(path),
                content_hash=content_hash,
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                metadata={"scanned_from": str(root)},
            )
            artifact_id = store.add_artifact(artifact)
            artifacts_registered += 1

            filename_tokens = _tokenize(path.stem)
            parent_tokens = _tokenize(path.parent.name)
            content_tokens: set[str] = set()
            if path.suffix.lower() in TEXT_EXTENSIONS and stat.st_size <= MAX_HASH_BYTES:
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")[:MAX_ANALYSIS_BYTES]
                    content_tokens = _tokenize(text)
                except OSError as exc:
                    logger.warning("classify-folder: could not read content of %s: %s", path, exc)

            matched_any = False
            for project_row in projects:
                score = _score(filename_tokens, parent_tokens, content_tokens,
                                _project_tokens(store, project_row))
                if score < FLOOR_CONFIDENCE:
                    continue
                store.add_artifact_project_candidate(ArtifactProjectCandidateRecord(
                    artifact_id=artifact_id,
                    project_id=project_row["project_id"],
                    confidence=score,
                    metadata={"content_hash": content_hash},
                ))
                candidates_created += 1
                matched_any = True
            if not matched_any:
                unclassified_count += 1

    return ClassificationResult(
        candidates_created=candidates_created,
        artifacts_registered=artifacts_registered,
        unclassified_count=unclassified_count,
        skipped=skipped,
    )


def list_candidate_details(store: MemoryStore, status: str = "candidate", limit: int = 50) -> list[dict]:
    """`list_artifact_project_candidates`, enriched with artifact/project
    names for display — the shape `UI_TRD.md`'s `start_scan` return
    value specifies (name/name/confidence/candidate_id), not just raw
    IDs. Read-only; never modifies a candidate's review status.
    """
    details = []
    for row in store.list_artifact_project_candidates(status, limit):
        artifact = store.conn.execute(
            "SELECT name FROM artifacts WHERE artifact_id=?", (row["artifact_id"],)
        ).fetchone()
        project = store.conn.execute(
            "SELECT name FROM projects WHERE project_id=?", (row["project_id"],)
        ).fetchone()
        details.append({
            "candidate_id": row["candidate_id"],
            "artifact_name": artifact["name"] if artifact else row["artifact_id"],
            "project_name": project["name"] if project else row["project_id"],
            "confidence": row["confidence"],
            "status": row["status"],
        })
    return details


__all__ = [
    "ClassificationResult",
    "classify_artifacts_against_projects",
    "list_candidate_details",
    "FLOOR_CONFIDENCE",
]
