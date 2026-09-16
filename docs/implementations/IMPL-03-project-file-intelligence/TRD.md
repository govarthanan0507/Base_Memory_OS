# IMPL-03 TRD — Project & File Intelligence

**Version:** 0.1

## Paths

- `src/memory_os/discovery.py` — filesystem discovery and project inspection
- `src/memory_os/core.py` — project/artifact persistence and relationships
- `src/memory_os/cli.py` — scan command boundary
- `tests/test_discovery.py` — deterministic discovery tests

## Technical approach

Use Python standard-library filesystem traversal. Detect project roots from repository/build/dependency/readme markers, prune dependency/cache/generated directories, and inspect source files without executing them. Store bounded SHA-256 hashes for artifacts and retain absolute source locations.

Project structural evidence is intentionally lightweight: marker files, code-file counts, dependency markers, likely entrypoint filenames, and import hints. It is metadata, not a claim of full semantic code understanding.

## Safety

Discovery never moves, deletes, renames, or executes source files. Hashing is bounded to avoid unexpectedly reading very large artifacts.

## Repeatability

Projects are unique by root location. Artifacts are unique by location. A rescan therefore refreshes metadata rather than creating duplicate physical records.

## Future extension points

Git metadata, AST-based language analysis, dependency graphs, repository history, semantic code summaries, and artifact-content embeddings can be added without changing the core artifact identity contract.
