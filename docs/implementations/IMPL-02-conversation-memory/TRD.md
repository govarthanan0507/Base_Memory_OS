# IMPL-02 TRD — Conversation Memory

**Version:** 0.1

## Paths

- `src/memory_os/conversation.py` — normalized conversation/message domain model and SQLite persistence
- `src/memory_os/importers.py` — provider-neutral local import adapters
- `tests/test_conversation.py` — import and idempotency tests
- `src/memory_os/cli.py` — future `import-conversation` command

## Technical approach

Extend the existing SQLite source of truth with `conversations` and `messages` tables. Use deterministic SHA-256 identities derived from source and external message identifiers when available; use content/sequence fallback for local transcripts.

## Normalized contract

A conversation has `conversation_id`, `source`, `title`, `started_at`, `ended_at`, `source_location` and JSON metadata. A message has `message_id`, `conversation_id`, sequence, role, content, observed timestamp and metadata.

## Safety

Importers only read source files. Database writes occur in a transaction so validation failures roll back the complete import.

## Provider boundary

Provider-specific exports are adapters into the normalized contract. Core storage does not depend on ChatGPT, Claude, Ollama or another vendor.
