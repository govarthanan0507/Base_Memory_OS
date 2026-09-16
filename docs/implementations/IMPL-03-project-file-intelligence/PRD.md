# IMPL-03 PRD — Project & File Intelligence

**Version:** 0.1

## Product intent

Turn a messy local workspace into a searchable semantic project inventory without requiring filesystem cleanup.

## User experience

1. Point Memory OS at a workspace.
2. Run a read-only discovery scan.
3. See likely projects and confidence.
4. Inspect project structure, technologies, entrypoints and artifact counts.
5. Re-scan later to refresh evidence.
6. Use the resulting project/artifact graph for continuity and re-entry.

## Priorities

**P0:** safe discovery, project boundaries, artifact registry, repeatable scans.

**P1:** lightweight code structure analysis and project summaries.

**P2:** Git history, richer language analysis, semantic code understanding.

## Constraints

Local-first, vendor-independent, no code execution during discovery, source-preserving, and non-destructive.
