# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-02 — Conversation Memory v1.1**

IMPL-01 established the SQLite memory core, provenance, projects, artifacts, typed relationships, lexical retrieval, read-only project discovery, tests and CI.

IMPL-02 now provides normalized conversation/message persistence, provider-neutral import boundaries, ChatGPT export ingestion, conversation/project/artifact continuity, conversation and project re-entry briefs, conservative memory-candidate extraction, explicit candidate review/promotion, project activity timelines, role/project-aware candidate evidence, historical project lifecycle events, richer provenance merging on re-import, normalized ChatGPT source timestamps, and evidence projection from accepted conversation candidates into project events.

The candidate layer is deliberately **review-first**: extracted decisions, preferences, tasks and unresolved items are not treated as durable memory automatically. Candidates retain source conversation/message provenance. User-authored personal decision/preference signals receive stronger evidence confidence than equivalent assistant-authored statements, and candidates can carry an associated project identifier when known.

Accepted candidates can now become **project evidence** without losing their provenance. A reviewed candidate can generate an idempotent project event containing the candidate ID, conversation ID, source message ID, confidence and evidence status. Rejected or unreviewed candidates are not projected into the project timeline. The projection is currently exposed as a library capability and is the next candidate for CLI workflow integration.

Conversation re-import is **evidence-preserving**. A later import can add timestamps, source location, external IDs, or metadata that was missing from the first import without replacing already-known values with blanks. Message-level timestamps and metadata are merged in the same way.

ChatGPT exports now have source epoch timestamps normalized to UTC ISO-8601, with message-level observed times and selected raw structural metadata retained for provenance.

Project lifecycle changes are preserved as explicit append-only events rather than only overwriting the current project status. The timeline therefore has historical evidence while current state remains directly queryable.

The project timeline is still **evidence-based**: it combines explicit project events, reviewed candidate evidence, recorded graph relationships, and known artifact modification timestamps. It does not yet claim to reconstruct the complete semantic history of a project.

The system is provider-neutral. Model runtimes such as Ollama are adapters, not the memory core itself.

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
15. Preserve candidate provenance when projecting reviewed evidence into project history.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented through the current evidence-projection milestone.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction:** implemented as conservative, provenance-preserving candidate generation.
- **Candidate persistence/review boundary:** implemented; explicit acceptance is required for durable promotion.
- **Project activity timeline:** implemented from explicit events, reviewed candidate evidence, recorded relationships and artifact modification evidence.
- **Role/project-aware candidates:** implemented with role-sensitive confidence and optional project context.
- **Historical project events:** implemented for project creation and status changes, plus explicit idempotent event insertion.
- **Conversation provenance merge:** implemented for later-discovered conversation/message timestamps and metadata.
- **ChatGPT timestamp normalization:** implemented for conversation/message source timestamps with UTC normalization and raw timestamp retention.
- **Accepted candidate → project evidence:** implemented with provenance and idempotent projection.
- **Automated test execution:** test suites exist, but the current execution environment has not provided a successful end-to-end test run, so CI/runtime verification is not claimed here.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.** It records the current milestone, implemented capabilities, known verification status, and next major path. Detailed behavior and implementation decisions remain in the versioned BRD/FRD/PRD/TRD documents under `docs/`.
