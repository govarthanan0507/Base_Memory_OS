# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.7 — CI-driven integration repair**

IMPL-03 now has read-only filesystem discovery, project/artifact registration, structural and state evidence, Git identity, historical artifact changes, project timelines, and explicit project↔conversation continuity. This cycle used the repository's real GitHub Actions execution as a diagnostic loop rather than assuming local correctness.

The repair pass restored message identity compatibility, candidate extraction from both domain objects and persisted records, conversation-schema initialization for evidence linking, memory-aware continuity traversal, richer JSON provenance, Git ref parsing, explicit timeline event types, stable continuity display identifiers, canonical resolution of provider external conversation IDs, and stable timestamps for idempotent candidate projection.

Discovery remains **read-only**: no source files are moved, renamed, deleted or executed.

## Verification status

GitHub Actions is exercising **38 tests** across Python 3.11–3.14. The initial diagnostic run exposed 3 failures and 11 errors. Subsequent repair runs progressively reduced the failures; the latest observed run before this documentation commit had one continuity error and one candidate-projection idempotence failure, both addressed in the current branch. A fresh full-matrix run is required to establish the final green state.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification is actively exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with explicit review and provenance.
- **Project activity timeline:** implemented from project events, relationships and artifact evidence, including historical changes.
- **IMPL-03 project discovery:** implemented as a non-executing structural intelligence layer.
- **IMPL-03 state evidence:** tests, TODO/FIXME and recent activity signals implemented.
- **IMPL-03 root hardening:** strong-marker precedence and code-only project discovery implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **CI repair pass:** active; real runtime failures are being used to harden domain boundaries and idempotence.

## IMPL-03 completion gate

IMPL-03 is not complete until the fresh CI matrix is green and discovery is validated against representative mixed workspaces/monorepo-like layouts. Structural signals remain evidence rather than claims of code quality, production readiness or project intent.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.**
