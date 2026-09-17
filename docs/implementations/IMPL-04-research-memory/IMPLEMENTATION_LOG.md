# IMPL-04 — Research Memory — Implementation Log

## 1. Purpose

Chronological engineering audit trail for IMPL-04. Failures remain visible; later fixes are recorded rather than rewriting history.

## 2. Starting state

IMPL-03 established project/file intelligence, artifact history, project timelines, explicit project↔conversation continuity and evidence-labelled project views. IMPL-04 began by establishing canonical external research-source identity.

---

## 3. Cycle v0.1 — Research source identity foundation

**Date:** 2026-09-17

**Objective:** establish deterministic external-source identity before attempting content understanding.

**Implementation:** HTTP(S) URL normalization, conservative source classification, deterministic research artifact IDs, duplicate-safe artifact registration and provenance metadata.

**Failure:** `ResearchSource.source_type` initially defaulted to `website`, so normal construction bypassed automatic URL classification.

**Root cause:** the dataclass default encoded a concrete type before registration could inspect the URL.

**Fix:** default changed to empty string; registration classifies when the explicit type is blank.

**Regression test:** YouTube registration without an explicit type must produce `video`.

**Verification:** GitHub Actions run #164 (`35180978862`) passed on Python 3.11–3.14.

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

**Implementation:** `extract_source_metadata()` recognizes YouTube watch/Shorts, `youtu.be`, GitHub and GitLab repository paths; unknown sites return canonical URL/host only.

**Failure:** one documentation update initially used a stale blob SHA and GitHub returned HTTP 409.

**Root cause:** the file had changed after the earlier fetch.

**Fix:** re-fetched the current file and retried with its current SHA.

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

**Test failure:** CI run #200 (`35183355300`) failed in Python 3.12. The test used `::bad` as a malformed URL, but `urljoin()` correctly treated it as a relative reference.

**Root cause:** the fixture was not actually malformed for URL resolution. A later corrected fixture used `https://[bad`, which exposed a second, real robustness gap: Python's `urljoin()` can itself raise `ValueError` for malformed absolute references.

**Remediation sequence:**
1. Test fixture corrected in `84290f3ee5d4f45dcf7296f8b38d587ee8fb954b`.
2. Subsequent CI run #211 (`35184049758`) exposed the production exception gap.
3. Production code hardened in `ba8204e920136c0aee975dec8ab9d5b07e41ae0c` to ignore `TypeError`/`ValueError` from malformed link resolution/normalization.

**Regression protection:** positive relative-link coverage remains; malformed absolute links now exercise the production exception boundary.

---

## 9. Cycle v0.7 — Provenance-bound semantic candidate layer

**Date:** 2026-09-17

**Objective:** create a deterministic semantic-candidate boundary that can later be replaced or augmented by an LLM without changing provenance semantics.

**Exact implementation paths:** `src/memory_os/research_semantic.py`, `tests/test_research_semantic.py`, IMPL-04 BRD/FRD/PRD/TRD, `README.md` and this log.

**Implementation:** added `ResearchCandidate` and `extract_semantic_candidates()`. The extractor consumes a `SourceSnapshot` plus `ResearchObservations` and produces conservative candidates for GitHub/GitLab repositories, explicitly introduced tools, explicitly introduced ideas, and title/heading topics. Every candidate stores exact source URL, snapshot content hash, capture timestamp, evidence text, confidence and `review_status=candidate`. Duplicate repository references are collapsed within one result.

**Boundary rule:** candidates are not durable memories, verified claims, endorsements or project links. The implementation makes no network calls, invokes no LLM and executes no downloaded code.

**Tests added:** repository/tool/idea/topic extraction with provenance; duplicate repository reference deduplication; unknown-source behavior that does not invent provider metadata.

**Known limitations:** textual patterns are intentionally narrow and heuristic. The candidate layer does not yet persist candidates into the graph.

**Evidence commits:** semantic implementation `5ca23dfebac290aa9b8285605db3dba8c1aaf4f1`; semantic tests `41746e5c2eb775ee64b703fb7983a8da9f1393fe`.

---

## 10. Cycle v0.8 — Mixed-source provenance-chain integration

**Date:** 2026-09-17

**Objective:** prove the evidence-to-candidate chain as one offline integration behavior rather than only separate unit tests.

**Implementation:** `tests/test_research_semantic_pipeline.py` exercises source → snapshot → observations → candidates and asserts exact provenance plus distinct repository/tool/idea/topic outputs.

**Verification:** run #218 (`35184233434`) completed successfully across Python 3.11–3.14 for the integrated semantic pipeline head.

**Known limitation:** candidate records remain an in-memory intermediate representation; cross-source durable deduplication and review persistence are not yet implemented.

---

## 11. Cycle v0.9 — Provenance-chain regression hardening

**Date:** 2026-09-17

**Objective:** add an additional regression proving that persisted artifact snapshot provenance and emitted semantic candidates share the same exact evidence identity, while keeping the test portable across CI platforms.

**Implementation path:** `tests/test_research_provenance_chain.py`.

**Failure:** CI run #223 (`35184529309`) failed in Python 3.13 with `TypeError: ingest_research_source() got an unexpected keyword argument 'title'`.

**Root cause:** the new test incorrectly assumed the ingestion function accepted convenience keyword arguments; its API requires a `ResearchSource` object.

**Remediation:** test corrected in `b86ee0505639701a9073768bb57788370be453c1` to construct `ResearchSource` explicitly. The hard-coded `/tmp/...` snapshot path was also replaced with `tempfile.TemporaryDirectory()` so the regression is platform-independent.

**Production impact:** none. No production implementation was changed for this failure.

**Current verification:** corrected head CI run #224 (`35184592014`) is queued at this log update; no green result is claimed until its jobs complete.

---

## 12. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | Source type default bypassed classification | Concrete dataclass default | Blank default + automatic classification | YouTube registration test |
| v0.2 | None observed | — | — | Snapshot/content-limit/idempotence tests |
| v0.3 | Documentation update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |
| v0.4 | None observed | — | — | Offline pipeline tests + capture=False no-network assertion |
| v0.5 | Log update returned GitHub 409 | Log changed between fetch and update | Re-fetched current blob SHA and retried | Fetch-before-update discipline |
| v0.6 | Structural extraction test initially used a valid relative URL as malformed; corrected fixture then exposed uncaught `urljoin()` ValueError | Test fixture ambiguity followed by production exception gap | Correct fixture + catch URL resolution/normalization errors | Positive relative-link test + malformed-link regression |
| v0.7 | None observed during candidate implementation | — | — | Provenance, deduplication and unknown-source tests |
| v0.8 | None observed | — | — | Full source→snapshot→observation→candidate provenance assertions |
| v0.9 | Provenance-chain regression passed unsupported `title=` argument; also used a Unix-specific temp path | Test API mismatch and non-portable fixture | Construct `ResearchSource` explicitly + `TemporaryDirectory` | Regression now matches public API and is platform-independent |

## 13. Current evidence boundary

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

## 14. Next step

Verify run #224. Then add candidate persistence/review and a cross-source deduplication boundary so repeated repositories/tools/entities from different research sources can converge on one durable artifact/entity while retaining every source and snapshot as provenance.
