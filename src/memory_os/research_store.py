from __future__ import annotations

import json
from dataclasses import dataclass

from .core import MemoryStore, stable_id, utc_now
from .research_semantic import ResearchCandidate


@dataclass(frozen=True)
class PersistedResearchCandidate:
    candidate_id: str
    kind: str
    value: str
    status: str
    confidence: float
    evidence_count: int


def ensure_research_candidate_schema(store: MemoryStore) -> None:
    store.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS research_candidates (
            candidate_id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            value TEXT NOT NULL,
            normalized_value TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('candidate', 'accepted', 'rejected')),
            confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            UNIQUE(kind, normalized_value)
        );
        CREATE TABLE IF NOT EXISTS research_candidate_evidence (
            evidence_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            evidence TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            UNIQUE(candidate_id, source_url, content_hash, evidence)
        );
        """
    )
    # The original v0.6 schema omitted source_url from the evidence uniqueness
    # key. Preserve existing rows while upgrading that key so identical quoted
    # evidence from different sources retains both provenance trails.
    indexes = store.conn.execute("PRAGMA index_list(research_candidate_evidence)").fetchall()
    legacy_unique = False
    for index in indexes:
        if not index["unique"]:
            continue
        columns = [
            row["name"]
            for row in store.conn.execute(f"PRAGMA index_info([{index['name']}])").fetchall()
        ]
        if columns == ["candidate_id", "content_hash", "evidence"]:
            legacy_unique = True
            break
    if legacy_unique:
        store.conn.executescript(
            """
            ALTER TABLE research_candidate_evidence RENAME TO research_candidate_evidence_legacy;
            CREATE TABLE research_candidate_evidence (
                evidence_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                source_url TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                evidence TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                UNIQUE(candidate_id, source_url, content_hash, evidence)
            );
            INSERT OR IGNORE INTO research_candidate_evidence
                (evidence_id, candidate_id, source_url, content_hash, captured_at, evidence, metadata_json)
            SELECT evidence_id, candidate_id, source_url, content_hash, captured_at, evidence, metadata_json
            FROM research_candidate_evidence_legacy;
            DROP TABLE research_candidate_evidence_legacy;
            """
        )
    store.conn.commit()


def persist_research_candidates(
    store: MemoryStore, candidates: tuple[ResearchCandidate, ...] | list[ResearchCandidate]
) -> tuple[PersistedResearchCandidate, ...]:
    """Persist candidates while converging identical entities across sources.

    Candidate identity is ``kind + normalized value``. Evidence is stored
    separately, so deduplication never discards the source snapshot trail.
    Nothing is promoted to durable memory automatically.
    """
    ensure_research_candidate_schema(store)
    results: list[PersistedResearchCandidate] = []
    for candidate in candidates:
        if not candidate.value.strip():
            continue
        normalized = " ".join(candidate.value.split()).casefold()
        candidate_id = stable_id("research-candidate", candidate.kind, normalized)
        now = utc_now()
        row = store.conn.execute(
            "SELECT * FROM research_candidates WHERE candidate_id=?", (candidate_id,)
        ).fetchone()
        if row is None:
            store.conn.execute(
                "INSERT INTO research_candidates VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (candidate_id, candidate.kind, candidate.value.strip(), normalized,
                 "candidate", candidate.confidence, now, now,
                 json.dumps(candidate.metadata, sort_keys=True)),
            )
        else:
            confidence = max(float(row["confidence"]), candidate.confidence)
            metadata = {**json.loads(row["metadata_json"]), **candidate.metadata}
            store.conn.execute(
                "UPDATE research_candidates SET confidence=?, updated_at=?, metadata_json=? WHERE candidate_id=?",
                (confidence, now, json.dumps(metadata, sort_keys=True), candidate_id),
            )

        evidence_id = stable_id(
            "research-evidence", candidate_id, candidate.source_url,
            candidate.content_hash, candidate.evidence,
        )
        store.conn.execute(
            "INSERT OR IGNORE INTO research_candidate_evidence VALUES (?, ?, ?, ?, ?, ?, ?)",
            (evidence_id, candidate_id, candidate.source_url, candidate.content_hash,
             candidate.captured_at, candidate.evidence,
             json.dumps({"provenance": "research_snapshot"}, sort_keys=True)),
        )
        evidence_count = store.conn.execute(
            "SELECT COUNT(*) FROM research_candidate_evidence WHERE candidate_id=?",
            (candidate_id,),
        ).fetchone()[0]
        results.append(PersistedResearchCandidate(
            candidate_id=candidate_id, kind=candidate.kind,
            value=candidate.value.strip(), status="candidate",
            confidence=max(float(row["confidence"]), candidate.confidence) if row else candidate.confidence,
            evidence_count=evidence_count,
        ))
    store.conn.commit()
    return tuple(results)


def list_research_candidates(store: MemoryStore, status: str = "candidate", limit: int = 50) -> list[dict[str, object]]:
    ensure_research_candidate_schema(store)
    if limit < 1:
        return []
    if status not in {"candidate", "accepted", "rejected", "all"}:
        raise ValueError("invalid research candidate status")
    where = "" if status == "all" else "WHERE status=?"
    params: tuple[object, ...] = () if status == "all" else (status,)
    rows = store.conn.execute(
        f"SELECT * FROM research_candidates {where} ORDER BY updated_at DESC LIMIT ?",
        (*params, limit),
    ).fetchall()
    output: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json"))
        item["evidence_count"] = store.conn.execute(
            "SELECT COUNT(*) FROM research_candidate_evidence WHERE candidate_id=?",
            (row["candidate_id"],),
        ).fetchone()[0]
        output.append(item)
    return output


def list_research_candidate_evidence(store: MemoryStore, candidate_id: str) -> list[dict[str, object]]:
    ensure_research_candidate_schema(store)
    rows = store.conn.execute(
        "SELECT * FROM research_candidate_evidence WHERE candidate_id=? ORDER BY captured_at DESC",
        (candidate_id,),
    ).fetchall()
    return [{**dict(row), "metadata": json.loads(row["metadata_json"])} for row in rows]


def review_research_candidate(store: MemoryStore, candidate_id: str, decision: str) -> str:
    ensure_research_candidate_schema(store)
    if decision not in {"accepted", "rejected"}:
        raise ValueError("decision must be accepted or rejected")
    row = store.conn.execute(
        "SELECT status FROM research_candidates WHERE candidate_id=?", (candidate_id,)
    ).fetchone()
    if row is None:
        raise KeyError(candidate_id)
    if row["status"] != "candidate":
        raise ValueError("research candidate has already been reviewed")
    store.conn.execute(
        "UPDATE research_candidates SET status=?, updated_at=? WHERE candidate_id=?",
        (decision, utc_now(), candidate_id),
    )
    store.conn.commit()
    return candidate_id


__all__ = [
    "PersistedResearchCandidate", "ensure_research_candidate_schema",
    "list_research_candidate_evidence", "list_research_candidates",
    "persist_research_candidates", "review_research_candidate",
]
