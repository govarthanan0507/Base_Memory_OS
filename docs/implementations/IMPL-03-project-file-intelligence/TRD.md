# IMPL-03 TRD — Project & File Intelligence

**Version:** 0.2

## Paths

- `src/memory_os/discovery.py` — filesystem discovery, root heuristics and project inspection
- `src/memory_os/core.py` — project/artifact persistence, relationships and artifact history
- `src/memory_os/cli.py` — scan/report command boundary
- `tests/test_discovery.py` — deterministic discovery and evidence tests

## Technical approach

Use Python standard-library filesystem traversal. Detect project roots from repository/build/dependency/readme markers, prune dependency/cache/generated directories, and inspect source files without executing them. Strong project markers (Git/build/dependency manifests) outrank README-only workspace markers. README-only roots are only retained when they also contain code and do not contain a stronger descendant.

Project structural evidence remains lightweight: marker files, code-file counts, dependency markers, likely entrypoint filenames, import hints, README presence, test presence/count, bounded TODO/FIXME count, and recent code-file activity. These values are evidence fields, not semantic judgments about code quality, intent, or production readiness.

State evidence is bounded to files already classified as code and to small text files (`MAX_ANALYSIS_BYTES`) for TODO/FIXME inspection. Recent activity uses a 30-day window and UTC filesystem modification timestamps.

## Safety

Discovery never moves, deletes, renames, or executes source files. Hashing is bounded to avoid unexpectedly reading very large artifacts. Read failures and malformed source files are skipped rather than treated as authoritative evidence.

## Repeatability

Projects are unique by root location. Artifacts are unique by location. A rescan therefore refreshes metadata rather than creating duplicate physical records while artifact events preserve observed changes.

## Future extension points

Git history, AST-based language analysis beyond Python, dependency graphs, semantic code summaries, richer artifact history/re-entry synthesis, and artifact-content embeddings can be added without changing the core artifact identity contract.
