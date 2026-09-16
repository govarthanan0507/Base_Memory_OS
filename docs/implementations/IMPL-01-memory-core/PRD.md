# IMPL-01 PRD — Memory Core

**Version:** 0.1

## Product intent
Give the future Personal Memory OS a dependable local foundation that can answer: what was recorded, where it came from, when it was observed, and what work artifact/project it relates to.

## User experience for this increment
This increment is intentionally CLI-first. The user can initialize storage, add a memory, search memories, and scan a workspace. There is no UI requirement yet.

## Priority
P0: persistence, provenance, project/artifact registry, safe discovery, tests.
P1: richer search and relationship queries.
P2: model-assisted interpretation and UI.

## Product constraints
Local-first; vendor-neutral; read-only discovery; evidence-preserving; no silent deletion or movement of user data.

## Future compatibility
The schema and interfaces must allow conversation sources, research sources, Git repositories, generated artifacts and external model providers to be added without replacing the core store.
