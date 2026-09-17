# IMPL-03 TRD — Project & File Intelligence

**Version:** 0.3

## Paths

- `src/memory_os/discovery.py` — filesystem discovery, root heuristics and project inspection
- `src/memory_os/core.py` — project/artifact persistence, relationships and artifact history
- `src/memory_os/cli.py` — scan/report/evidence command boundary
- `src/memory_os/evidence.py` — explicit project↔conversation evidence linking
- `src/memory_os/continuity.py` — cross-entity continuity and re-entry traversal
- `src/memory_os/timeline.py` — project timeline assembly including artifact history
- `src/memory_os/project_evidence.py` — compact evidence-labelled project view
- `tests/test_discovery.py` — filesystem/Git/artifact-history/nested-root tests
- `tests/test_evidence.py` — evidence linking and candidate projection tests
- `tests/test_continuity.py` — continuity traversal tests
- `tests/test_timeline.py` — artifact-history timeline tests
- `tests/test_project_evidence.py` — compact evidence-view tests

## Technical approach

Use Python standard-library filesystem traversal. Detect project roots from repository/build/dependency/readme markers, prune dependency/cache/generated directories, and inspect source files without executing them. Strong project markers outrank README-only workspace markers. Strong nested project roots are retained; selected child roots are pruned from parent artifact traversal so ownership remains isolated.

Project structural evidence remains lightweight: marker files, code-file counts, dependency markers, likely entrypoints, import hints, README presence, test presence/count, bounded TODO/FIXME count and recent code-file activity. These values are evidence fields, not semantic judgments about code quality, intent or production readiness.

Artifact identity is location-based. Bounded SHA-256 hashing and modification timestamps provide repeat-scan evidence. Artifact events preserve old/new values rather than overwriting history.

Project↔conversation continuity uses explicit relations. Provider-facing conversation external IDs are resolved to canonical internal IDs before graph linking. Candidate-derived project events preserve a stable observation timestamp when source timestamps are absent.

`project-evidence-view` assembles current snapshot, historical evidence, explicit continuity and current artifacts. The renderer labels structural signals as evidence and does not infer unsupported conclusions.

## Safety

Discovery never moves, deletes, renames or executes source files. Hashing is bounded. Git metadata is read directly from repository metadata. Read failures and malformed source files are not treated as authoritative semantic evidence.

## Repeatability

Projects are unique by root location. Artifacts are unique by location. Relationships are unique by source/relation/target. Event identities are deterministic for the same evidence tuple. This supports repeatable rescans and candidate projection without duplicate physical records.

## Verification

GitHub Actions runs `python -m unittest discover -s tests -v` with `PYTHONPATH=src` across Python 3.11–3.14. IMPL-03's evidence-view change was verified by runs #146 and #147; run #147 succeeded on commit `62581407594e5c06ef034c58ea73282b974599de`.

## Future extension points

Full Git history, richer multi-language AST analysis, dependency graphs, semantic code summaries, artifact-content embeddings, missing/deleted artifact evidence, richer workspace-vs-package modelling and automatic project↔conversation discovery can be added without changing the basic artifact identity contract.
