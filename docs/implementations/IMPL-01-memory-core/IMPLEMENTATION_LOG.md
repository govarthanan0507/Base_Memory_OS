# IMPL-01 Implementation Log

## 2026-09-17 — v0.1 foundation

### Completed paths
- repository bootstrap
- Python packaging
- memory persistence
- artifact/project persistence
- stable project/artifact upserts
- typed relations
- FTS5 search with fallback
- read-only project discovery
- project-to-artifact relationships
- CLI
- automated core and discovery tests
- BRD / FRD / PRD / TRD
- GitHub Actions test workflow

### Deliberate limitations
- No LLM extraction yet.
- No provider-specific conversation adapters yet.
- Project naming/status inference is heuristic and explicitly provisional.
- No destructive filesystem organization.
- No UI.
- Word documentation copies will be generated as part of the documentation packaging path rather than treated as the canonical source.

### Quality verification
Local execution of the IMPL-01 test suite passes: 5 tests.

### Next path
IMPL-02: conversation ingestion and normalization, preserving the same provenance and artifact model.

## 2026-09-17 — IMPL-02 started

Documentation and the first provider-neutral conversation persistence/import paths have been added. Local verification of the conversation implementation passes: 3 tests in addition to the 5 IMPL-01 tests.
