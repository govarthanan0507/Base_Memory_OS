# IMPL-02 — Conversation Memory Implementation Log

## Version

v0.5

## Status

In progress — normalized conversation storage, local import, graph linkage, candidate-memory admission, project re-entry, and project activity timeline foundations implemented.

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
  - no automatic durable-memory promotion
- `src/memory_os/core.py`
  - persistent reviewable candidate storage
  - candidate status lifecycle
  - explicit accept/reject review boundary
  - accepted candidates can be promoted to durable memories with provenance
- `src/memory_os/cli.py`
  - `extract-candidates`
  - `list-candidates`
  - `review-candidate`
  - `timeline-project`
- `src/memory_os/timeline.py`
  - project activity timeline from recorded relationships and artifact modification timestamps
  - deterministic Markdown timeline rendering
- Tests
  - idempotent conversation import
  - source preservation
  - rollback behavior
  - conversation → project → artifact continuity
  - project-centric conversation/artifact/memory continuity
  - candidate extraction and admission boundary
  - project timeline and missing-project behavior

## Current limitation

The timeline is currently an evidence timeline, not a full inferred project history. It uses recorded graph relationships and known artifact modification timestamps; it does not yet reconstruct semantic milestones, changed decisions, unresolved threads, or project status transitions from all available evidence.

Candidate extraction is intentionally heuristic and conservative. It is not yet a semantic/LLM consolidation engine, and provider-specific adapters are still limited to verified input shapes.

## Next

1. Strengthen candidate extraction with conversation/project context and source-role filtering.
2. Preserve richer source timestamps and metadata consistently across all import paths.
3. Add semantic project activity events and status transitions without overwriting historical evidence.
4. Validate against a real user export fixture before declaring IMPL-02 complete.
5. Add provider adapters only from verified export formats; do not invent provider schemas.
6. Begin stronger multi-hop continuity and cross-agent source reconciliation.

## Safety

Import is additive and does not modify source export files. Files are not moved or deleted. Re-entry and timeline output are evidence-based and only include relationships or timestamps recorded in the local graph. Inferred memory remains candidate-only until explicit review accepts it.
