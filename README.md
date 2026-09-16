# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-02 — Conversation Memory v0.1**

IMPL-01 established the SQLite memory core, provenance, projects, artifacts, typed relationships, lexical retrieval, read-only project discovery, tests and CI.

IMPL-02 now adds normalized conversation/message persistence plus provider-neutral local JSON and Markdown importers and CLI inspection. Conversation sources remain read-only and traceable.

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

## Status

IMPL-01 foundation: implemented and locally verified.

IMPL-02 conversation normalization: first usable path implemented; provider-specific adapters and semantic extraction remain future work.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS
