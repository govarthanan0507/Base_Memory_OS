# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.8.1 — canonical identity test repair**

IMPL-03 now has read-only filesystem discovery, project/artifact registration, structural and state evidence, Git identity, historical artifact changes, project timelines, and explicit project↔conversation continuity. This cycle uses real GitHub Actions execution as the runtime diagnostic loop.

The repair pass restored message identity compatibility, candidate extraction from both domain objects and persisted records, conversation-schema initialization for evidence linking, memory-aware continuity traversal, richer JSON provenance, Git ref parsing, explicit timeline event types, stable continuity identifiers, canonical provider external-ID resolution, and stable timestamps for idempotent candidate projection.

Project discovery now also preserves strong nested project boundaries in monorepo-like layouts and prevents a parent project's artifact scan from swallowing selected child-project artifacts.

The latest CI failure was isolated to a stale assertion in `tests/test_evidence.py`: conversation external IDs are provider-facing identifiers, while graph relations correctly target the system's canonical conversation ID. The test now resolves and asserts that canonical identity rather than conflating the two namespaces.

Discovery remains **read-only**: no source files are moved, renamed, deleted or executed.

## Verification status

GitHub Actions is exercising the suite across Python 3.11–3.14. The latest observed run reached 39 tests and had one failure; all other tests in the 3.11 job passed before the stale identity assertion failed. The assertion has now been repaired, and a fresh full-matrix run is required before the completion gate can be called green.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification is exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with explicit review and provenance.
- **Project activity timeline:** implemented from project events, relationships and artifact evidence, including historical changes.
- **IMPL-03 project discovery:** implemented as a non-executing structural intelligence layer.
- **IMPL-03 state evidence:** tests, TODO/FIXME and recent activity signals implemented.
- **IMPL-03 root hardening:** strong-marker precedence, code-only discovery, and nested strong-project boundaries implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **Canonical identity boundary:** provider-facing conversation external IDs are resolved to stable internal conversation IDs before graph linking.
- **CI repair pass:** active; real runtime failures are being used to harden domain boundaries and idempotence.

## IMPL-03 completion gate

IMPL-03 is not complete until the newest CI matrix is green and discovery is validated against representative mixed workspaces/monorepo-like layouts. Structural signals remain evidence rather than claims of code quality, production readiness or project intent.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.**
