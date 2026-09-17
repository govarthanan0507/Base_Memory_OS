# IMPL-04 — Research Memory — Implementation Log

## 1. Purpose

Chronological engineering audit trail for IMPL-04. Failures remain visible; later fixes are recorded rather than rewriting history.

## 2. Starting state

IMPL-03 established project/file intelligence, artifact history, project timelines, explicit project↔conversation continuity and evidence-labelled project views. IMPL-04 began by establishing canonical external research-source identity.

---

## 3. Cycle v0.1 — Research source identity foundation

**Date:** 2026-09-17

**Objective:** establish deterministic external-source identity before attempting content understanding.

**Implementation paths:**
- `src/memory_os/research.py`
- `tests/test_research.py`
- IMPL-04 BRD/FRD/PRD/TRD

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

**Starting state:** source identity was CI-verified, but registered sources had no preserved content evidence.

**Objective:** add explicit, bounded content capture without turning retrieval into interpretation.

**Exact implementation paths:**
- `src/memory_os/research_content.py`
- `tests/test_research_content.py`
- `docs/implementations/IMPL-04-research-memory/{BRD,FRD,PRD,TRD}.md`

**Implementation:** `SourceSnapshot`, bounded standard-library HTTP capture, timeout and byte limits, charset-aware text decoding, SHA-256 content identity, content-hash-named JSON snapshot persistence and idempotent snapshot provenance attachment to research artifacts.

**Tests:** deterministic hashing, provenance-preserving persistence, idempotent attachment and oversized-response rejection.

**Failure status:** no implementation failure observed in the recorded cycle. Rejected oversized input is intentional test behavior, not a build failure.

**Verification:** the source-capture commits were pushed to `main`; CI verification is to be recorded when the resulting workflow completes.

**Known limitations:** text only; no provider metadata extraction; no semantic parsing; snapshots are filesystem JSON; network capture is explicit.

**Evidence commits:**
- implementation `c589e128443cf6b084d89e2aa861095473109ed7`
- tests `e13c0c68fb9b336faf19dfdc0c364cb4a7aeaa05`
- BRD `30b27a555deefe96e28727d790e4027d03d818ac`
- FRD `1cab3b3adf488aa91be5142608ce720167e0a0ae`
- PRD `493d8a9d1721b4e7aaedd855e1abcec4e2e44556`
- TRD `41402afa03f95eb0ef1e5efac900335ac214dc72`

---

## 5. Cycle v0.3 — URL-only provider metadata hints

**Date:** 2026-09-17

**Starting state:** bounded capture existed; the system still lacked a clean adapter boundary for identifying provider/resource IDs without making network calls.

**Objective:** add deterministic provider-neutral metadata extraction from URL structure only.

**Exact implementation paths:**
- `src/memory_os/research_metadata.py`
- `tests/test_research_metadata.py`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- this log

**Implementation:** added `extract_source_metadata()` recognizing:
- YouTube watch URLs → provider/resource ID/video;
- YouTube Shorts URLs → provider/resource ID/short;
- `youtu.be` URLs → provider/resource ID/video;
- GitHub/GitLab repository paths → provider/owner/repository/repository kind;
- unknown sites → canonical URL and host only.

The adapter performs no HTTP requests and does not infer titles, authors, view counts, repository contents or other remote facts.

**Tests:** added four tests covering YouTube video identity, YouTube Shorts identity, repository identity and safe unknown-site behavior.

**Failure:** one documentation update initially used a stale blob SHA and GitHub returned HTTP 409.

**Root cause:** the file had changed after the earlier fetch, so the optimistic update used an outdated content SHA.

**Fix:** re-fetched the current file and retried with its current SHA. The retry succeeded.

**Regression protection:** future documentation edits must fetch the latest blob SHA immediately before updating a file that may have changed during the cycle.

**Verification:** implementation and test commits were accepted by GitHub. CI result for the new test-bearing commits is not yet recorded in this log and will be appended when available.

**Known limitations:** URL hints are observations about URL structure; they are not remote metadata verification. Provider support is intentionally narrow and provider-neutral.

**Evidence commits:**
- metadata implementation `69318789af6078432860af49abefd24ad4ba4155`
- metadata tests `5c6219ead71c4df6e94dd4d53f349ec7a0ab2576`
- TRD v0.3 `876ca60f409a8924e8a0128118f274ed9bd27ebd`
- FRD v0.3 `98396e11e8334d74a98ca39d068cc7fe458f6198`

---

## 6. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | Source type default bypassed classification | Concrete dataclass default | Blank default + automatic classification | YouTube registration test |
| v0.2 | None observed | — | — | Snapshot/content-limit/idempotence tests |
| v0.3 | Documentation update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |

## 7. Current evidence boundary

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
SEMANTIC UNDERSTANDING  ← future
```

## 8. Next step

Verify v0.2/v0.3 test-bearing commits in CI. Then add a small integration path that registers a source, derives URL metadata, optionally captures bounded content, persists the snapshot and exposes the complete provenance chain. Only after that should semantic research extraction begin.
