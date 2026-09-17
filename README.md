# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.7 — integration repair pass**

IMPL-03 now has read-only filesystem discovery, project/artifact registration, structural and state evidence, Git identity, historical artifact changes, project timelines, and explicit project↔conversation continuity. This cycle also used the repository's real GitHub Actions execution as a diagnostic loop rather than assuming local correctness.

The CI run exposed integration mismatches between domain objects and persisted records. The repair pass now restores explicit message identity compatibility, lets candidate extraction consume both `Message` objects and persisted dictionaries, initializes conversation schema before explicit evidence linking, recognizes memory entities in continuity traversal, preserves richer JSON source provenance, corrects Git `refs/heads/*` parsing, distinguishes discovered artifacts from later artifact changes in timeline tests, and renders timeline event types explicitly.

Discovery remains **read-only**: no source files are moved, renamed, deleted or executed.

## Verification status

GitHub Actions is now exercising **38 tests** across Python 3.11–3.14. The first diagnostic run failed with 3 failures and 11 errors; the subsequent repair run reduced this to 2 failures and 6 errors, confirming that several compatibility defects were fixed while also exposing the remaining issues. The current branch therefore must not yet be called green.

Remaining repair targets are centered on test fixture/entity semantics and discovery artifact-root behavior. CI remains the source of runtime truth for the completion gate.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification is actively exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with explicit review and provenance.
- **Project activity timeline:** implemented from project events, relationships and artifact evidence, including historical changes.
- **IMPL-03 project discovery:** implemented as a non-executing structural intelligence layer.
- **IMPL-03 state evidence:** tests, TODO/FIXME and recent activity signals implemented.
- **IMPL-03 root hardening:** strong-marker precedence and code-only project discovery implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **CI repair pass:** active; multiple real integration defects have been identified and patched.

## IMPL-03 completion gate

IMPL-03 is not complete until the remaining CI failures are resolved, the full matrix is green, and discovery is validated against representative mixed workspaces/monorepo-like layouts. Structural signals remain evidence rather than claims of code quality, production readiness or project intent.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.**
