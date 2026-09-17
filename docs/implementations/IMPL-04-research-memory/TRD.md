# IMPL-04 TRD — Research Memory

**Version:** 0.5

## Paths

- `src/memory_os/research.py` — URL normalization, classification and source registration
- `src/memory_os/research_content.py` — bounded text capture, content hashing, snapshot persistence and artifact provenance attachment
- `src/memory_os/research_metadata.py` — provider-neutral metadata hints derived from URL structure only
- `src/memory_os/research_pipeline.py` — explicit source-ingestion orchestration
- `src/memory_os/research_extract.py` — deterministic structural observations from captured evidence
- `tests/test_research.py` — deterministic normalization, classification and deduplication tests
- `tests/test_research_content.py` — snapshot hashing, persistence, idempotent attachment and byte-bound tests
- `tests/test_research_metadata.py` — YouTube/repository/unknown-source metadata tests
- `tests/test_research_pipeline.py` — offline integration tests for registration, optional capture and provenance
- `tests/test_research_extract.py` — structural title/heading/link extraction tests
- `src/memory_os/core.py` — artifact persistence and stable IDs

## Technical approach

Use Python's standard-library `urllib.parse` for deterministic HTTP(S) URL normalization. Preserve query parameters because they may identify distinct resources; remove fragments because they describe page-local navigation rather than source identity. Normalize scheme/hostname case, remove default ports and trim trailing path slashes.

Research sources reuse the existing artifact contract. The canonical URL is the artifact location and a deterministic hash-derived ID is generated from a `research` namespace plus the canonical URL. Existing artifact uniqueness by location provides a second persistence-level deduplication boundary.

Classification is conservative and URL-derived: YouTube-like hosts map to `video`, common Git hosting hosts map to `repository`, common document extensions map to `document`, and other HTTP(S) sources map to `website`.

Registration also persists safe URL-derived metadata returned by `extract_source_metadata()`. A local import keeps the two modules acyclic.

## Source capture

`capture_text()` normalizes the URL, performs a standard-library HTTP(S) request, applies a caller-configurable timeout, reads at most `max_bytes + 1` bytes, rejects oversized responses, and decodes the response using the declared charset or UTF-8. It returns a `SourceSnapshot` containing canonical URL, raw text, capture timestamp, content type, status code and SHA-256 content hash.

`save_snapshot()` stores the captured evidence as a JSON file named by content hash. The snapshot contains explicit provenance metadata and is separate from the canonical research artifact so a source's identity is not confused with one particular capture.

`attach_snapshot_metadata()` appends an idempotent snapshot record to the existing artifact metadata. It does not silently replace the source artifact's identity.

## URL metadata adapters

`extract_source_metadata()` provides provider-neutral identity hints without network access. Current rules recognize YouTube watch/Shorts URLs, `youtu.be` video URLs, and GitHub/GitLab repository paths. Unknown sites return only safe canonical URL/host hints. The adapter deliberately does not scrape titles, authors, view counts, repository contents or other remote metadata.

## Structural evidence extraction

`extract_observations()` operates only on an existing `SourceSnapshot`. It uses bounded regular-expression parsing suitable for the current lightweight evidence layer to collect a title, headings, hyperlinks and absolute URLs. Relative hyperlinks are resolved against the captured source URL and normalized through the canonical URL boundary. Duplicate observations are removed while preserving first-observed order.

The result carries the snapshot content hash and capture timestamp. This is an evidence observation object, not a memory record and not a semantic claim. No network request, LLM inference, code execution or source verification occurs.

## Ingestion pipeline

`ingest_research_source()` composes the layers while preserving their boundaries:

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
ResearchIngestResult
    ↓
extract_observations(snapshot)  ← optional deterministic evidence inspection
```

With `capture=False`, the operation performs no network I/O and returns the artifact ID, canonical URL and URL-derived metadata. With `capture=True`, a snapshot directory is mandatory and the capture/persistence/provenance stages execute only after successful bounded capture.

## Safety and evidence semantics

Capture is an evidence acquisition step, not semantic understanding. Structural extraction is likewise evidence inspection, not interpretation. The implementation does not execute downloaded content, summarize it, infer claims from it, or declare it authoritative. The byte limit is a resource-control boundary, and decode failures are surfaced rather than converted into invented text.

URL-derived provider metadata and structural observations are observations about supplied URL/evidence structure. They are not verified statements about the current remote resource.

No access-control bypass, credential handling or arbitrary code execution is implemented.

## Future extension points

Fetched provider metadata, repository/video/document extraction, citation relationships, content indexing and semantic research synthesis can be added after this deterministic evidence layer is stable.
