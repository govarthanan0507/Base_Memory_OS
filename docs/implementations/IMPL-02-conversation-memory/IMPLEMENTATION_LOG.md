# IMPL-02 — Conversation Memory Implementation Log

## Version

v1.1

## Status

In progress — normalized conversation storage, local import, graph linkage, candidate-memory admission, project re-entry, project activity timeline, role/project-aware candidate extraction, historical project events, richer re-import provenance, normalized ChatGPT source timestamps, and reviewed-candidate project evidence implemented.

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
  - epoch timestamp normalization to UTC ISO-8601
  - message-level observed timestamps
  - preservation of raw source timestamps and selected structural metadata
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
- `src/memory_os/evidence.py`
  - projects can receive events from explicitly accepted conversation candidates
  - candidate, conversation, message, confidence, and evidence status are retained in event metadata
  - repeated projection is idempotent
  - rejected/unreviewed candidates are not projected as project milestones
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
  - ChatGPT epoch timestamp normalization
  - metadata persistence
  - source preservation
  - rollback behavior
  - conversation → project → artifact continuity
  - project-centric conversation/artifact/memory continuity
  - candidate extraction and admission boundary
  - role-aware candidate confidence and project context
  - project creation/status-change history and explicit event idempotence
  - project timeline and missing-project behavior
  - accepted-candidate projection and idempotence

## Current limitation

Project events derived from conversation candidates require explicit candidate acceptance; the system does not silently infer durable project milestones. Code changes, commits, artifact content, and unreviewed conversation language are not yet semantic project events.

The timeline remains evidence-based. It does not yet reconstruct the complete semantic history of a project or automatically resolve changed decisions and unresolved threads.

Candidate extraction is intentionally heuristic and conservative. It is not yet a semantic/LLM consolidation engine, and provider-specific adapters are still limited to verified input shapes.

ChatGPT timestamp handling now preserves normalized UTC timestamps, but other providers still require verified adapters before provider-specific timestamp mapping is added.

The new evidence projection helper is currently a library-level capability; it is not yet wired into the CLI's normal review workflow.

## Next

1. Integrate accepted-candidate projection into the normal conversation/project workflow and CLI.
2. Validate against a real user export fixture before declaring IMPL-02 complete.
3. Add provider adapters only from verified export formats; do not invent provider schemas.
4. Add stronger multi-hop continuity and cross-agent source reconciliation.
5. Prepare the IMPL-02 completion gate and transition into IMPL-03 Project & File Intelligence.

## Safety

Import is additive and does not modify source export files. Files are not moved or deleted. Re-entry and timeline output are evidence-based and only include relationships, explicit project events, or timestamps recorded in the local graph. Inferred memory remains candidate-only until explicit review accepts it.
