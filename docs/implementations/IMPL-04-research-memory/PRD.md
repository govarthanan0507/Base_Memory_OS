# IMPL-04 PRD — Research Memory

**Version:** 0.8

## Product intent

Make external research traceable inside Personal Work Memory by turning sources into durable, deduplicated artifacts, preserving bounded evidence, exposing reproducible structural observations, and producing conservative reviewable candidates before deeper semantic understanding. Repeated candidates discovered through multiple sources must converge without losing provenance.

## First user experience

1. Provide a research URL.
2. Normalize it into a canonical form.
3. Identify a conservative source category and URL-derived provider/resource hints.
4. Store the source as an artifact with provenance.
5. Optionally request bounded text capture.
6. Store the snapshot separately and attach its hash, capture time and location to the source artifact.
7. Inspect the captured evidence for reproducible title, heading and link observations.
8. Extract candidate repositories, tools, ideas and topics from the preserved evidence.
9. Persist candidates using deterministic kind + normalized-value identity.
10. Retain each distinct source/snapshot/evidence occurrence beneath the shared candidate.
11. Review candidates before they become durable memory or graph claims.
12. Follow every candidate back to the exact source snapshot(s) that produced it.

The programmatic entry point for ingestion is `ingest_research_source()`. Structural inspection is `extract_observations()`, the semantic-candidate boundary is `extract_semantic_candidates()`, and durable candidate storage is provided by `research_store.py`.

## Priorities

**P0:** canonical URL identity, artifact registration, provenance, deduplication.

**P1:** bounded source-content snapshots, content hashing, capture metadata, provider-specific URL adapters and explicit ingestion composition.

**P2:** deterministic structural evidence inspection, provenance-bound candidate extraction and end-to-end provenance-chain verification.

**P3:** persistent cross-source candidate identity, evidence multiplicity and explicit candidate review.

**P4:** model-assisted semantic summaries, citation graphs, idea/project linkage and cross-source synthesis after the candidate/review boundary is stable.

## Product behavior

The system must make the provenance chain visible enough to answer: "What source did we record?" and, after capture, "What exact content snapshot did we store, when, and where?" It should also answer: "What reproducible structural signals and candidate references were present in that snapshot?" and "Which other sources independently produced the same candidate?" without silently converting candidates into conclusions.

Registration and URL metadata are local observations; network capture is opt-in; snapshot persistence follows successful capture; structural inspection and candidate extraction operate only on preserved evidence.

A candidate is an intermediate research record, not a verified fact. Candidate generation must be conservative, deterministic and traceable. Persistent candidate identity is based on kind + normalized value. Evidence occurrences remain separate, so deduplication removes duplicate entity records rather than source history.

Candidate review is explicit. Accepted/rejected research-candidate status does not automatically create a general durable memory record.

The provenance-chain test is itself product protection: it ensures a future refactor cannot accidentally detach a candidate from the evidence that produced it.

## Constraints

Local-first, vendor-independent, source-preserving and evidence-oriented. Network capture is explicit rather than implicit. Capture is bounded and failures are surfaced. Structural and candidate extraction are deterministic and network-free. Candidate persistence is SQLite-backed through the existing MemoryStore connection. Tests must use platform-independent temporary storage. No credentials, access-control bypass or downloaded-code execution are part of this slice.
