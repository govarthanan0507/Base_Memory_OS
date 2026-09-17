# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-04 — Research Memory v0.3 — source identity, bounded evidence capture, URL metadata hints**

IMPL-03 established read-only filesystem/project intelligence, artifact registration and history, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and an evidence-labelled project view.

IMPL-04 now provides a provider-neutral research-source boundary that normalizes external HTTP(S) URLs, conservatively classifies common research sources, preserves provenance, and registers sources as deduplicated artifacts using deterministic IDs.

The content layer can explicitly capture bounded text responses, hash them with SHA-256, persist them as separate JSON evidence snapshots, and attach snapshot provenance to the source artifact. A separate URL-only metadata adapter now extracts safe provider/resource identity hints for YouTube, `youtu.be`, GitHub and GitLab without making network calls.

These layers deliberately preserve the distinction between **URL observation, captured evidence, verification and semantic understanding**.

## Verification status

The source-identity cycle is verified by GitHub Actions run #164 across Python 3.11–3.14. The v0.2/v0.3 source-capture and metadata test-bearing commits have been pushed to `main`; their CI result is still pending and will be recorded in the IMPL-04 implementation log before these slices are called green.

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
- **IMPL-04 source capture:** bounded text capture, SHA-256 snapshot identity, local JSON evidence persistence and idempotent provenance attachment implemented; CI verification pending.
- **IMPL-04 URL metadata:** provider-neutral YouTube/GitHub/GitLab identity hints implemented without network access; CI verification pending.

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
SOURCE VERIFIED        ← not implied
      ↓
SOURCE UNDERSTOOD      ← future layer
```

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README and the implementation log must be updated after every implementation iteration, before the next `go on` cycle is considered complete. Failures and remediation remain in the log rather than being rewritten away.**
