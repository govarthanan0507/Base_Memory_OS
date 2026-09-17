# IMPL-04 TRD — Research Memory

**Version:** 0.9

## Paths

- `src/memory_os/research.py` — URL normalization, classification and source registration
- `src/memory_os/research_content.py` — bounded capture, hashing, snapshot persistence and provenance attachment
- `src/memory_os/research_metadata.py` — URL-only provider/resource hints
- `src/memory_os/research_pipeline.py` — source-ingestion orchestration
- `src/memory_os/research_extract.py` — deterministic structural observations
- `src/memory_os/research_semantic.py` — conservative provenance-bound candidate extraction
- `src/memory_os/research_registry.py` — persistent cross-source candidate/entity deduplication, evidence multiplicity and review lifecycle
- `tests/test_research_registry.py` — cross-source deduplication and review tests
- `tests/test_research_provenance_chain.py` — end-to-end snapshot provenance regression
- `tests/test_research_semantic_pipeline.py` — source → snapshot → observations → candidates integration
- `tests/test_research*.py` — lower-level research behavior tests
- `src/memory_os/core.py` — SQLite source of truth and stable IDs

## Registry data model

`research_entities` is the durable identity boundary. Identity is `stable_id("research-entity", kind, normalized_value)`, with a uniqueness constraint on `(kind, normalized_value)`. Status is `candidate`, `accepted` or `rejected`; review timestamp is retained.

`research_entity_evidence` is deliberately separate. Each row retains entity ID, source URL, snapshot content hash, capture timestamp, exact evidence text, confidence and candidate metadata. `(entity_id, content_hash, evidence)` is unique, so the same occurrence can be safely re-persisted while independent sources remain visible.

This creates the required shape:

```text
SOURCE A ──┐
           ├──> RESEARCH ENTITY (deduplicated identity)
SOURCE B ──┘          │
                      ├── evidence A / snapshot A
                      └── evidence B / snapshot B
```

## Processing pipeline

```text
ResearchSource
 ↓
register_research_source()
 ↓
extract_source_metadata()
 ↓
optional capture_text()
 ↓
SourceSnapshot
 ↓
extract_observations()
 ↓
extract_semantic_candidates()
 ↓
register_research_candidates()
 ↓
review_research_entity()
```

Registration and candidate persistence use SQLite transactions. Duplicate identity and duplicate evidence are ignored rather than multiplied. Review only changes research-entity status and never writes to the general `memories` table.

## Evidence semantics

URL classification and metadata are observations. Snapshots are preserved evidence. Structural observations are deterministic interpretations of captured structure. Semantic candidates are heuristic, reviewable intermediates. Acceptance is a human review state, not source verification and not automatic durable-memory admission.

No network access occurs during structural extraction, semantic extraction or candidate persistence. Downloaded content is never executed.

## Verification

The research registry tests verify cross-source identity convergence, distinct evidence retention, kind separation, idempotent persistence and explicit review without durable-memory creation. The full provenance-chain regression verifies source URL, snapshot hash and capture timestamp continuity. Corrected-head workflow run #224 (`35184592014`) passed Python 3.11, 3.12, 3.13 and 3.14.

## Future extension points

Model-assisted extraction can feed the same `ResearchCandidate` contract. Later work can add explicit claim nodes, project/idea linkage and richer provider adapters without changing the evidence boundary.
