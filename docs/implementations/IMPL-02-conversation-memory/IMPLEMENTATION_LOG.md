# IMPL-02 — Conversation Memory Implementation Log

## Version

v0.1

## Status

In progress — normalized conversation storage and local import path implemented.

## Completed

- `src/memory_os/conversation.py`
  - provider-neutral `Conversation` and `Message` models
  - deterministic conversation/message IDs
  - SQLite persistence
  - duplicate-safe inserts
  - transactional validation and rollback
  - ordered message retrieval
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
- `tests/test_conversation.py`
  - idempotent import
  - source preservation
  - rollback behavior

## Next

1. Add export adapters for other providers, beginning with Claude-compatible local exports.
2. Preserve richer source timestamps and metadata where available.
3. Add conversation-to-project and conversation-to-artifact relations.
4. Add candidate memory extraction without committing inferred memories automatically.
5. Validate against a real user export fixture before declaring IMPL-02 complete.

## Safety

Import is additive and does not modify source export files. Files are not moved or deleted.
