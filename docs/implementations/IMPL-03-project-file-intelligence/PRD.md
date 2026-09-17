# IMPL-03 PRD — Project & File Intelligence

**Version:** 0.2

## Product intent

Turn a messy local workspace into a searchable semantic project inventory without requiring filesystem cleanup.

## User experience

1. Point Memory OS at a workspace.
2. Run a read-only discovery scan.
3. See likely projects and confidence.
4. Inspect project structure, technologies, entrypoints and artifact counts.
5. Inspect bounded state evidence such as tests, TODO/FIXME markers and recent code activity.
6. Re-scan later to refresh evidence and preserve artifact history.
7. Use the resulting project/artifact graph for continuity and re-entry.

## Priorities

**P0:** safe discovery, project boundaries, artifact registry, repeatable scans.

**P1:** lightweight code structure and state evidence, project summaries, explicit continuity links.

**P2:** Git history, richer language analysis, semantic code understanding and content embeddings.

## Constraints

Local-first, vendor-independent, no code execution during discovery, source-preserving, non-destructive. Evidence is presented as evidence; the product must not convert structural signals into unsupported claims about intent, quality or production readiness.
