# IMPL-07 — Memory Consolidation

## Version
v1.0

## Business/user problem
V0 can preserve raw evidence, observations and reviewable candidates, but durable memory formation is still conservative and fragmented across memory, conversation, research and project paths. V1 needs a controlled mechanism for turning reviewed evidence into durable, queryable memory without losing provenance or historical state.

## Objective
Establish the first V1 consolidation boundary: reviewed candidates can become durable memory only through an explicit, provenance-preserving, conflict-aware process.

## Scope
- accepted candidate → durable memory promotion
- provenance retention
- duplicate detection
- conflict/supersession recording
- deterministic audit trail
- safe rollback/rejection semantics

## Out of scope
- autonomous deletion of memories
- opaque LLM-only consolidation
- automatic filesystem changes
- UI redesign
- cross-agent connectors

## Success condition
A reviewer can trace every newly consolidated memory back to its evidence and understand whether it is new, duplicate, conflicting, or superseding prior state.
