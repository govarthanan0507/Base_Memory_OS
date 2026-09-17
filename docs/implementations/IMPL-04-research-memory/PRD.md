# IMPL-04 PRD — Research Memory

**Version:** 0.9

## Product intent

Make external research traceable inside Personal Work Memory by turning sources into durable, deduplicated artifacts, preserving bounded evidence, exposing reproducible structural observations, and producing conservative reviewable candidates before deeper semantic understanding. Repeated candidates discovered through multiple sources converge without losing provenance.

## First user experience

1. Provide a research URL.
2. Normalize it into a canonical form.
3. Identify a conservative source category and URL-derived provider/resource hints.
4. Store the source as an artifact with provenance.
5. Optionally request bounded text capture.
6. Store the snapshot separately and attach its hash, capture time and location to the source artifact.
7. Inspect captured evidence for reproducible title, heading and link observations.
8. Extract candidate repositories, tools, ideas and topics from preserved evidence.
9. Persist candidates using deterministic kind + normalized-value identity.
10. Retain each distinct source/snapshot/evidence occurrence beneath the shared candidate.
11. Review candidates before they become durable memory or graph claims.
12. Follow every candidate back to the exact source snapshot(s) that produced it.

Programmatic entry points: `ingest_research_source()`, `extract_observations()`, `extract_semantic_candidates()`, and `register_research_candidates()` / `review_research_entity()`.

## Priorities

**P0:** canonical source identity, artifact registration, provenance and deduplication.

**P1:** bounded evidence snapshots, hashing, capture metadata, URL adapters and explicit ingestion.

**P2:** deterministic structural evidence and provenance-bound candidate extraction.

**P3:** persistent cross-source candidate identity, evidence multiplicity and explicit candidate review.

**P4:** model-assisted summaries, citation graphs, idea/project linkage and cross-source synthesis after the evidence/review boundary is stable.

## Product behavior

The system makes the provenance chain inspectable: source → snapshot → observations → candidates → shared research entity → evidence occurrences. Candidate identity is shared across sources, while each source occurrence remains independently traceable.

Registration and URL metadata are local observations; network capture is opt-in; structural inspection and candidate extraction operate only on preserved evidence.

A candidate is an intermediate research record, not a verified fact. Persistent identity is based on kind + normalized value. Candidate review supports accepted/rejected state without automatically creating a general durable memory record.

## Constraints

Local-first, vendor-independent, source-preserving and evidence-oriented. Capture is bounded and failures are surfaced. Structural and candidate extraction are deterministic and network-free. Candidate persistence is SQLite-backed through the existing MemoryStore connection. Tests use platform-independent temporary storage. No credentials, access-control bypass or downloaded-code execution are part of this slice.
