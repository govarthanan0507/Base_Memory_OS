# IMPL-04 PRD — Research Memory

**Version:** 0.3

## Product intent

Make external research traceable inside Personal Work Memory by turning sources into durable, deduplicated artifacts and allowing explicit, bounded capture of source evidence before deeper understanding.

## First user experience

1. Provide a research URL.
2. Normalize it into a canonical form.
3. Identify a conservative source category and URL-derived provider/resource hints.
4. Store the source as an artifact with provenance.
5. Optionally request bounded text capture.
6. Store the snapshot separately and attach its hash, capture time and location to the source artifact.
7. Treat the snapshot as evidence, not a verified conclusion.

The programmatic entry point for this sequence is `ingest_research_source()`.

## Priorities

**P0:** canonical URL identity, artifact registration, provenance, deduplication.

**P1:** bounded source-content snapshots, content hashing, capture metadata, provider-specific URL adapters and explicit ingestion composition.

**P2:** semantic research summaries, citation graphs, idea/project linkage and cross-source synthesis.

## Product behavior

The system must make the provenance chain visible enough to answer: "What source did we record?" and, after capture, "What exact content snapshot did we store, when, and where?" The ingestion path must make the boundary explicit: registration and URL metadata are local observations; network capture is opt-in; snapshot persistence follows successful capture; provenance records the relationship.

It must not imply that a fetched source is true or authoritative merely because HTTP retrieval succeeded.

## Constraints

Local-first, vendor-independent, source-preserving and evidence-oriented. Network capture is explicit rather than implicit. Capture is bounded and failures are surfaced. No credentials, access-control bypass or downloaded-code execution are part of this slice.
