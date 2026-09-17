# IMPL-04 TRD — Research Memory

**Version:** 0.7

## Paths

- `src/memory_os/research.py` — URL normalization, classification and source registration
- `src/memory_os/research_content.py` — bounded text capture, content hashing, snapshot persistence and artifact provenance attachment
- `src/memory_os/research_metadata.py` — provider-neutral metadata hints derived from URL structure only
- `src/memory_os/research_pipeline.py` — explicit source-ingestion orchestration
- `src/memory_os/research_extract.py` — deterministic structural observations from captured evidence; malformed URL resolution is safely ignored
- `src/memory_os/research_semantic.py` — conservative, provenance-bound semantic candidate extraction
- `tests/test_research.py` — deterministic normalization, classification and deduplication tests
- `tests/test_research_content.py` — snapshot hashing, persistence, idempotent attachment and byte-bound tests
- `tests/test_research_metadata.py` — YouTube/repository/unknown-source metadata tests
- `tests/test_research_pipeline.py` — offline integration tests for registration, optional capture and provenance
- `tests/test_research_extract.py` — structural title/heading/link extraction and malformed-link regression tests
- `tests/test_research_semantic.py` — candidate extraction, deduplication and provenance tests
- `tests/test_research_semantic_pipeline.py` — source → snapshot → observations → candidates provenance-chain integration test
- `src/memory_os/core.py` — artifact persistence and stable IDs

## Technical approach

Use Python's standard-library `urllib.parse` for deterministic HTTP(S) URL normalization. Preserve query parameters because they may identify distinct resources; remove fragments because they describe page-local navigation rather than source identity. Normalize scheme/hostname case, remove default ports and trim trailing path slashes.

Research sources reuse the existing artifact contract. The canonical URL is the artifact location and a deterministic hash-derived ID is generated from a `research` namespace plus the canonical URL. Existing artifact uniqueness by location provides a second persistence-level deduplication boundary.

Classification is conservative and URL-derived: YouTube-like hosts map to `video`, common Git hosting hosts map to `repository`, common document extensions map to `document`, and other HTTP(S) sources map to `website`.

Registration also persists safe URL-derived metadata returned by `extract_source_metadata()`.

## Source capture

`capture_text()` normalizes the URL, performs a standard-library HTTP(S) request, applies a caller-configurable timeout, reads at most `max_bytes + 1` bytes, rejects oversized responses, and decodes the response using the declared charset or UTF-8. It returns a `SourceSnapshot` containing canonical URL, raw text, capture timestamp, content type, status code and SHA-256 content hash.

`save_snapshot()` stores the captured evidence as a JSON file named by content hash. The snapshot contains explicit provenance metadata and is separate from the canonical research artifact so a source's identity is not confused with one particular capture.

`attach_snapshot_metadata()` appends an idempotent snapshot record to the existing artifact metadata.

## URL metadata adapters

`extract_source_metadata()` provides provider-neutral identity hints without network access. Current rules recognize YouTube watch/Shorts URLs, `youtu.be` video URLs, and GitHub/GitLab repository paths. Unknown sites return only safe canonical URL/host hints. The adapter deliberately does not scrape titles, authors, view counts, repository contents or other remote metadata.

## Structural evidence extraction

`extract_observations()` operates only on an existing `SourceSnapshot`. It uses bounded regular-expression parsing suitable for the current lightweight evidence layer to collect a title, headings, hyperlinks and absolute URLs. Relative hyperlinks are resolved against the captured source URL and normalized through the canonical URL boundary. `urljoin()` and URL normalization failures are ignored so malformed link input cannot crash the observation boundary. Duplicate observations are removed while preserving first-observed order.

The result carries the snapshot content hash and capture timestamp. This is an evidence observation object, not a memory record and not a semantic claim. No network request, LLM inference, code execution or source verification occurs.

## Semantic candidate extraction

`extract_semantic_candidates()` consumes an existing `SourceSnapshot` plus its `ResearchObservations`. It emits a small, provider-neutral `ResearchCandidate` record for:

- repository references found in observed GitHub/GitLab URLs;
- tools explicitly introduced by conservative `tool/library/framework/platform/service/software` textual patterns;
- ideas explicitly introduced by conservative `idea/project/approach/concept` textual patterns;
- source topics represented by the captured title and headings.

Each candidate stores kind, normalized value, exact evidence text, source URL, snapshot content hash, capture timestamp, confidence and `review_status=candidate`. Candidates are deduplicated by kind/value/evidence within one result.

This is a deliberate semantic boundary, not a full semantic understanding engine. Heuristics are deterministic and intentionally conservative. Candidates are never automatically inserted into durable memory, treated as verified claims, or used to assert that a referenced repository/tool is actually suitable. A future model adapter may propose richer candidates, but it must preserve the same provenance and review boundary.

## Provenance-chain integration

`tests/test_research_semantic_pipeline.py` exercises the complete offline evidence chain on one synthetic mixed-source document:

```text
captured source
    ↓
SourceSnapshot + SHA-256
    ↓
ResearchObservations
    ↓
ResearchCandidate records
    ↓
source URL + content hash + capture timestamp + review status
```

The integration assertion verifies that every produced candidate remains traceable to the exact snapshot and that repository/tool/idea/topic outputs remain distinct intermediate records.

## Ingestion pipeline

```text
ResearchSource
    ↓
register_research_source()
    ↓
extract_source_metadata()
    ↓
[capture=True?]
    ↓
capture_text()
    ↓
save_snapshot()
    ↓
attach_snapshot_metadata()
    ↓
extract_observations(snapshot)
    ↓
extract_semantic_candidates(snapshot, observations)
    ↓
review / future memory admission
```

With `capture=False`, the operation performs no network I/O and returns the artifact ID, canonical URL and URL-derived metadata. With `capture=True`, a snapshot directory is mandatory and the capture/persistence/provenance stages execute only after successful bounded capture.

## Safety and evidence semantics

Capture is an evidence acquisition step, not semantic understanding. Structural extraction and semantic candidate extraction are evidence inspection steps, not verification. The implementation does not execute downloaded content, silently summarize it, or declare it authoritative. Candidate records remain explicitly reviewable and provenance-bound.

No access-control bypass, credential handling or arbitrary code execution is implemented.

## Future extension points

Fetched provider metadata, repository/video/document extraction, claim-level citation relationships, content indexing and model-assisted semantic research synthesis can be added behind the same evidence and review boundary.
