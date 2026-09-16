# IMPL-01 TRD — Memory Core

**Version:** 0.1

## Technical approach

Python 3.11+ with the standard library and SQLite. No mandatory LLM, vector database, cloud service or vendor runtime.

## Paths implemented

- `src/memory_os/core.py` — domain records and SQLite persistence
- `src/memory_os/discovery.py` — read-only filesystem/project discovery
- `src/memory_os/cli.py` — CLI surface
- `tests/test_core.py` — persistence tests

## Data model

`memories`, `projects`, `artifacts`, `relations`, and `memory_fts` tables. JSON metadata preserves extensibility without prematurely fixing every future field.

## Provenance

Memory records retain source and observed time. Artifacts retain physical location, optional SHA-256 content hash, modification time and project-root metadata. Relationships retain creation time.

## Discovery safety

The scanner only reads filesystem metadata/content required for classification and hashing. It never writes to scanned paths. Large files are not hashed above the configured 20 MB threshold in v0.1.

## Provider boundary

No provider is required. Future adapters may implement model-assisted extraction against Ollama, OpenAI, Claude or another runtime without coupling persistence to the provider.

## Testing

Tests use Python `unittest` and temporary SQLite databases. CI is intentionally deferred until the repository's execution environment is established.
