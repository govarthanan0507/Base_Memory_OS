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

**Verification:** workflow `tests`, run #186 (`35181985251`), passed across Python 3.11–3.14.

---

## 7. Cycle v0.5 — Research CLI boundary

**Date:** 2026-09-17

**Objective:** expose deterministic registration and explicit capture through the CLI.

**Implementation:** `add-research-source` and `capture-research-source`.

**Failure:** first implementation-log update returned GitHub HTTP 409 because the log blob changed after fetch.

**Root cause:** stale optimistic-concurrency SHA.

**Fix:** re-fetched the current log blob and retried.

---

## 8. Cycle v0.6 — Deterministic structural evidence inspection

**Date:** 2026-09-17

**Objective:** extract reproducible title, heading, hyperlink and absolute-URL observations from captured evidence without network access.

**Implementation:** `src/memory_os/research_extract.py` and tests. Relative links are resolved and normalized; duplicate observations preserve first-observed order; snapshot hash/timestamp remain provenance.

**Test failure:** CI run #200 (`35183355300`) failed in Python 3.12 because `::bad` is a valid relative URL reference rather than malformed input.

**Remediation sequence:** fixture corrected in `84290f3ee5d4f45dcf7296f8b38d587ee8fb954b`; run #211 (`35184049758`) then exposed a real `urljoin()` `ValueError` boundary; production hardened in `ba8204e920136c0aee975dec8ab9d5b07e41ae0c`.

---

## 9. Cycle v0.7 — Provenance-bound semantic candidate layer

**Date:** 2026-09-17

**Objective:** create a deterministic semantic-candidate boundary that can later be replaced or augmented by an LLM without changing provenance semantics.

**Implementation:** `src/memory_os/research_semantic.py` and tests. Candidates cover repositories, explicitly introduced tools, ideas and source topics. Each retains exact source URL, snapshot hash, capture timestamp, evidence, confidence and review status.

**Known limitation:** candidates initially remained in-memory and were not cross-source persistent entities.

---

## 10. Cycle v0.8 — Mixed-source provenance-chain integration

**Date:** 2026-09-17

**Objective:** prove source → snapshot → observation → candidate as one offline behavior.

**Implementation:** `tests/test_research_semantic_pipeline.py`.

**Verification:** run #218 (`35184233434`) completed successfully across Python 3.11–3.14.

---

## 11. Cycle v0.9 — Provenance-chain regression hardening

**Date:** 2026-09-17

**Objective:** prove persisted artifact snapshot provenance and emitted semantic candidates share the exact evidence identity.

**Failure:** run #223 (`35184529309`) failed because the new test passed unsupported `title=` to `ingest_research_source()`.

**Root cause:** test assumed a convenience API that does not exist. The test also used a Unix-specific temporary path.

**Remediation:** `b86ee0505639701a9073768bb57788370be453c1` constructs `ResearchSource` explicitly and uses `TemporaryDirectory()`.

**Verification:** run #224 (`35184592014`) passed Python 3.11, 3.12, 3.13 and 3.14.

---

## 12. Cycle v1.0 — Persistent cross-source research registry

**Date:** 2026-09-17

**Objective:** turn semantic candidates into durable, deduplicated research entities without losing independent evidence provenance.

**Exact implementation paths:**
- `src/memory_os/research_registry.py`
- `tests/test_research_registry.py`
- `docs/implementations/IMPL-04-research-memory/BRD.md`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/PRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- `README.md`

**Implementation:** added `research_entities` with deterministic identity from `kind + normalized value`, and `research_entity_evidence` for distinct source/snapshot/evidence occurrences. Duplicate entity identity converges across sources while duplicate evidence insertion is idempotent. Added explicit `candidate → accepted/rejected` review state with review timestamp. Review intentionally does not create a general durable-memory record.

**Tests:** same repository from two sources produces one entity and two evidence rows; different candidate kinds remain distinct; review changes status and does not insert into `memories`.

**CI verification:** corrected-head run #224 (`35184592014`) passed all four Python versions before this registry documentation closure. The registry changes and documentation are on newer commits and therefore require a fresh CI run before the final IMPL-04 gate is considered green.

---

## 13. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | Source type default bypassed classification | Concrete dataclass default | Blank default + automatic classification | YouTube registration test |
| v0.2 | None observed | — | — | Snapshot/content-limit/idempotence tests |
| v0.3 | Documentation update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |
| v0.4 | None observed | — | — | Offline pipeline tests |
| v0.5 | Log update returned GitHub 409 | Stale file SHA | Re-fetch current SHA and retry | Fetch-before-update discipline |
| v0.6 | Bad malformed-link fixture; then real `urljoin()` exception | Fixture ambiguity followed by production boundary gap | Correct fixture + catch URL resolution/normalization errors | Positive relative-link + malformed-link tests |
| v0.7 | None observed | — | — | Candidate provenance/dedup tests |
| v0.8 | None observed | — | — | Full provenance-chain assertions |
| v0.9 | Test used unsupported ingestion keyword and Unix-specific path | Test/API mismatch and portability issue | Explicit `ResearchSource` + `TemporaryDirectory()` | Corrected-head CI #224 |
| v1.0 | No implementation failure observed in registry cycle | — | Fresh CI required after final registry/docs commits | Registry dedup/review tests |

## 14. Current evidence boundary

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
SEMANTIC CANDIDATE ── reviewable, provenance-bound
 ↓
RESEARCH ENTITY ── deduplicated identity + evidence history
 ↓
ACCEPT / REJECT ── explicit review state
 ↓
DURABLE MEMORY / VERIFIED CLAIM ── not automatic
```

## 15. IMPL-04 gate state

**Implementation:** complete for the defined v0.9 scope.

**Documentation:** BRD/FRD/PRD/TRD, README and this audit log updated.

**Verification:** registry behavior is covered by automated tests; the last fully verified head is run #224 before the final registry/doc commits. A fresh CI run on the current head is required before marking the milestone release gate green.

## 16. Next milestone

IMPL-05 — Re-entry: use the existing conversation/project/artifact timelines and research provenance to generate a compact, evidence-labelled re-entry briefing that answers where the user left off and what unresolved thread should be resumed, without pretending inference is fact.
