# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-04 — Research Memory v0.1 — canonical external-source identity**

IMPL-03 established read-only filesystem/project intelligence, artifact registration and history, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and an evidence-labelled project view.

IMPL-04 now adds a provider-neutral `ResearchSource` boundary that normalizes external HTTP(S) URLs, conservatively classifies common research sources (video, repository, document, website), preserves provenance/capture metadata, and registers sources as deduplicated artifacts using deterministic IDs.

A refinement corrected an important identity-boundary bug: an omitted research source type now triggers URL classification instead of silently defaulting to `website`. The regression test covers a YouTube URL registered without an explicit type.

Research registration is intentionally **not content verification**. This slice records source identity only; it does not fetch, parse, summarize, or claim that an external page was independently verified.

## Verification status

The source-classification remediation and its regression test are committed. GitHub Actions verification for the new test-bearing commits is pending and will be recorded in the IMPL-04 engineering log; no unverified CI result is presented as green.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification is exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with explicit review and provenance.
- **Project activity timeline:** implemented from project events, relationships and artifact evidence, including historical changes.
- **IMPL-03 project discovery:** implemented as a non-executing structural intelligence layer.
- **IMPL-03 state evidence:** tests, TODO/FIXME and recent activity signals implemented.
- **IMPL-03 root hardening:** strong-marker precedence, code-only discovery, and nested strong-project boundaries implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **Canonical identity boundary:** provider-facing conversation external IDs are resolved to stable internal conversation IDs before graph linking.
- **Compact project evidence:** snapshot/history/continuity/artifact view implemented with explicit evidence semantics.
- **IMPL-04 research identity:** URL normalization, source classification, deterministic research artifact identity and duplicate-safe registration implemented.

## IMPL-04 current gate

The research identity slice is complete only after its regression test is green in the repository CI matrix. The next slice is source-content/metadata capture with explicit provenance; semantic synthesis remains deliberately out of scope until source capture is reliable.

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README and the implementation log must be updated after every implementation iteration, before the next `go on` cycle is considered complete. Failures and remediation remain in the log rather than being rewritten away.**
