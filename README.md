# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.5**

IMPL-01 established the SQLite memory core, provenance, projects, artifacts, typed relationships and lexical retrieval. IMPL-02 established normalized conversations, provider-neutral imports, continuity, candidate review, project evidence, timelines and re-entry briefs.

IMPL-03 provides a filesystem intelligence layer. Memory OS can discover likely project roots, inspect project structure without executing code, register files as artifacts, connect artifacts to projects, and retain evidence such as dependency markers, likely entrypoints, lightweight import hints and bounded project-state signals.

Discovery is deliberately **read-only**. It does not move, rename, delete or execute user files. Physical filesystem organization remains separate from the semantic project overlay.

Project inspection is intentionally evidence-based rather than pretending to understand an entire codebase. Current structural evidence includes file/code counts, dependency markers, README-derived summaries, likely entrypoints, bounded content hashes, lightweight Python/JavaScript/TypeScript import hints, Git branch/HEAD metadata read directly from `.git` files, test presence/count, bounded TODO/FIXME counts and recent code-file activity.

Root detection gives stronger project markers (Git/build/dependency manifests) precedence over README-only workspace boundaries, reducing false project roots. A Git root remains discoverable when it is itself the project boundary.

Rescans are repeatable: projects are keyed by root location and artifacts by file location. Artifact state changes are preserved as append-only `artifact_events`, so later scans can show that a file changed instead of silently erasing its prior observed hash/mtime.

Project timelines now expose those historical artifact-change events alongside project events, relationships and current artifact modification evidence. This makes filesystem evolution part of the continuity trail rather than merely a current snapshot.

Project/conversation continuity is explicit rather than inferred silently. A known project and conversation can be linked with evidence, and accepted candidate projection also creates that continuity link. `reentry-project` and `project-report` can therefore expose the conversation trail alongside project artifacts and events.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented through evidence projection; completion gate remains pending reliable runtime verification and a real sanitized export.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented as conservative, provenance-preserving candidate generation.
- **Project activity timeline:** implemented from explicit events, reviewed candidate evidence, relationships and artifact modification/change evidence.
- **Accepted candidate → project evidence:** implemented with provenance and idempotent projection, including CLI access.
- **IMPL-03 project discovery:** implemented as a read-only structural intelligence layer.
- **IMPL-03 artifact registry linkage:** implemented with bounded SHA-256 hashes and project containment relationships.
- **IMPL-03 structural/state evidence:** implemented with dependency markers, entrypoints, import hints, Git identity, test signals, TODO/FIXME signals and recent code activity.
- **IMPL-03 root hardening:** initial strong-marker precedence and workspace README protection implemented.
- **IMPL-03 artifact change history:** implemented with append-only artifact events and idempotent repeated scans.
- **IMPL-03 timeline integration:** artifact history is now surfaced in project timelines.
- **IMPL-03 project↔conversation continuity:** explicit linking and candidate-backed linking implemented; re-entry/report surfaces linked conversations.
- **Automated test execution:** test suites exist, but the current execution environment has not provided a successful end-to-end test run, so CI/runtime verification is not claimed here.

## IMPL-03 completion gate

Before IMPL-03 is declared complete, discovery must be exercised against representative real workspaces, including mixed workspace layouts and monorepo-like structures, and runtime verification must be obtained. Structural/state evidence remains evidence rather than a definitive project-health or production-readiness judgment. Discovery must remain non-destructive.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.** It records the current milestone, implemented capabilities, known verification status, and next major path. Detailed behavior and implementation decisions remain in the versioned BRD/FRD/PRD documents under `docs/`.
