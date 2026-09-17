# IMPL-04 TRD — Research Memory

**Version:** 0.2

## Paths

- `src/memory_os/research.py` — URL normalization, classification and source registration
- `src/memory_os/research_content.py` — bounded text capture, content hashing, snapshot persistence and artifact provenance attachment
- `tests/test_research.py` — deterministic normalization, classification and deduplication tests
- `tests/test_research_content.py` — snapshot hashing, persistence, idempotent attachment and byte-bound tests
- `src/memory_os/core.py` — artifact persistence and stable IDs

## Technical approach

Use Python's standard-library `urllib.parse` for deterministic HTTP(S) URL normalization. Preserve query parameters because they may identify distinct resources; remove fragments because they describe page-local navigation rather than source identity. Normalize scheme/hostname case, remove default ports and trim trailing path slashes.

Research sources reuse the existing artifact contract. The canonical URL is the artifact location and a deterministic hash-derived ID is generated from a `research` namespace plus the canonical URL. Existing artifact uniqueness by location provides a second persistence-level deduplication boundary.

Classification is conservative and URL-derived: YouTube-like hosts map to `video`, common Git hosting hosts map to `repository`, common document extensions map to `document`, and other HTTP(S) sources map to `website`.

## Source capture

`capture_text()` normalizes the URL, performs a standard-library HTTP(S) request, applies a caller-configurable timeout, reads at most `max_bytes + 1` bytes, rejects oversized responses, and decodes the response using the declared charset or UTF-8. It returns a `SourceSnapshot` containing canonical URL, raw text, capture timestamp, content type, status code and SHA-256 content hash.

`save_snapshot()` stores the captured evidence as a JSON file named by content hash. The snapshot contains explicit provenance metadata and is separate from the canonical research artifact so a source's identity is not confused with one particular capture.

`attach_snapshot_metadata()` appends an idempotent snapshot record to the existing artifact metadata. It does not silently replace the source artifact's identity.

## Safety and evidence semantics

Capture is an evidence acquisition step, not semantic understanding. The implementation does not execute downloaded content, summarize it, infer claims from it, or declare it authoritative. The byte limit is a resource-control boundary, and decode failures are surfaced rather than converted into invented text.

No access-control bypass, credential handling or arbitrary code execution is implemented.

## Future extension points

Provider-specific metadata adapters, repository/video/document extraction, citation relationships, content indexing and semantic research synthesis can be added after the capture boundary is stable.
