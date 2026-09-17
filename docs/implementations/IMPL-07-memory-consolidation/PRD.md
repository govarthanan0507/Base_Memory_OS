# IMPL-07 — Product Requirements

## Version
v1.0

## Product behavior
Memory formation is a staged workflow rather than an implicit side effect:

`evidence → observation → candidate → human review → consolidation → durable memory`

The user must be able to inspect why a memory exists, where it came from, and what changed when newer evidence conflicts with it.

## Priority
P0: reviewed-candidate promotion, provenance, duplicate safety, conflict preservation.

P1: explicit supersession and audit queries.

P2: richer consolidation heuristics and optional local-model assistance.

## UX/CLI expectation
The first V1 implementation should expose a small, deterministic programmatic API and CLI surface. It should not require an LLM or external service.

## Non-goals
No automatic deletion, silent overwrite, forced focus behavior, or vendor-specific memory format.
