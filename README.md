# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.2**

IMPL-01 established the SQLite memory core, provenance, projects, artifacts, typed relationships and lexical retrieval. IMPL-02 established normalized conversations, provider-neutral imports, continuity, candidate review, project evidence, timelines and re-entry briefs.

IMPL-03 now provides a filesystem intelligence layer. Memory OS can discover likely project roots, inspect project structure without executing code, register files as artifacts, connect artifacts to projects, and retain evidence such as dependency markers, likely entrypoints and lightweight import hints.

Discovery is deliberately **read-only**. It does not move, rename, delete or execute user files. Physical filesystem organization remains separate from the semantic project overlay.

Project inspection is intentionally evidence-based rather than pretending to understand an entire codebase. Current structural evidence includes file/code counts, dependency markers, README-derived summaries, likely entrypoints, bounded content hashes, lightweight Python/JavaScript/TypeScript import hints, and Git branch/HEAD metadata read directly from `.git` files.

Rescans are repeatable: projects are keyed by root location and artifacts by file location. Artifact state changes are now preserved as append-only `artifact_events`, so a later scan can show that a file changed instead of silently erasing its prior observed hash/mtime.

A deterministic `project-report` CLI command exposes the stored project evidence, registered artifacts and project events without executing project code.

## Design principles

1. Preserve raw evidence and provenance.
2. Prefer observed facts over unsupported inference.
3. Never move or delete user files during discovery or import.
4. Keep project understanding separate from physical filesystem organization.
5. Preserve temporal history rather than silently overwriting it.
6. Keep external model providers replaceable.
7. Build in small, testable increments.
8. Do not commit inferred durable memory blindly; preserve evidence first.
9. Treat extracted memories as reviewable candidates before durable promotion.
10. Keep continuity anchored to conversations, projects, artifacts and their relationships.
11. Preserve lifecycle history instead of treating current state as the whole story.
12. Preserve richer provenance discovered by later imports rather than discarding it.
13. Normalize source timestamps without discarding original source values.
14. Only project candidate-derived project milestones after explicit review acceptance.
15. Treat filesystem discovery as a semantic overlay, not a filesystem cleanup operation.
16. Do not execute discovered code as part of project intelligence.
17. Treat observed Git metadata as evidence, not as a claim about project health or quality.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented through evidence projection; completion gate remains pending reliable runtime verification and a real sanitized export.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented as conservative, provenance-preserving candidate generation.
- **Project activity timeline:** implemented from explicit events, reviewed candidate evidence, recorded relationships and artifact modification evidence.
- **Accepted candidate → project evidence:** implemented with provenance and idempotent projection, including CLI access.
- **IMPL-03 project discovery:** implemented as a read-only structural intelligence layer.
- **IMPL-03 artifact registry linkage:** implemented with bounded SHA-256 hashes and project containment relationships.
- **IMPL-03 structural evidence:** dependency markers, likely entrypoints, lightweight import hints and Git branch/HEAD metadata implemented.
- **IMPL-03 artifact change history:** implemented with append-only artifact events and idempotent repeated scans.
- **IMPL-03 project report:** implemented as a deterministic CLI view of stored structural evidence.
- **Automated test execution:** test suites exist, but the current execution environment has not provided a successful end-to-end test run, so CI/runtime verification is not claimed here.

## IMPL-03 completion gate

Before IMPL-03 is declared complete, discovery must be exercised against representative real workspaces, project-to-conversation continuity must be validated, and the project-state evidence model must be hardened. Git evidence and artifact-change tracking are now implemented. Discovery must remain non-destructive.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.** It records the current milestone, implemented capabilities, known verification status, and next major path. Detailed behavior and implementation decisions remain in the versioned BRD/FRD/PRD/TRD documents under `docs/`.
