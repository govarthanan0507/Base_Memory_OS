# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.9 — evidence view + completion validation**

IMPL-03 now has read-only filesystem discovery, project/artifact registration, structural and state evidence, Git identity, historical artifact changes, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and a compact evidence-labelled project view.

The repair pass restored message identity compatibility, candidate extraction from both domain objects and persisted records, conversation-schema initialization for evidence linking, memory-aware continuity traversal, richer JSON provenance, Git ref parsing, explicit timeline event types, stable continuity identifiers, canonical provider external-ID resolution, and stable timestamps for idempotent candidate projection.

Project discovery preserves strong nested project boundaries in monorepo-like layouts and prevents a parent project's artifact scan from swallowing selected child-project artifacts.

The new `project-evidence-view` CLI presents four distinct evidence surfaces: current snapshot, historical project evidence, explicit conversation continuity, and current artifacts. Structural signals are explicitly treated as evidence rather than claims of intent, code quality, production readiness, or completion.

Discovery remains **read-only**: no source files are moved, renamed, deleted or executed.

## Verification status

GitHub Actions run #142 completed successfully across Python 3.11–3.14 after the canonical conversation identity assertion was repaired. The new project-evidence view and its test are now the remaining verification change for this cycle.

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
- **Compact project evidence:** snapshot/history/continuity/artifact view implemented with explicit evidence semantics.

## IMPL-03 completion gate

IMPL-03 is complete only after the latest CI matrix including the new evidence-view test is green and representative mixed workspace/monorepo-like discovery tests remain green. Structural signals remain evidence rather than claims of code quality, production readiness or project intent.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.**
