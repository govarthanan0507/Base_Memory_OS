# IMPL-03 PRD — Project & File Intelligence

**Version:** 0.3

## Product intent

Turn a messy local workspace into a searchable semantic project inventory without requiring filesystem cleanup, while retaining enough evidence to reconstruct how a project and its artifacts changed over time.

## User experience

1. Point Memory OS at a workspace.
2. Run a read-only discovery scan.
3. See likely projects and confidence.
4. Inspect project structure, technologies, entrypoints and artifact counts.
5. Inspect bounded state evidence such as tests, TODO/FIXME markers and recent code activity.
6. Re-scan later to refresh evidence and preserve artifact history.
7. Inspect a compact project evidence view separating current snapshot, history, explicit continuity and current artifacts.
8. Use the project/artifact graph and explicitly linked conversations for continuity and re-entry.

## Priorities

**P0:** safe discovery, project boundaries, artifact registry, repeatable scans.

**P1:** lightweight code structure/state evidence, artifact history, project timelines, explicit continuity and evidence views.

**P2:** full Git history, richer language analysis, semantic code understanding, automatic relationship discovery and content embeddings.

## Evidence semantics

Structural signals are deliberately presented as evidence. The product must not convert file counts, tests, TODOs, Git state or similar signals into unsupported claims about project intent, code quality, production readiness or completion.

## Constraints

Local-first, vendor-independent, no code execution during discovery, source-preserving, non-destructive. Explicit project↔conversation links are evidence-backed rather than silently inferred.
