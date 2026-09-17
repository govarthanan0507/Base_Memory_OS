# IMPL-04 TRD — Research Memory

**Version:** 0.1

## Paths

- `src/memory_os/research.py` — URL normalization, classification and source registration
- `tests/test_research.py` — deterministic normalization, classification and deduplication tests
- `src/memory_os/core.py` — artifact persistence and stable IDs

## Technical approach

Use Python's standard-library `urllib.parse` for deterministic HTTP(S) URL normalization. Preserve query parameters because they may identify distinct resources; remove fragments because they describe page-local navigation rather than source identity. Normalize scheme/hostname case, remove default ports and trim trailing path slashes.

Research sources reuse the existing artifact contract. The canonical URL is the artifact location and a deterministic hash-derived ID is generated from a `research` namespace plus the canonical URL. Existing artifact uniqueness by location provides a second persistence-level deduplication boundary.

Classification is conservative and URL-derived: YouTube-like hosts map to `video`, common Git hosting hosts map to `repository`, common document extensions map to `document`, and other HTTP(S) sources map to `website`.

## Safety

Registration stores metadata only. It does not fetch or execute external content.

## Future extension points

Fetched source snapshots, metadata extraction, repository/video/document adapters, citation relationships and semantic research synthesis can be added after the source-identity boundary is stable.
