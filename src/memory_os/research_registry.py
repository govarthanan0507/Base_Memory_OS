from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

from .core import MemoryStore, stable_id, utc_now
from .research_semantic import ResearchCandidate


@dataclass(frozen=True)
class ResearchEntity:
    entity_id: str
    kind: str
    value: str


def ensure_research_registry(store: MemoryStore) -> None:
    store.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS research_entities (
            entity_id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            normalized_value TEXT NOT NULL,
            display_value TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'candidate'
                CHECK(status IN ('candidate', 'accepted', 'rejected')),
            created_at TEXT NOT NULL,
            reviewed_at TEXT,
            UNIQUE(kind, normalized_value)
        );
        CREATE TABLE IF NOT EXISTS research_entity_evidence (
            evidence_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            evidence TEXT NOT NULL,
            confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
            metadata_json TEXT NOT NULL,
            UNIQUE(entity_id, content_hash, evidence)
        );
        """
    )
    store.conn.commit()


def register_research_candidates(store: MemoryStore, candidates: Iterable[ResearchCandidate]) -> tuple[ResearchEntity, ...]:
    """Deduplicate candidates while retaining every distinct evidence trail."""
    ensure_research_registry(store)
    entities: dict[tuple[str, str], ResearchEntity] = {}
    for candidate in candidates:
        if not candidate.kind.strip() or not candidate.value.strip():
            continue
        kind = candidate.kind.strip().lower()
        normalized = " ".join(candidate.value.split()).casefold()
        entity_id = stable_id("research-entity", kind, normalized)
        store.conn.execute(
            "INSERT OR IGNORE INTO research_entities "
            "(entity_id, kind, normalized_value, display_value, status, created_at) VALUES (?, ?, ?, ?, 'candidate', ?)",
            (entity_id, kind, normalized, candidate.value.strip(), utc_now()),
        )
        evidence_id = stable_id("research-evidence", entity_id, candidate.content_hash, candidate.evidence)
        store.conn.execute(
            "INSERT OR IGNORE INTO research_entity_evidence "
            "(evidence_id, entity_id, source_url, content_hash, captured_at, evidence, confidence, metadata_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (evidence_id, entity_id, candidate.source_url, candidate.content_hash,
             candidate.captured_at, candidate.evidence, candidate.confidence,
             json.dumps(candidate.metadata, sort_keys=True)),
        )
        row = store.conn.execute("SELECT kind, display_value FROM research_entities WHERE entity_id=?", (entity_id,)).fetchone()
        entities[(kind, normalized)] = ResearchEntity(entity_id, row["kind"], row["display_value"])
    store.conn.commit()
    return tuple(entities.values())


def review_research_entity(store: MemoryStore, entity_id: str, decision: str) -> str:
    """Accept or reject a research candidate without creating durable memory."""
    if decision not in {"accepted", "rejected"}:
        raise ValueError("decision must be accepted or rejected")
    ensure_research_registry(store)
    row = store.conn.execute("SELECT status FROM research_entities WHERE entity_id=?", (entity_id,)).fetchone()
    if row is None:
        raise KeyError(entity_id)
    if row["status"] != "candidate":
        raise ValueError("research entity has already been reviewed")
    store.conn.execute("UPDATE research_entities SET status=?, reviewed_at=? WHERE entity_id=?", (decision, utc_now(), entity_id))
    store.conn.commit()
    return entity_id


def list_research_entities(store: MemoryStore, status: str = "candidate", limit: int = 50) -> list[dict[str, object]]:
    if limit < 1:
        return []
    if status not in {"candidate", "accepted", "rejected", "all"}:
        raise ValueError("invalid research entity status")
    ensure_research_registry(store)
    if status == "all":
        rows = store.conn.execute("SELECT * FROM research_entities ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    else:
        rows = store.conn.execute("SELECT * FROM research_entities WHERE status=? ORDER BY created_at DESC LIMIT ?", (status, limit)).fetchall()
    return [dict(row) for row in rows]


def list_research_entity_evidence(store: MemoryStore, entity_id: str) -> list[dict[str, object]]:
    ensure_research_registry(store)
    rows = store.conn.execute("SELECT * FROM research_entity_evidence WHERE entity_id=? ORDER BY captured_at DESC", (entity_id,)).fetchall()
    return [dict(row) for row in rows]


__all__ = ["ResearchEntity", "ensure_research_registry", "list_research_entities", "list_research_entity_evidence", "register_research_candidates", "review_research_entity"]
