# IMPL-03 — Project & File Intelligence Implementation Log

## Version

v0.5

## Status

In progress — safe filesystem discovery, artifact registration, structural/state evidence, Git metadata, artifact change history, timeline integration and explicit project↔conversation continuity are implemented.

## Completed

- Project root discovery using repository/build/dependency/readme markers.
- Strong-marker precedence so workspace-level README files do not swallow stronger child project boundaries.
- Git repository roots remain discoverable when the scan root is itself the project boundary.
- Pruning of common dependency, cache and generated directories.
- Read-only project inspection.
- Code-file classification.
- Bounded SHA-256 artifact hashing.
- Project-to-artifact `contains` relationships.
- Repeatable project/artifact persistence by root/location.
- README-derived project naming/summary evidence.
- Dependency-marker detection.
- Likely entrypoint detection.
- Lightweight Python AST import hints and JavaScript/TypeScript import hints.
- Project confidence based on available structural evidence.
- Direct read-only Git evidence for repository presence, branch and HEAD commit where available.
- ISO-8601 UTC artifact modification timestamps.
- Append-only artifact change events preserving old/new hash and modification-time evidence.
- Bounded project-state evidence: README presence, test presence/count, TODO/FIXME count and recent code-file activity.
- Deterministic `project-report` CLI output.
- Explicit project-to-conversation linking with entity validation.
- Accepted candidate projection now establishes project↔conversation continuity as part of the evidence trail.
- Project reports and project re-entry can surface linked conversations.
- Project timelines now include append-only artifact change events, including old/new hash and modification-time evidence.
- Tests for read-only behavior, root selection, structure/state analysis, Git metadata, repeatable scans, artifact history, timeline artifact-change rendering and conversation continuity.

## Current limitation

This remains structural intelligence, not full code comprehension. Git history beyond current branch/HEAD, commit-level activity, dependency resolution, AST analysis for languages beyond Python, semantic summaries, artifact-content embeddings and automatic project-to-conversation discovery are future layers.

Project-to-conversation linking is deliberately explicit/evidence-backed. The system does not silently guess that a conversation belongs to a project from a filename or keyword match.

The discovery layer does not execute discovered code and does not infer project intent solely from filenames as a durable fact.

Structural state evidence is deliberately not used to claim production readiness or code quality.

Automated test execution remains unverified in the available execution environment.

Representative real-workspace validation is not yet complete.

## Next

1. Validate discovery against representative real workspaces.
2. Harden root heuristics against mixed workspace layouts and monorepos using deterministic fixtures.
3. Add a compact project-evidence/re-entry view that distinguishes current artifact state from historical artifact changes.
4. Obtain reliable runtime/CI verification and then evaluate the IMPL-03 completion gate.

## Safety

Discovery is additive to the local Memory OS database. It never moves, deletes, renames or executes user source files. Original filesystem locations are retained as artifact provenance. Git metadata is read directly from repository metadata files rather than by running project code. Conversation links are explicit evidence relationships rather than silent inference.
