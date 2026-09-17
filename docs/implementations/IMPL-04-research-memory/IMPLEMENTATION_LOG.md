# IMPL-04 — Research Memory — Implementation Log

## 1. Purpose of this log

This is the chronological engineering audit trail for IMPL-04. It records the starting state, objective, exact implementation paths, tests, failures, root causes, remediation, verification evidence, limitations and next steps.

**Standing rule:** a green result does not erase earlier failures. If a later implementation changes an assumption, both the earlier assumption and the correction remain visible.

---

## 2. Starting state

IMPL-03 closed with project/file intelligence, artifact registration, artifact history, explicit project↔conversation continuity and evidence-labelled project views.

The next unresolved product gap was external research. Useful research sources—websites, videos, repositories and documents—could be discussed in conversations, but there was not yet a dedicated research-source registration boundary that gave them canonical identity and duplicate-safe provenance.

---

## 3. Cycle v0.1 — Research source identity foundation

**Date:** 2026-09-17

### Objective

Create the smallest useful Research Memory layer without prematurely adding web scraping or semantic summarization.

### Implementation

Added provider-neutral `ResearchSource`, deterministic URL normalization, conservative URL classification and duplicate-safe artifact registration.

### Failure discovered during refinement

`ResearchSource.source_type` initially defaulted to `website`, bypassing automatic URL classification for ordinary constructor calls.

### Root cause

The dataclass default encoded a concrete classification before the registration boundary could inspect the URL.

### Remediation

Changed the default to empty string. Registration now classifies whenever the explicit type is omitted/blank.

### Regression test

Added a YouTube registration test asserting `artifact_type == "video"` when no source type is supplied.

### Verification

GitHub Actions run **#164** (`35180978862`) completed successfully on Python 3.11, 3.12, 3.13 and 3.14 for the test-bearing source-identity changes. This closes the verification loop for v0.1.

### Known limitations

- URL classification is heuristic.
- No external content is fetched.
- No source snapshot is stored.
- No citation extraction or automatic project linkage exists.

---

## 4. Cycle v0.2 — Bounded source-content evidence

**Date:** 2026-09-17

### Starting state

Research-source identity and classification were green in the repository CI matrix. The product still could not preserve the actual external evidence behind a registered source.

### Objective

Add the smallest content-capture boundary that preserves evidence without turning fetching into semantic interpretation.

### Exact implementation paths

Added:

- `src/memory_os/research_content.py`
- `tests/test_research_content.py`

Updated:

- `docs/implementations/IMPL-04-research-memory/BRD.md`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/PRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- this implementation log

### Implementation

`SourceSnapshot` represents a captured text response and records:

- canonical URL;
- captured text;
- capture timestamp;
- content type;
- HTTP status when available;
- deterministic SHA-256 content hash; and
- optional metadata.

`capture_text()`:

- normalizes the URL through the existing research identity boundary;
- performs an explicit HTTP(S) request using Python's standard library;
- applies a caller-configurable timeout;
- reads at most `max_bytes + 1` bytes;
- rejects responses beyond the configured byte bound;
- uses the declared response charset or UTF-8; and
- raises an explicit error when text decoding fails.

`save_snapshot()` persists the snapshot as a JSON evidence file named by its content hash. The snapshot is separate from the source artifact, so source identity is not confused with a particular capture.

`attach_snapshot_metadata()` adds an idempotent provenance record to an existing research artifact, including snapshot path, hash, capture time, content type and HTTP status.

### Evidence semantics

The implementation deliberately stops at capture. A successful HTTP response is not treated as proof that the source is authoritative, correct or semantically understood. No summarization, claim extraction, downloaded-code execution, credential handling or access-control bypass is included.

### Tests added

`tests/test_research_content.py` covers:

1. deterministic snapshot hashing;
2. preservation of content and explicit provenance during snapshot persistence;
3. idempotent attachment of the same snapshot metadata;
4. rejection of an oversized response before it can become stored evidence.

### Tests executed

The test-bearing commits were pushed to `main`; repository CI is the authoritative execution environment for the Python 3.11–3.14 matrix. The resulting CI run is not yet recorded here at the time of this entry and will be appended once available.

### Failure register

No implementation failure has been observed in this cycle yet. The oversized-response behavior is an intentional rejected-input test, not a build failure.

### Known limitations

- Capture currently handles text responses only.
- It does not extract YouTube metadata, repository metadata or document structure.
- It does not sanitize or canonicalize arbitrary tracking query parameters.
- Snapshot storage is filesystem JSON rather than a dedicated artifact table/blob store.
- Network access remains explicit and caller initiated.

---

## 5. Verification strategy

### Unit verification

Normalization, classification, deterministic identity, deduplication, snapshot hashing, persistence, byte limits and idempotent provenance attachment.

### Integration verification

Research source → artifact → captured snapshot → provenance relationship.

### Provenance verification

A source retains canonical identity; each capture retains its own hash/time/location. No capture is promoted to a semantic conclusion automatically.

### CI verification

The repository's GitHub Actions matrix runs the full unittest suite on Python 3.11–3.14.

---

## 6. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | `ResearchSource.source_type` defaulted to `website`, bypassing URL classification | Concrete dataclass default prevented the unspecified-type branch from executing | Default changed to empty string; registration classifies when type is omitted | YouTube registration regression test |
| v0.2 | None observed yet | — | — | Snapshot hashing/persistence/limit/idempotence tests |

This table is append-oriented. Future failures remain visible.

---

## 7. Evidence trail

### Source identity

- Research implementation: `41e426b796fb036d31738a7ba527bd90ffa6df0f`
- Research tests: `6387c0ccfa1409cf33278142033e8c6ceae12b15`
- Source-type default remediation: `2a71b2120543a930d0fcd8654c38bf81f38d03ec`
- Regression test: `e089c6974b924c28a97fcbde06c31a5b48238402`
- CI run #164: `35180978862`, green on Python 3.11–3.14

### Documentation baseline

- BRD baseline: `9e74293b2dd4e35a9e17dbd13391d852992451c8`
- FRD baseline: `ebfae12b61b773cab17c1a168f87d14beaaccd9c`
- PRD baseline: `108e9e1e2b74f82ac61dc36de4425fb68c5bfc62`
- TRD baseline: `2fa8fbcf5678c9f5a57a5b65a5fbc5612326c7f1`

### v0.2 source capture

- `research_content.py`: `c589e128443cf6b084d89e2aa861095473109ed7`
- `test_research_content.py`: `e13c0c68fb9b336faf19dfdc0c364cb4a7aeaa05`
- BRD v0.2: `30b27a555deefe96e28727d790e4027d03d818ac`
- FRD v0.2: `1cab3b3adf488aa91be5142608ce720167e0a0ae`
- TRD v0.2: `41402afa03f95eb0ef1e5efac900335ac214dc72`
- PRD v0.2: `493d8a9d1721b4e7aaedd855e1abcec4e2e44556`

The current log update itself is committed separately. The resulting CI run will be appended without rewriting this history.

---

## 8. Next step

Verify v0.2 in CI. If green, add the first provider-specific metadata adapter boundary—starting with metadata that can be obtained without pretending to understand the source content. Semantic synthesis remains later.
