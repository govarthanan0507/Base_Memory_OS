# IMPL-05 — Re-entry FRD v0.1

## Functional requirements

1. `project_context()` shall validate the project and return linked conversations, artifacts and memories.
2. It shall identify the latest linked conversation from persisted conversation timestamps.
3. It shall expose recent project events in descending timestamp order.
4. It shall expose only `candidate` memory candidates explicitly tagged to the project in candidate metadata.
5. `render_project_reentry_brief()` shall present these signals in deterministic sections.
6. Empty evidence shall be rendered explicitly rather than omitted.
7. Re-entry shall be read-only.

## Acceptance criteria

- Existing continuity tests remain green.
- A project with an unresolved candidate shows that candidate.
- A project with recent decisions shows recent activity.
- A project with no linked evidence reports the absence explicitly.
