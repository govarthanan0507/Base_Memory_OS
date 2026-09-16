# IMPL-02 — Conversation Memory Implementation Log

## Version

v0.3

## Status

In progress — normalized conversation storage, local import, graph linkage, and project/conversation re-entry foundations implemented.

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
- `src/memory_os/cli.py`
  - `import-conversation`
  - `import-chatgpt-export`
  - `show-conversation`
  - `list-conversations`
  - `reentry`
  - `reentry-project`
- `src/memory_os/continuity.py`
  - related-record traversal
  - compact conversation context packet
  - one-hop project-to-artifact expansion for conversation re-entry
  - project context containing linked conversations, artifacts, and linked memories
  - deterministic Markdown conversation and project re-entry briefs
- Tests
  - idempotent conversation import
  - source preservation
  - rollback behavior
  - conversation → project → artifact continuity
  - project-centric conversation/artifact/memory continuity
  - missing-entity behavior

## Current limitation

Re-entry is still evidence-based graph retrieval, not semantic reconstruction. It does not yet infer decisions, unresolved questions, tasks, project status changes, or a next smallest experiment from conversation content. Those capabilities belong to the candidate-memory and consolidation layer.

## Next

1. Add candidate memory extraction without committing inferred memories automatically.
2. Preserve richer source timestamps and metadata where available.
3. Add explicit conversation/project/artifact relation helpers where they improve correctness and ergonomics.
4. Validate against a real user export fixture before declaring IMPL-02 complete.
5. Add provider adapters only from verified export formats; do not invent provider schemas.
6. Move toward project activity timelines and stronger multi-hop continuity.

## Safety

Import is additive and does not modify source export files. Files are not moved or deleted. Re-entry output is evidence-based and only includes relationships already present in the local graph. Inferred memory will remain candidate-only until an explicit promotion/consolidation mechanism exists.
