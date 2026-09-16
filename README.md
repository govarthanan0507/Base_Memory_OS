# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-02 — Conversation Memory v0.4**

IMPL-01 established the SQLite memory core, provenance, projects, artifacts, typed relationships, lexical retrieval, read-only project discovery, tests and CI.

IMPL-02 now provides normalized conversation/message persistence, provider-neutral import boundaries, ChatGPT export ingestion, conversation/project/artifact continuity, project and conversation re-entry briefs, and conservative memory-candidate extraction.

The candidate layer is deliberately **review-first**: extracted decisions, preferences, tasks and unresolved items are not treated as durable memory automatically. Candidates retain source conversation/message provenance and must cross an explicit review boundary before promotion.

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

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented through the current candidate-admission milestone.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction:** implemented as conservative, provenance-preserving candidate generation.
- **Candidate persistence/review boundary:** implemented; explicit acceptance is required for durable promotion.
- **Automated test execution:** test suites exist, but the current execution environment has not provided a successful end-to-end test run, so CI/runtime verification is not claimed here.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

After every implementation iteration, update this README with the current milestone, implemented capabilities, known verification status, and the next major path. The README is the high-level progress record; detailed behavior and implementation decisions remain in the versioned BRD/FRD/PRD/TRD documents under `docs/`.