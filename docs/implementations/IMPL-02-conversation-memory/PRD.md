# IMPL-02 PRD — Conversation Memory

**Version:** 0.1

## Product intent

Make conversations first-class work artifacts. The user should be able to bring an export or local transcript into Memory OS without learning a provider-specific schema.

## User experience

1. Point Memory OS at a local conversation file.
2. Import into the normalized conversation store.
3. Preserve the original source path and provenance.
4. Re-import safely when the same source is encountered again.
5. Later milestones can build memory candidates and re-entry views from these records.

## Priorities

**P0:** normalized storage, provenance, duplicate-safe import, tests.

**P1:** JSON/Markdown adapters and CLI import command.

**P2:** provider-specific adapters and semantic extraction.

## Constraints

Local-first, source-preserving, vendor-independent, no mandatory LLM, and no destructive source operations.
