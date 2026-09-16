# IMPL-02 TRD — Conversation Memory

**Version:** 0.2

## Paths

- `src/memory_os/conversation.py` — normalized conversation/message domain model and SQLite persistence
- `src/memory_os/importers.py` — provider-neutral local import adapters
- `src/memory_os/adapters.py` — provider-specific normalization boundary, currently including verified ChatGPT export mapping
- `src/memory_os/candidates.py` — conservative candidate extraction and persistence
- `src/memory_os/evidence.py` — accepted candidate → project-event projection
- `src/memory_os/continuity.py` — conversation/project context and re-entry rendering
- `src/memory_os/timeline.py` — project activity timeline rendering
- `src/memory_os/cli.py` — import, candidate review, project-evidence, timeline and re-entry commands
- `tests/test_conversation.py` — import, provenance and idempotency tests
- `tests/test_candidates.py` — candidate extraction tests
- `tests/test_evidence.py` — review boundary and projection idempotence tests
- `tests/test_integration.py` — end-to-end import → project → candidate → evidence → timeline → re-entry path

## Technical approach

Extend the existing SQLite source of truth with normalized `conversations` and `messages` records, reviewable candidate records, and append-only project events. Use deterministic identities so repeated imports and evidence projection remain idempotent.

## Normalized contract

A conversation has `conversation_id`, `source`, `title`, `started_at`, `ended_at`, `source_location` and JSON metadata. A message has `message_id`, `conversation_id`, sequence, role, content, observed timestamp and metadata. Candidates retain memory type, content, source message, confidence, status and metadata. Project events retain event type, observed timestamp and JSON provenance metadata.

## Evidence boundary

Extraction creates candidates only. Explicit review changes candidate status. Only accepted candidates may be promoted to durable memory or projected into project evidence. Projection retains candidate, conversation, source-message, confidence and evidence-status metadata.

## Timeline and continuity

Project timelines combine explicit project events, reviewed candidate evidence, graph relationships and known artifact modification timestamps. Re-entry views consume this evidence without claiming unsupported semantic history.

## Safety

Importers only read source files. Database writes occur in transactions where applicable. Discovery/import never moves or deletes source files. Candidate extraction is conservative and does not silently create durable memory.

## Provider boundary

Provider-specific exports are adapters into the normalized contract. Core storage does not depend on ChatGPT, Claude, Ollama or another vendor. New provider adapters require verified source formats before mapping provider-specific timestamps or fields.
