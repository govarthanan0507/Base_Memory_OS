# IMPL-02 — Conversation Memory Implementation Log

## Version

v0.8

## Status

In progress — normalized conversation storage, local import, graph linkage, candidate-memory admission, project re-entry, project activity timeline, role-aware candidate extraction, historical project events, and richer re-import provenance implemented.

## Completed

- `src/memory_os/conversation.py`
  - provider-neutral `Conversation` and `Message` models
  - deterministic conversation/message IDs
  - SQLite persistence
  - duplicate-safe inserts
  - transactional validation and rollback
  - ordered message retrieval
  - single-conversation retrieval
  - conversation listing
  - re-import merging for richer conversation timestamps/source location/metadata
  - re-import merging for richer message timestamps/metadata
  - existing evidence is preserved when a later import omits a field
- `src/memory_os/importers.py`
  - normalized JSON importer
  - Markdown role-marker importer
  - ChatGPT export importer
- `src/memory_os/adapters.py`
  - ChatGPT export normalization
  - provider-neutral generic normalization boundary
- `src/memory_os/continuity.py`
  - related-record traversal
  - compact conversation context packet
  - one-hop project-to-artifact expansion for conversation re-entry
  - project context containing linked conversations, artifacts, and linked memories
  - deterministic Markdown conversation and project re-entry briefs
- `src/memory_os/candidates.py`
  - conservative extraction of explicit decisions, preferences, tasks, and unresolved items
  - candidate-only output with confidence and source message provenance
  - role-aware confidence adjustment for personal decision/preference signals
  - optional project context attached to candidate metadata
  - no automatic durable-memory promotion
- `src/memory_os/core.py`
  - persistent reviewable candidate storage
  - candidate status lifecycle
  - explicit accept/reject review boundary
  - accepted candidates can be promoted to durable memories with provenance
  - append-only project event records for project creation and status changes
  - explicit project-event API with idempotent event identity
- `src/memory_os/cli.py`
  - `extract-candidates`
  - `list-candidates`
  - `review-candidate`
  - `timeline-project`
- `src/memory_os/timeline.py`
  - project activity timeline from explicit project events, recorded relationships, and artifact modification timestamps
  - deterministic Markdown timeline rendering
- Tests
  - idempotent conversation import
  - richer provenance merge on re-import
  - source preservation
  - rollback behavior
  - conversation → project → artifact continuity
  - project-centric conversation/artifact/memory continuity
  - candidate extraction and admission boundary
  - role-aware candidate confidence and project context
  - project creation/status-change history and explicit event idempotence
  - project timeline and missing-project behavior

## Current limitation

Project events currently record explicit lifecycle changes made through the store API. They do not yet infer semantic milestones from conversations, code changes, commits, or artifact content.

The timeline remains evidence-based. It does not yet reconstruct the complete semantic history of a project or automatically infer changed decisions and unresolved threads.

Candidate extraction is intentionally heuristic and conservative. It is not yet a semantic/LLM consolidation engine, and provider-specific adapters are still limited to verified input shapes.

## Next

1. Add evidence-derived project events from imported conversations and project/file discovery.
2. Validate against a real user export fixture before declaring IMPL-02 complete.
3. Add provider adapters only from verified export formats; do not invent provider schemas.
4. Begin stronger multi-hop continuity and cross-agent source reconciliation.
5. Prepare the IMPL-02 completion gate and transition into IMPL-03 Project & File Intelligence.

## Safety

Import is additive and does not modify source export files. Files are not moved or deleted. Re-entry and timeline output are evidence-based and only include relationships, explicit project events, or timestamps recorded in the local graph. Inferred memory remains candidate-only until explicit review accepts it.
