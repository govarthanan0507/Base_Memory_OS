# IMPL-03 — Project & File Intelligence Implementation Log

## Version

v0.7

## Status

In progress — safe filesystem discovery, artifact registration, structural/state evidence, Git metadata, artifact change history, timeline integration, explicit project↔conversation continuity, and a CI-driven integration repair pass are implemented.

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
- Continuity views now expose stable entity identifiers and display names consistently across projects, artifacts, conversations and memories.
- Conversation re-entry avoids re-expanding the conversation itself through a project relation.
- Candidate persistence now assigns a stable observed timestamp when the source message has none, preventing repeated candidate projection from producing different project-event identities.
- Explicit evidence linking accepts either a canonical conversation ID or its provider external ID, while storing the canonical relationship target.
- GitHub Actions now executes the test suite across Python 3.11–3.14 and has exposed several real integration defects that were repaired in sequence.

## CI evidence

The initial CI diagnostic run executed 38 tests and reported 3 failures plus 11 errors. Repair passes eliminated the candidate-store, candidate-extraction, discovery-artifact and most continuity/evidence compatibility defects. The latest observed run narrowed the remaining issues to continuity self-expansion and candidate-event idempotence; both were patched in the current branch. A fresh full-matrix run is required before declaring the branch green.

## Current limitation

This remains structural intelligence, not full code comprehension. Git history beyond current branch/HEAD, commit-level activity, dependency resolution, AST analysis for languages beyond Python, semantic summaries, artifact-content embeddings and automatic project-to-conversation discovery are future layers.

Project-to-conversation linking is deliberately explicit/evidence-backed. The system does not silently guess that a conversation belongs to a project from a filename or keyword match.

The discovery layer does not execute discovered code and does not infer project intent solely from filenames as a durable fact.

Structural state evidence is deliberately not used to claim production readiness or code quality.

Representative real-workspace validation is not yet complete.

## Next

1. Verify the current repair pass with a fresh full CI matrix.
2. Add deterministic representative mixed-workspace and monorepo-like fixtures.
3. Add a compact project-evidence/re-entry view that distinguishes current artifact state from historical artifact changes.
4. Re-run the IMPL-03 completion gate only after CI is green and representative discovery fixtures pass.

## Safety

Discovery is additive to the local Memory OS database. It never moves, deletes, renames or executes user source files. Original filesystem locations are retained as artifact provenance. Git metadata is read directly from repository metadata files rather than by running project code. Conversation links are explicit evidence relationships rather than silent inference.
