# IMPL-07 — Technical Requirements

## Version
v1.0

## Implementation boundary
Primary paths expected to evolve:
- `src/memory_os/core.py` — durable memory/relation primitives
- `src/memory_os/candidates.py` — candidate lifecycle
- new consolidation module under `src/memory_os/`
- CLI command surface in `src/memory_os/cli.py`
- `tests/` — unit and integration coverage

## Design
Use existing SQLite source-of-truth and stable IDs. Consolidation must run transactionally. Existing evidence and candidate records remain immutable historical evidence; state transitions are represented explicitly through relations/events/metadata.

## Invariants
1. Unreviewed candidates cannot become durable memory.
2. Every promoted memory has candidate provenance.
3. Repeating the same consolidation request is idempotent.
4. Existing conflicting state is never silently destroyed.
5. All writes are local and deterministic.
6. No network or LLM dependency is required.

## Test strategy
Start with failing tests for each invariant, implement the smallest change, run the full suite, inspect persisted rows, then document the result before the next change.

## Exit gate
CLEAR only when all FR-01..FR-07 acceptance tests pass and provenance can be followed end-to-end.
