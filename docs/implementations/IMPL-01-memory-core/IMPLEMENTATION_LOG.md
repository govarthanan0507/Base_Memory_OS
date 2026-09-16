# IMPL-01 Implementation Log

## 2026-09-17 — v0.1 foundation

### Completed paths
- repository bootstrap
- Python packaging
- memory persistence
- artifact/project persistence
- typed relations
- FTS5 search with fallback
- read-only project discovery
- CLI
- automated core tests
- BRD / FRD / PRD / TRD

### Deliberate limitations
- No LLM extraction yet.
- No conversation import yet.
- Project naming/status inference is heuristic and explicitly provisional.
- No destructive filesystem organization.
- No UI.
- Word documentation copies will be generated as part of the documentation packaging path rather than treated as the canonical source.

### Next path
IMPL-02: conversation ingestion and normalization, while preserving the same provenance and artifact model.
