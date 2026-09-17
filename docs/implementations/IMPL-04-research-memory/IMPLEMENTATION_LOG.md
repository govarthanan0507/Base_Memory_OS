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

## 6. Cycle v0.4 — Explicit research ingestion pipeline

**Date:** 2026-09-17

**Starting state:** source registration, URL metadata extraction and bounded snapshot capture existed as separate capabilities. There was no single explicit operation expressing their intended order or enforcing the capture boundary.

**Objective:** compose the existing layers into a deterministic-to-optional ingestion path without collapsing evidence and interpretation.

**Exact implementation paths:**
- `src/memory_os/research.py`
- `src/memory_os/research_pipeline.py`
- `tests/test_research_pipeline.py`
- `docs/implementations/IMPL-04-research-memory/BRD.md`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/PRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- `README.md`
- this log

**Implementation:**
1. `register_research_source()` now persists safe URL-derived metadata alongside source provenance.
2. `ResearchIngestResult` records artifact ID, canonical URL, URL-derived metadata, optional snapshot and snapshot path.
3. `ingest_research_source()` performs registration and metadata derivation without network I/O when `capture=False`.
4. When `capture=True`, a snapshot directory is mandatory; bounded capture, hash-named persistence and provenance attachment happen in that order.

**Tests:** added three offline integration tests covering network-free registration, end-to-end mocked capture/provenance persistence, and required snapshot-directory validation. No external website is contacted by the tests.

**Failure status:** no implementation failure observed in this cycle. The network-free assertion is deliberate protection against accidental I/O during registration.

**Verification:** commits were accepted on `main`. Latest CI verification remains pending; no green status is claimed until a workflow run for the current test-bearing commits is observed.

**Known limitations:** orchestration is library-level only; no CLI command yet. Snapshot capture remains text-only and uses standard-library HTTP. Provider metadata remains URL-derived observation, not remote verification.

**Evidence commits:**
- research registration metadata `61531f12992989708e0f09b196e658e909be7914`
- ingestion pipeline `283690b62a998a0ee99be7fb1dc4c892665b7f36`
- pipeline tests `8cab3e287b4528e0263fcafac2c2adcd1a1265d0`
- README v0.4 `ea362dd5f2e47bbf8a82603ca35c5df7a74f613c`
- FRD v0.4 `8d64ad5e3041dce9eac6bbe7fdfa9dd175be78bf`
- PRD v0.3 `79022dd0a1d0afb107bf434f4fb6066791c4fcc4`
- TRD v0.4 `dec60a9fd64299f6ab45e0d9b0e4df8527ffb2fd`

---

## 7. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | Source type default bypassed classification | Concrete dataclass default | Blank default + automatic classification | YouTube registration test |
| v0.2 | None observed | — | — | Snapshot/content-limit/idempotence tests |
| v0.3 | Documentation update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |
| v0.4 | None observed | — | — | Offline pipeline tests + capture=False no-network assertion |

## 8. Current evidence boundary

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
PROVENANCE ATTACHMENT
 ↓
SEMANTIC UNDERSTANDING  ← future
```

## 9. Next step

Verify v0.2/v0.3/v0.4 test-bearing commits in CI. Then add a small research-source CLI surface if it improves actual user workflow, followed by semantic research extraction only after the evidence boundary remains stable.
