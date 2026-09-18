from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(*parts: str) -> str:
    raw = "\x1f".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


@dataclass(frozen=True)
class Memory:
    content: str
    memory_type: str = "episodic"
    source: str = "manual"
    confidence: float = 1.0
    observed_at: str = field(default_factory=utc_now)
    memory_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Artifact:
    name: str
    artifact_type: str
    location: str
    artifact_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    content_hash: str | None = None
    modified_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Project:
    name: str
    root: str
    status: str = "DISCOVERED"
    confidence: float = 0.5
    project_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryCandidateRecord:
    content: str
    memory_type: str
    source: str
    source_message_id: str | None = None
    confidence: float = 0.5
    status: str = "candidate"
    observed_at: str = field(default_factory=utc_now)
    candidate_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    """Small SQLite-backed source of truth for the memory OS."""

    def __init__(self, db_path: str | Path = ".memory-os/memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self.conn.close()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY, content TEXT NOT NULL,
                memory_type TEXT NOT NULL, source TEXT NOT NULL,
                confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                observed_at TEXT NOT NULL, metadata_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memory_candidates (
                candidate_id TEXT PRIMARY KEY, content TEXT NOT NULL,
                memory_type TEXT NOT NULL, source TEXT NOT NULL,
                source_message_id TEXT, confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
                status TEXT NOT NULL CHECK(status IN ('candidate', 'accepted', 'rejected')),
                observed_at TEXT NOT NULL, metadata_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY, name TEXT NOT NULL, root TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL, confidence REAL NOT NULL,
                summary TEXT NOT NULL, metadata_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_events (
                event_id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
                event_type TEXT NOT NULL, timestamp TEXT NOT NULL,
                summary TEXT NOT NULL, metadata_json TEXT NOT NULL,
                UNIQUE(project_id, event_type, timestamp, summary)
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY, name TEXT NOT NULL, artifact_type TEXT NOT NULL,
                location TEXT NOT NULL UNIQUE, content_hash TEXT, modified_at TEXT,
                metadata_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS artifact_events (
                event_id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL,
                event_type TEXT NOT NULL, timestamp TEXT NOT NULL,
                old_hash TEXT, new_hash TEXT, old_modified_at TEXT, new_modified_at TEXT,
                metadata_json TEXT NOT NULL,
                UNIQUE(artifact_id, event_type, timestamp, old_hash, new_hash, old_modified_at, new_modified_at)
            );
            CREATE TABLE IF NOT EXISTS relations (
                relation_id TEXT PRIMARY KEY, source_id TEXT NOT NULL,
                relation TEXT NOT NULL, target_id TEXT NOT NULL,
                created_at TEXT NOT NULL, metadata_json TEXT NOT NULL,
                UNIQUE(source_id, relation, target_id)
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                memory_id UNINDEXED, content, memory_type, source
            );
            """
        )
        self.conn.commit()

    @staticmethod
    def _validate_confidence(confidence: float) -> None:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    @staticmethod
    def _validate_content(content: str) -> None:
        if not content.strip():
            raise ValueError("memory content must not be empty")

    def add_memory(self, memory: Memory) -> str:
        self._validate_confidence(memory.confidence)
        self._validate_content(memory.content)
        self.conn.execute(
            "INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?, ?, ?, ?)",
            (memory.memory_id, memory.content, memory.memory_type, memory.source,
             memory.confidence, memory.observed_at, json.dumps(memory.metadata, sort_keys=True)),
        )
        self.conn.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory.memory_id,))
        self.conn.execute("INSERT INTO memory_fts VALUES (?, ?, ?, ?)",
                          (memory.memory_id, memory.content, memory.memory_type, memory.source))
        self.conn.commit()
        return memory.memory_id

    def add_candidate(self, candidate: MemoryCandidateRecord) -> str:
        self._validate_confidence(candidate.confidence)
        if candidate.status not in {"candidate", "accepted", "rejected"}:
            raise ValueError("candidate status must be candidate, accepted, or rejected")
        self.conn.execute(
            "INSERT OR REPLACE INTO memory_candidates VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (candidate.candidate_id, candidate.content, candidate.memory_type, candidate.source,
             candidate.source_message_id, candidate.confidence, candidate.status,
             candidate.observed_at, json.dumps(candidate.metadata, sort_keys=True)),
        )
        self.conn.commit()
        return candidate.candidate_id

    def list_candidates(self, status: str = "candidate", limit: int = 50) -> list[sqlite3.Row]:
        if limit < 1:
            return []
        if status not in {"candidate", "accepted", "rejected", "all"}:
            raise ValueError("invalid candidate status")
        if status == "all":
            return list(self.conn.execute(
                "SELECT * FROM memory_candidates ORDER BY observed_at DESC LIMIT ?", (limit,)))
        return list(self.conn.execute(
            "SELECT * FROM memory_candidates WHERE status=? ORDER BY observed_at DESC LIMIT ?",
            (status, limit)))

    def review_candidate(self, candidate_id: str, decision: str) -> str:
        if decision not in {"accepted", "rejected"}:
            raise ValueError("decision must be accepted or rejected")
        row = self.conn.execute("SELECT * FROM memory_candidates WHERE candidate_id=?", (candidate_id,)).fetchone()
        if row is None:
            raise KeyError(candidate_id)
        if row["status"] != "candidate":
            raise ValueError("candidate has already been reviewed")
        self.conn.execute("UPDATE memory_candidates SET status=? WHERE candidate_id=?", (decision, candidate_id))
        if decision == "accepted":
            memory = Memory(content=row["content"], memory_type=row["memory_type"],
                            source=f"candidate:{candidate_id}", confidence=row["confidence"],
                            observed_at=row["observed_at"], metadata={**json.loads(row["metadata_json"]),
                                                                       "candidate_id": candidate_id,
                                                                       "source_message_id": row["source_message_id"]})
            self.add_memory(memory)
        self.conn.commit()
        return candidate_id

    def add_project_event(self, project_id: str, event_type: str, summary: str,
                          timestamp: str | None = None,
                          metadata: dict[str, Any] | None = None) -> str:
        if not event_type.strip() or not summary.strip():
            raise ValueError("event_type and summary must be non-empty")
        event_timestamp = timestamp or utc_now()
        event_id = stable_id(project_id, event_type.strip(), event_timestamp, summary.strip())
        self.conn.execute(
            "INSERT OR IGNORE INTO project_events VALUES (?, ?, ?, ?, ?, ?)",
            (event_id, project_id, event_type.strip(), event_timestamp, summary.strip(),
             json.dumps(metadata or {}, sort_keys=True)),
        )
        self.conn.commit()
        return event_id

    def list_project_events(self, project_id: str, limit: int = 100) -> list[sqlite3.Row]:
        if limit < 1:
            return []
        return list(self.conn.execute(
            "SELECT * FROM project_events WHERE project_id=? ORDER BY timestamp DESC LIMIT ?",
            (project_id, limit)))

    def add_project(self, project: Project) -> str:
        self._validate_confidence(project.confidence)
        existing = self.conn.execute(
            "SELECT * FROM projects WHERE root = ?", (project.root,)
        ).fetchone()
        now = utc_now()
        if existing:
            project_id = existing["project_id"]
            old_status = existing["status"]
            self.conn.execute(
                "UPDATE projects SET name=?, status=?, confidence=?, summary=?, metadata_json=? WHERE project_id=?",
                (project.name, project.status, project.confidence, project.summary,
                 json.dumps(project.metadata, sort_keys=True), project_id),
            )
            if old_status != project.status:
                self.add_project_event(
                    project_id, "status_change",
                    f"Project status changed: {old_status} → {project.status}", now,
                    {"from_status": old_status, "to_status": project.status},
                )
        else:
            project_id = project.project_id
            self.conn.execute(
                "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, project.name, project.root, project.status, project.confidence,
                 project.summary, json.dumps(project.metadata, sort_keys=True)),
            )
            self.add_project_event(
                project_id, "project_created", f"Project recorded: {project.name}", now,
                {"status": project.status, "root": project.root},
            )
        self.conn.commit()
        return project_id

    def add_artifact(self, artifact: Artifact) -> str:
        existing = self.conn.execute("SELECT * FROM artifacts WHERE location = ?", (artifact.location,)).fetchone()
        if existing:
            artifact_id = existing["artifact_id"]
            changed = (existing["content_hash"] != artifact.content_hash or
                       existing["modified_at"] != artifact.modified_at)
            self.conn.execute(
                "UPDATE artifacts SET name=?, artifact_type=?, content_hash=?, modified_at=?, metadata_json=? WHERE artifact_id=?",
                (artifact.name, artifact.artifact_type, artifact.content_hash, artifact.modified_at,
                 json.dumps(artifact.metadata, sort_keys=True), artifact_id),
            )
            if changed:
                self.add_artifact_event(
                    artifact_id,
                    "changed",
                    existing["content_hash"], artifact.content_hash,
                    existing["modified_at"], artifact.modified_at,
                    {"location": artifact.location},
                )
        else:
            artifact_id = artifact.artifact_id
            self.conn.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (artifact_id, artifact.name, artifact.artifact_type, artifact.location,
                 artifact.content_hash, artifact.modified_at, json.dumps(artifact.metadata, sort_keys=True)),
            )
            self.add_artifact_event(
                artifact_id, "discovered", None, artifact.content_hash, None, artifact.modified_at,
                {"location": artifact.location},
            )
        self.conn.commit()
        return artifact_id

    def add_artifact_event(self, artifact_id: str, event_type: str,
                           old_hash: str | None, new_hash: str | None,
                           old_modified_at: str | None, new_modified_at: str | None,
                           metadata: dict[str, Any] | None = None,
                           timestamp: str | None = None) -> str:
        event_timestamp = timestamp or utc_now()
        event_id = stable_id(artifact_id, event_type, event_timestamp,
                             old_hash or "", new_hash or "",
                             old_modified_at or "", new_modified_at or "")
        self.conn.execute(
            "INSERT OR IGNORE INTO artifact_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, artifact_id, event_type, event_timestamp, old_hash, new_hash,
             old_modified_at, new_modified_at, json.dumps(metadata or {}, sort_keys=True)),
        )
        self.conn.commit()
        return event_id

    def list_artifact_events(self, artifact_id: str, limit: int = 100) -> list[sqlite3.Row]:
        if limit < 1:
            return []
        return list(self.conn.execute(
            "SELECT * FROM artifact_events WHERE artifact_id=? ORDER BY timestamp DESC LIMIT ?",
            (artifact_id, limit)))

    def relate(self, source_id: str, relation: str, target_id: str,
               metadata: dict[str, Any] | None = None) -> None:
        if not relation.strip():
            raise ValueError("relation must be non-empty")
        self.conn.execute(
            "INSERT OR IGNORE INTO relations VALUES (?, ?, ?, ?, ?, ?)",
            (stable_id(source_id, relation, target_id), source_id, relation.strip(), target_id,
             utc_now(), json.dumps(metadata or {}, sort_keys=True)),
        )
        self.conn.commit()

    def related(self, entity_id: str, relation: str | None = None) -> list[sqlite3.Row]:
        if relation is None:
            return list(self.conn.execute(
                "SELECT * FROM relations WHERE source_id=? OR target_id=? ORDER BY created_at",
                (entity_id, entity_id)))
        return list(self.conn.execute(
            "SELECT * FROM relations WHERE (source_id=? OR target_id=?) AND relation=? ORDER BY created_at",
            (entity_id, entity_id, relation)))

    def search(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        if limit < 1:
            return []
        try:
            return list(self.conn.execute(
                "SELECT m.* FROM memory_fts f JOIN memories m ON m.memory_id=f.memory_id "
                "WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?", (query, limit)))
        except sqlite3.OperationalError:
            term = f"%{query}%"
            return list(self.conn.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY observed_at DESC LIMIT ?",
                (term, limit)))

    def list_projects(self, limit: int = 50) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM projects ORDER BY rowid DESC LIMIT ?", (limit,)))

    def list_artifacts(self, limit: int = 100) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM artifacts ORDER BY rowid DESC LIMIT ?", (limit,)))

    def list_memories(self, limit: int = 50) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM memories ORDER BY observed_at DESC LIMIT ?", (limit,)))

    def counts(self) -> dict[str, int]:
        return {table: self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("memories", "memory_candidates", "projects", "project_events", "artifacts", "artifact_events", "relations")}


__all__ = ["Artifact", "Memory", "MemoryCandidateRecord", "MemoryStore", "Project", "stable_id", "utc_now"]
