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

The hypothesis for this cycle is:

> Before Memory OS can understand research content, it must reliably know which external source is being referred to and avoid storing the same source repeatedly under superficial URL variations.

### Files added

- `src/memory_os/research.py`
- `tests/test_research.py`
- `docs/implementations/IMPL-04-research-memory/BRD.md`
- `docs/implementations/IMPL-04-research-memory/FRD.md`
- `docs/implementations/IMPL-04-research-memory/PRD.md`
- `docs/implementations/IMPL-04-research-memory/TRD.md`
- this implementation log

### Implementation

Added `ResearchSource` as a provider-neutral source record.

Added deterministic `normalize_url()` behavior:

- HTTP(S) is required;
- scheme is normalized to lowercase;
- hostname is normalized to lowercase;
- default HTTP/HTTPS ports are removed;
- non-default ports are retained;
- empty paths become `/`;
- trailing path slashes are removed where safe; and
- fragments are removed while query parameters are preserved.

Added conservative `classify_url()` behavior:

- YouTube-like hosts → `video`;
- GitHub/GitLab-like hosts → `repository`;
- common document extensions → `document`;
- other HTTP(S) sources → `website`.

Added `register_research_source()` which reuses the existing artifact registry. The canonical URL becomes the artifact location and a deterministic research-namespaced ID is derived from the canonical URL.

### Failure discovered during refinement

The first implementation gave `ResearchSource.source_type` a default of `"website"`. That meant the registration layer's intended automatic classification branch (`explicit type or classify_url`) was never reached for the normal constructor path. A YouTube URL could therefore be stored as `website` unless callers explicitly supplied `source_type=""`.

### Root cause

The dataclass default encoded a concrete classification before the registration boundary had an opportunity to inspect the URL.

### Remediation

Changed the default to an empty string. Registration now treats an empty/whitespace type as unspecified and calls `classify_url(canonical_url)`. Explicit source types remain supported for cases where URL heuristics are insufficient.

### Regression test

Added `test_registration_uses_url_classification_when_type_is_omitted` to `tests/test_research.py`. It registers a YouTube URL without a source type and asserts that both the artifact type and persisted metadata identify it as `video`.

### Important design choice

This cycle intentionally does **not** fetch external pages. Registering a URL means only that the source was recorded as a research artifact. It does not mean the content was downloaded, parsed or independently verified.

### Tests

`tests/test_research.py` now covers:

1. URL normalization while preserving query parameters;
2. removal of fragments/default ports;
3. classification of video/repository/document/website examples;
4. automatic classification during registration when type is omitted; and
5. duplicate-safe registration of equivalent canonical URLs.

### Verification status

The implementation and regression test were committed successfully. GitHub Actions verification for these two commits is still pending at the time of this log update; no CI result is being represented as green until the workflow reports it.

### Known limitations

- URL classification is heuristic and host/path based.
- No external content is fetched.
- No source snapshot is stored.
- No citation extraction exists.
- No automatic project/idea linkage exists.
- Tracking/affiliate parameters are deliberately not stripped because query parameters may be semantically meaningful; future canonicalization can add an explicit policy if evidence justifies it.

---

# 4. Verification strategy

Research Memory will be verified in layers:

### Unit verification

Normalization, classification, deterministic identity and deduplication tests.

### Integration verification

Research source → artifact → project/idea relationship flows once relationship semantics are introduced.

### Provenance verification

A source should retain canonical URL, source type, capture time and provenance without implying content verification.

### CI verification

The repository's existing GitHub Actions matrix will run the full unittest suite on Python 3.11–3.14.

---

# 5. Failure/remediation register

| Cycle | Failure | Root cause | Remediation | Regression protection |
|---|---|---|---|---|
| v0.1 | `ResearchSource.source_type` defaulted to `website`, bypassing URL classification | Concrete dataclass default prevented the unspecified-type branch from executing | Default changed to empty string; registration classifies when type is omitted | YouTube registration regression test |

This table will be appended to rather than rewritten as new failures are discovered.

---

# 6. Evidence trail

Initial implementation commits:

- Research implementation: `41e426b796fb036d31738a7ba527bd90ffa6df0f`
- Research tests: `6387c0ccfa1409cf33278142033e8c6ceae12b15`
- IMPL-04 BRD: `9e74293b2dd4e35a9e17dbd13391d852992451c8`
- IMPL-04 FRD: `ebfae12b61b773cab17c1a168f87d14beaaccd9c`
- IMPL-04 PRD: `108e9e1e2b74f82ac61dc36de4425fb68c5bfc62`
- IMPL-04 TRD: `2fa8fbcf5678c9f5a57a5b65a5fbc5612326c7f1`
- Source-type default remediation: `2a71b2120543a930d0fcd8654c38bf81f38d03ec`
- Regression test: `e089c6974b924c28a97fcbde06c31a5b48238402`

CI run identifiers will be added after the test-bearing commits are verified by GitHub Actions.

---

# 7. Next step

Verify the new test-bearing commits in CI. If green, the next Research Memory slice is source-content/metadata capture adapters with explicit provenance—not semantic synthesis yet.
