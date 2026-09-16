# IMPL-02 PRD — Conversation Memory

**Version:** 0.2

## Product intent

Make conversations first-class work artifacts. The user should be able to bring an export or local transcript into Memory OS without learning a provider-specific schema, then recover project context without turning every conversational statement into trusted memory.

## User experience

1. Point Memory OS at a local conversation file.
2. Import into the normalized conversation store.
3. Preserve the original source path and provenance.
4. Re-import safely when the same source is encountered again.
5. Extract conservative memory candidates from explicit language.
6. Review candidates explicitly as accepted or rejected.
7. When a candidate is accepted and associated with a project, project it into project history with provenance.
8. Use the project timeline and re-entry brief to recover context later.

## Priorities

**P0:** normalized storage, provenance, duplicate-safe import, tests.

**P1:** JSON/Markdown/ChatGPT adapters, CLI import and review workflow, candidate extraction, project evidence and re-entry.

**P2:** broader provider adapters and semantic consolidation.

## Constraints

Local-first, source-preserving, vendor-independent, no mandatory LLM, no destructive source operations, explicit review before durable promotion or project-evidence projection.
