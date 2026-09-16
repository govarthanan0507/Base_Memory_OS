# IMPL-02 BRD — Conversation Memory

**Version:** 0.2

## Why this milestone exists

The user's work is distributed across ChatGPT, Claude, local agents and files. A project can begin in one conversation and continue somewhere else, creating a high context-reconstruction cost.

## Business/user problem

The Memory OS must preserve conversation history as durable work evidence without forcing the user to manually summarize every session. It must also distinguish conversation evidence from memories that have actually been reviewed and accepted.

## Outcome

A normalized, provider-neutral conversation store that preserves source, conversation identity, message order, timestamps and provenance; supports conservative candidate extraction and explicit review; and can connect accepted evidence to project history for continuity and re-entry.

## Scope

- normalized conversations and messages
- provider-neutral import contract
- local JSON and Markdown import paths
- ChatGPT export normalization with source timestamp preservation
- provenance and source metadata
- duplicate-safe import identity and richer re-import merging
- conservative candidate extraction and explicit review boundary
- project evidence projection from accepted candidates
- conversation/project re-entry and project timeline integration
- tests and documentation

## Non-goals

- provider-specific authentication
- automatic blind durable-memory extraction
- semantic LLM consolidation
- cloud synchronization
- deleting or rewriting source conversations
- claiming a complete semantic project history from incomplete evidence

## Success criteria

A conversation can be imported from a local source into SQLite, searched/retrieved by conversation identity, re-imported without duplicate messages, traced back to its source location, converted into reviewable candidates, and—only after explicit acceptance—projected into idempotent project evidence with preserved provenance.
