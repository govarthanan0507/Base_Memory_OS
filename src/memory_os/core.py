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


class MemoryStore:
    """Small SQLite-backed source of truth for IMPL-01."""

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
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY, name TEXT NOT NULL, root TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL, confidence REAL NOT NULL,
                summary TEXT NOT NULL, metadata_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY, name TEXT NOT NULL, artifact_type TEXT NOT NULL,
                location TEXT NOT NULL UNIQUE, content_hash TEXT, modified_at TEXT,
                metadata_json TEXT NOT NULL
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

    def add_memory(self, memory: Memory) -> str:
        self._validate_confidence(memory.confidence)
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

    def add_project(self, project: Project) -> str:
        self._validate_confidence(project.confidence)
        existing = self.conn.execute("SELECT project_id FROM projects WHERE root = ?", (project.root,)).fetchone()
        if existing:
            project_id = existing[0]
            self.conn.execute(
                """UPDATE projects SET name=?, status=?, confidence=?, summary=?, metadata_json=?
                   WHERE project_id=?""",
                (project.name, project.status, project.confidence, project.summary,
                 json.dumps(project.metadata, sort_keys=True), project_id),
            )
        else:
            project_id = project.project_id
            self.conn.execute(
                "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, project.name, project.root, project.status, project.confidence,
                 project.summary, json.dumps(project.metadata, sort_keys=True)),
            )
        self.conn.commit()
        return project_id

    def add_artifact(self, artifact: Artifact) -> str:
        existing = self.conn.execute("SELECT artifact_id FROM artifacts WHERE location = ?", (artifact.location,)).fetchone()
        if existing:
            artifact_id = existing[0]
            self.conn.execute(
                """UPDATE artifacts SET name=?, artifact_type=?, content_hash=?, modified_at=?, metadata_json=?
                   WHERE artifact_id=?""",
                (artifact.name, artifact.artifact_type, artifact.content_hash, artifact.modified_at,
                 json.dumps(artifact.metadata, sort_keys=True), artifact_id),
            )
        else:
            artifact_id = artifact.artifact_id
            self.conn.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (artifact_id, artifact.name, artifact.artifact_type, artifact.location,
                 artifact.content_hash, artifact.modified_at, json.dumps(artifact.metadata, sort_keys=True)),
            )
        self.conn.commit()
        return artifact_id

    def relate(self, source_id: str, relation: str, target_id: str,
               metadata: dict[str, Any] | None = None) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO relations VALUES (?, ?, ?, ?, ?, ?)",
            (stable_id(source_id, relation, target_id), source_id, relation, target_id,
             utc_now(), json.dumps(metadata or {}, sort_keys=True)),
        )
        self.conn.commit()

    def search(self, query: str, limit: int = 20) -> list[sqlite3.Row]:
        try:
            return list(self.conn.execute(
                "SELECT m.* FROM memory_fts f JOIN memories m ON m.memory_id=f.memory_id "
                "WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?", (query, limit)))
        except sqlite3.OperationalError:
            term = f"%{query}%"
            return list(self.conn.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY observed_at DESC LIMIT ?",
                (term, limit)))

    def counts(self) -> dict[str, int]:
        return {table: self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("memories", "projects", "artifacts", "relations")}


__all__ = ["Artifact", "Memory", "MemoryStore", "Project", "stable_id", "utc_now"]
