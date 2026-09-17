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
            created_at TEXT NOT NULL,
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


def register_research_candidates(
    store: MemoryStore, candidates: Iterable[ResearchCandidate]
) -> tuple[ResearchEntity, ...]:
    """Deduplicate semantic candidates while retaining every distinct evidence trail."""
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
            "(entity_id, kind, normalized_value, display_value, created_at) VALUES (?, ?, ?, ?, ?)",
            (entity_id, kind, normalized, candidate.value.strip(), utc_now()),
        )
        evidence_id = stable_id(
            "research-evidence", entity_id, candidate.content_hash, candidate.evidence
        )
        store.conn.execute(
            "INSERT OR IGNORE INTO research_entity_evidence "
            "(evidence_id, entity_id, source_url, content_hash, captured_at, evidence, confidence, metadata_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                evidence_id,
                entity_id,
                candidate.source_url,
                candidate.content_hash,
                candidate.captured_at,
                candidate.evidence,
                candidate.confidence,
                json.dumps(candidate.metadata, sort_keys=True),
            ),
        )
        entities[(kind, normalized)] = ResearchEntity(entity_id, kind, candidate.value.strip())
    store.conn.commit()
    return tuple(entities.values())


def list_research_entity_evidence(store: MemoryStore, entity_id: str) -> list[dict[str, object]]:
    ensure_research_registry(store)
    rows = store.conn.execute(
        "SELECT * FROM research_entity_evidence WHERE entity_id=? ORDER BY captured_at DESC",
        (entity_id,),
    ).fetchall()
    return [dict(row) for row in rows]


__all__ = [
    "ResearchEntity",
    "ensure_research_registry",
    "list_research_entity_evidence",
    "register_research_candidates",
]
