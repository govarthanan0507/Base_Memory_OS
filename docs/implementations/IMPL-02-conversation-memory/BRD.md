# IMPL-02 BRD — Conversation Memory

**Version:** 0.1

## Why this milestone exists

The user's work is distributed across ChatGPT, Claude, local agents and files. A project can begin in one conversation and continue somewhere else, creating a high context-reconstruction cost.

## Business/user problem

The Memory OS must preserve conversation history as durable work evidence without forcing the user to manually summarize every session.

## Outcome

A normalized, provider-neutral conversation store that preserves source, conversation identity, message order, timestamps and provenance, and can later feed memory extraction and cross-agent continuity.

## Scope

- normalized conversations and messages
- provider-neutral import contract
- local JSON and Markdown import paths
- provenance and source metadata
- duplicate-safe import identity
- tests and documentation

## Non-goals

- provider-specific authentication
- automatic blind durable-memory extraction
- semantic summarization
- cloud synchronization
- deleting or rewriting source conversations

## Success criteria

A conversation can be imported from a local source into SQLite, searched/retrieved by conversation identity, re-imported without duplicate messages, and traced back to its source location.
