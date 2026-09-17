# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-04 — Research Memory v0.4 — explicit source-ingestion pipeline**

IMPL-03 established read-only filesystem/project intelligence, artifact registration and history, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and an evidence-labelled project view.

IMPL-04 now provides a provider-neutral research-source boundary that normalizes external HTTP(S) URLs, conservatively classifies common research sources, preserves provenance, and registers sources as deduplicated artifacts using deterministic IDs.

The content layer can explicitly capture bounded text responses, hash them with SHA-256, persist them as separate JSON evidence snapshots, and attach snapshot provenance to the source artifact. A separate URL-only metadata adapter extracts safe provider/resource identity hints for YouTube, `youtu.be`, GitHub and GitLab without making network calls.

The v0.4 ingestion pipeline now composes those stages explicitly: register the source, derive URL metadata, optionally capture bounded evidence, persist the snapshot, and attach its provenance. Network I/O happens only when `capture=True` is requested.

These layers deliberately preserve the distinction between **URL observation, captured evidence, verification and semantic understanding**.

## Verification status

IMPL-04 v0.4 is CI-verified by GitHub Actions workflow `tests`, run #186 (`35181985251`), at head `90c36bfc433baddd66b9b642589ac4c8ef2575b0`. The Python 3.11, 3.12, 3.13 and 3.14 matrix jobs all completed successfully, including the new ingestion-pipeline tests.

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
- **IMPL-04 research identity:** URL normalization, source classification, deterministic research artifact identity and duplicate-safe registration implemented and CI-verified.
- **IMPL-04 source capture:** bounded text capture, SHA-256 snapshot identity, local JSON evidence persistence and idempotent provenance attachment implemented and CI-verified in the v0.4 matrix.
- **IMPL-04 URL metadata:** provider-neutral YouTube/GitHub/GitLab identity hints implemented without network access and CI-verified.
- **IMPL-04 ingestion pipeline:** explicit register → metadata → optional capture → snapshot → provenance flow implemented with offline integration tests and CI-verified across Python 3.11–3.14.

## IMPL-04 evidence boundary

```text
SOURCE REGISTERED
      ↓
URL-DERIVED HINTS       ← observation only
      ↓
SOURCE CAPTURED         ← optional, bounded
      ↓
SNAPSHOT HASHED
      ↓
SNAPSHOT PRESERVED
      ↓
PROVENANCE ATTACHED
      ↓
SOURCE VERIFIED        ← not implied
      ↓
SOURCE UNDERSTOOD      ← future layer
```

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README and the implementation log must be updated after every implementation iteration, before the next `go on` cycle is considered complete. Failures and remediation remain in the log rather than being rewritten away.**
