# IMPL-04 — Research Memory — Implementation Log

## 1. Purpose

Chronological engineering audit trail for IMPL-04. Failures remain visible; later fixes are recorded rather than rewriting history.

## 2. Starting state

IMPL-03 established project/file intelligence, artifact history, project timelines, explicit project↔conversation continuity and evidence-labelled project views. IMPL-04 began by establishing canonical external research-source identity.

---

## 3. Cycle v0.1 — Research source identity foundation

**Date:** 2026-09-17

**Objective:** establish deterministic external-source identity before attempting content understanding.

**Implementation paths:** `src/memory_os/research.py`, `tests/test_research.py`, IMPL-04 BRD/FRD/PRD/TRD.

**Implementation:** HTTP(S) URL normalization, conservative source classification, deterministic research artifact IDs, duplicate-safe artifact registration and provenance metadata.

**Failure:** `ResearchSource.source_type` initially defaulted to `website`, so normal construction bypassed automatic URL classification.

**Root cause:** the dataclass default encoded a concrete type before registration could inspect the URL.

**Fix:** default changed to empty string; registration classifies when the explicit type is blank.

**Regression test:** YouTube registration without an explicit type must produce `video`.

**Verification:** GitHub Actions run #164 (`35180978862`) passed on Python 3.11–3.14.

**Known limitations:** classification is heuristic; no external content capture or semantic interpretation.

---

## 4. Cycle v0.2 — Bounded source-content evidence

**Date:** 2026-09-17

**Objective:** add explicit, bounded content capture without turning retrieval into interpretation.

**Implementation:** `SourceSnapshot`, bounded standard-library HTTP capture, timeout and byte limits, charset-aware text decoding, SHA-256 content identity, content-hash-named JSON snapshot persistence and idempotent snapshot provenance attachment to research artifacts.

**Tests:** deterministic hashing, provenance-preserving persistence, idempotent attachment and oversized-response rejection.

**Known limitations:** text only; no provider metadata extraction; no semantic parsing; snapshots are filesystem JSON; network capture is explicit.

---

## 5. Cycle v0.3 — URL-only provider metadata hints

**Date:** 2026-09-17

**Objective:** add deterministic provider-neutral metadata extraction from URL structure only.

**Implementation:** added `extract_source_metadata()` recognizing YouTube watch/Shorts, `youtu.be`, GitHub and GitLab repository paths; unknown sites return canonical URL/host only.

**Failure:** one documentation update initially used a stale blob SHA and GitHub returned HTTP 409.

**Root cause:** the file had changed after the earlier fetch.

**Fix:** re-fetched the current file and retried with its current SHA.

**Verification:** implementation/test commits were accepted; CI result was to be recorded when available.

---

## 6. Cycle v0.4 — Explicit research ingestion pipeline

**Date:** 2026-09-17

**Objective:** compose source registration, URL metadata and optional bounded capture without collapsing evidence and interpretation.

**Implementation:** `ResearchIngestResult` plus `ingest_research_source()`. `capture=False` is network-free; `capture=True` requires a snapshot directory and performs bounded capture → hash-named persistence → provenance attachment.

**Tests:** offline registration, mocked end-to-end capture/provenance, required snapshot-directory validation.

**Verification:** workflow `tests`, run #186 (`35181985251`), passed across Python 3.11–3.14.

---

## 7. Cycle v0.5 — Research CLI boundary

**Date:** 2026-09-17

**Objective:** expose deterministic registration and explicit capture through the CLI.

**Implementation:** `add-research-source` and `capture-research-source`; the authoritative command implementation remains in `src/memory_os/cli.py`.

**Failure:** first implementation-log update returned GitHub HTTP 409 because the log blob changed after fetch.

**Root cause:** stale optimistic-concurrency SHA.

**Fix:** re-fetched the current log blob and retried.

**Known limitation:** `cli_research.py` remains as a helper/extraction experiment but is not the console entry point.

---

## 8. Cycle v0.6 — Deterministic structural evidence inspection

**Date:** 2026-09-17

**Objective:** extract reproducible title, heading, hyperlink and absolute-URL observations from captured evidence without network access.

**Implementation:** `src/memory_os/research_extract.py` and `tests/test_research_extract.py`. Relative links are resolved and normalized; duplicate observations preserve first-observed order; snapshot hash/timestamp remain provenance.

**Test failure:** CI run #200 (`35183355300`) failed in Python 3.12 because the test treated `::bad` as malformed even though URL resolution legitimately treats it as a relative reference.

**Root cause:** incorrect regression fixture, not a production defect.

**Fix:** replaced it with `https://[bad`. Remediation commit: `84290f3ee5d4f45dcf7296f8b38d587ee8fb954b`.

**Current verification:** no workflow run is currently associated with the remediation commit through the connected GitHub workflow lookup, so this is not claimed as CI-green. The failure remains recorded.

---

## 9. Cycle v0.7 — Provenance-bound semantic candidate layer

**Date:** 2026-09-17

**Starting state:** preserved snapshots could be structurally inspected, but there was no intermediate representation for the research-intake use case: identify referenced repositories/tools/ideas/topics while retaining exact evidence provenance.

**Objective:** create a deterministic semantic-candidate boundary that can later be replaced or augmented by an LLM without changing provenance semantics.

**Exact implementation paths:**
- `src/memory_os/research_semantic.py`
- `tests/test_research_semantic.py`
- `docs/implementations/IMPL-04-research-memory/BRD.md`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/PRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- `README.md`
- this log

**Implementation:** added `ResearchCandidate` and `extract_semantic_candidates()`. The extractor consumes a `SourceSnapshot` plus `ResearchObservations` and produces conservative candidates for GitHub/GitLab repositories, explicitly introduced tools, explicitly introduced ideas, and title/heading topics. Every candidate stores exact source URL, snapshot content hash, capture timestamp, evidence text, confidence and `review_status=candidate`. Duplicate repository references are collapsed within one result.

**Boundary rule:** candidates are not durable memories, verified claims, endorsements or project links. The implementation makes no network calls, invokes no LLM and executes no downloaded code.

**Tests added:** repository/tool/idea/topic extraction with provenance; duplicate repository reference deduplication; unknown-source behavior that does not invent provider metadata.

**Failure status:** no production failure observed in this cycle. CI verification of the new head is pending; no green result is claimed until GitHub Actions reports it.

**Known limitations:** textual patterns are intentionally narrow and heuristic. This is a staging boundary for future semantic/model-assisted extraction, not a complete natural-language understanding engine. The candidate layer currently does not persist candidates into the graph.

**Evidence commits:**
- semantic implementation `5ca23dfebac290aa9b8285605db3dba8c1aaf4f1`
- semantic tests `41746e5c2eb775ee64b703fb7983a8da9f1393fe`
- BRD v0.4 `4fec748de4a1394c66823619f83462a3e29b34a9`
- FRD v0.6 `d7eba1594b5bd976aa0dbc477c9e9232b713b8ce`
- PRD v0.6 `845c65f9aabadeda8f3a6351fd9d741975f6f300`
- TRD v0.6 `c12fa4a42022bc77b324a9df2fba0b50093bb2e5`

---

## 10. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | Source type default bypassed classification | Concrete dataclass default | Blank default + automatic classification | YouTube registration test |
| v0.2 | None observed | — | — | Snapshot/content-limit/idempotence tests |
| v0.3 | Documentation update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |
| v0.4 | None observed | — | — | Offline pipeline tests + capture=False no-network assertion |
| v0.5 | Log update returned GitHub 409 | Log changed between fetch and update | Re-fetched current blob SHA and retried | Fetch-before-update discipline |
| v0.6 | Structural extraction test rejected valid relative URL | Incorrect test fixture, not production defect | Replace with genuinely malformed absolute URL | Positive relative-link test + malformed-link regression |
| v0.7 | None observed | — | — | Provenance, deduplication and unknown-source tests |

## 11. Current evidence boundary

```text
URL
 ↓
CANONICAL SOURCE IDENTITY
 ↓
URL-DERIVED METADATA ── observation only
 ↓
OPTIONAL BOUNDED CAPTURE
 ↓
HASHED SNAPSHOT
 ↓
PRESERVED EVIDENCE
 ↓
STRUCTURAL OBSERVATION ── evidence-bound
 ↓
SEMANTIC CANDIDATES ── reviewable, provenance-bound
 ↓
DURABLE MEMORY / VERIFIED CLAIM ── not automatic
```

## 12. Next step

Verify the newest test-bearing head in CI. Then add a mixed-source integration path that demonstrates source → snapshot → observations → candidates, with repository/tool/entity records remaining deduplicated and traceable to exact evidence before moving toward model-assisted semantic extraction.
