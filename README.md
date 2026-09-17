# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-03 — Project & File Intelligence v0.6 — CI repair**

IMPL-01 established the SQLite memory core. IMPL-02 established normalized conversations, provider-neutral imports, continuity, candidate review, project evidence, timelines and re-entry briefs. IMPL-03 adds read-only filesystem/project intelligence.

The project layer discovers likely roots, inspects structure without executing code, registers files as artifacts, preserves bounded hashes and modification evidence, records Git identity, tracks historical artifact changes, and connects projects with conversations through explicit evidence. Project timelines expose historical artifact changes.

A GitHub Actions test run exposed integration regressions that were previously hidden because local runtime verification had not been available. This iteration repairs the discovered compatibility boundaries: message identity is now accepted as an explicit field while retaining deterministic fallback identity; candidate extraction accepts both domain `Message` objects and persisted message dictionaries; explicit project/conversation linking initializes its conversation schema; continuity recognizes memory entities; JSON imports preserve richer supplied source provenance; Git ref parsing correctly strips the full `refs/heads/` prefix; timeline tests distinguish initial discovery events from later change events.

Discovery remains **read-only**: no source files are moved, renamed, deleted or executed.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification is now being actively exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with provenance-preserving candidates and explicit review.
- **Project activity timeline:** implemented from explicit events, relationships and artifact evidence, including historical changes.
- **IMPL-03 project discovery:** implemented as a read-only structural intelligence layer.
- **IMPL-03 state evidence:** implemented with tests, TODO/FIXME and recent activity signals.
- **IMPL-03 root hardening:** strong-marker precedence implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **CI repair:** first full GitHub Actions run exposed 3 failures and 11 errors across 38 tests; the principal compatibility causes identified in that run have been patched in this iteration. A new CI run is required before claiming green verification.

## IMPL-03 completion gate

Before IMPL-03 is declared complete, the repaired implementation must pass CI and discovery must be exercised against representative mixed workspaces/monorepo-like layouts. Structural signals remain evidence rather than claims of code quality, production readiness or project intent.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README must be updated after every implementation iteration, before the next `go on` cycle is considered complete.**
