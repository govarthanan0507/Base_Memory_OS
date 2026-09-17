# IMPL-04 PRD — Research Memory

**Version:** 0.5

## Product intent

Make external research traceable inside Personal Work Memory by turning sources into durable, deduplicated artifacts, preserving bounded evidence, and exposing reproducible structural observations before deeper semantic understanding.

## First user experience

1. Provide a research URL.
2. Normalize it into a canonical form.
3. Identify a conservative source category and URL-derived provider/resource hints.
4. Store the source as an artifact with provenance.
5. Optionally request bounded text capture.
6. Store the snapshot separately and attach its hash, capture time and location to the source artifact.
7. Inspect the captured evidence for reproducible title, heading and link observations.
8. Treat all observations as evidence, not verified conclusions.

The programmatic entry point for ingestion is `ingest_research_source()`. The CLI exposes the registration/capture boundary through `add-research-source` and `capture-research-source`. Structural inspection is currently a library-level operation over `SourceSnapshot`.

## Priorities

**P0:** canonical URL identity, artifact registration, provenance, deduplication.

**P1:** bounded source-content snapshots, content hashing, capture metadata, provider-specific URL adapters and explicit ingestion composition.

**P2:** deterministic structural evidence inspection, followed by semantic research summaries, citation graphs, idea/project linkage and cross-source synthesis.

## Product behavior

The system must make the provenance chain visible enough to answer: "What source did we record?" and, after capture, "What exact content snapshot did we store, when, and where?" It should also answer: "What reproducible structural signals were present in that snapshot?" without silently converting those signals into conclusions.

Registration and URL metadata are local observations; network capture is opt-in; snapshot persistence follows successful capture; structural inspection operates only on preserved evidence.

It must not imply that a fetched source is true or authoritative merely because HTTP retrieval succeeded, nor that a page title or link is a semantic endorsement of the linked resource.

## Constraints

Local-first, vendor-independent, source-preserving and evidence-oriented. Network capture is explicit rather than implicit. Capture is bounded and failures are surfaced. Structural extraction is deterministic and network-free. No credentials, access-control bypass or downloaded-code execution are part of this slice.
