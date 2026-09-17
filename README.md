# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-04 — Research Memory v0.6 — provenance-bound semantic candidates**

IMPL-03 established read-only filesystem/project intelligence, artifact registration and history, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and an evidence-labelled project view.

IMPL-04 provides a provider-neutral research-source boundary that normalizes external HTTP(S) URLs, conservatively classifies common research sources, preserves provenance, and registers sources as deduplicated artifacts using deterministic IDs.

The content layer can explicitly capture bounded text responses, hash them with SHA-256, persist them as separate JSON evidence snapshots, and attach snapshot provenance to the source artifact. A separate URL-only metadata adapter extracts safe provider/resource identity hints for YouTube, `youtu.be`, GitHub and GitLab without making network calls.

The ingestion pipeline composes those stages explicitly: register the source, derive URL metadata, optionally capture bounded evidence, persist the snapshot, and attach its provenance. Network I/O happens only when `capture=True` is requested.

The structural evidence layer inspects an already-captured snapshot deterministically for a title, headings, hyperlinks and absolute URLs. It preserves the snapshot hash and capture timestamp as provenance and does not invoke an LLM or make network requests. Malformed link resolution is now explicitly hardened so a bad URL cannot crash the extraction boundary.

The semantic-candidate layer consumes that preserved snapshot evidence and structural observations to identify conservative candidates for referenced repositories, explicitly introduced tools, ideas and source topics. Candidates remain reviewable records with exact evidence provenance; they are not automatically promoted to durable memory or verified claims. An offline integration test now exercises the full source → snapshot → observation → candidate chain and checks provenance on every candidate.

These layers deliberately preserve the distinction between **URL observation, captured evidence, structural observation, candidate extraction, verification and semantic understanding**.

## Verification status

IMPL-04 v0.4 ingestion tests are CI-verified by GitHub Actions workflow `tests`, run #186 (`35181985251`), with Python 3.11, 3.12, 3.13 and 3.14 matrix jobs successful.

Structural extraction run #200 (`35183355300`) exposed a malformed-link test problem. After the fixture was corrected in `84290f3ee5d4f45dcf7296f8b38d587ee8fb954b`, run #211 (`35184049758`) exposed the production robustness gap: `urljoin()` can raise `ValueError` for a malformed absolute reference. The production boundary was hardened in `ba8204e920136c0aee975dec8ab9d5b07e41ae0c` to ignore malformed URL-resolution/normalization errors. Fresh CI verification for the hardened/current head is still pending.

The semantic-candidate implementation, tests, and provenance-chain integration are committed. The newest head has not yet been claimed as CI-green.

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
- **IMPL-04 source capture:** bounded text capture, SHA-256 snapshot identity, local JSON evidence persistence and idempotent provenance attachment implemented and CI-verified.
- **IMPL-04 URL metadata:** provider-neutral YouTube/GitHub/GitLab identity hints implemented without network access and CI-verified.
- **IMPL-04 ingestion pipeline:** explicit register → metadata → optional capture → snapshot → provenance flow implemented with offline integration tests.
- **IMPL-04 structural evidence:** deterministic title/headings/link/URL observations over captured snapshots implemented; malformed URL resolution is hardened; fresh CI verification is pending.
- **IMPL-04 semantic candidates:** deterministic repository/tool/idea/topic candidate extraction implemented with provenance, confidence, review status and deduplication; fresh CI verification is pending.
- **IMPL-04 provenance-chain integration:** source → snapshot → observations → candidates is covered by an offline end-to-end regression test.

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
STRUCTURAL OBSERVATION  ← deterministic, evidence-bound
      ↓
SEMANTIC CANDIDATE      ← deterministic, reviewable
      ↓
DURABLE MEMORY / CLAIM  ← not automatic
      ↓
SOURCE VERIFIED         ← not implied
```

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README and the implementation log must be updated after every implementation iteration, before the next `go on` cycle is considered complete. Failures and remediation remain in the log rather than being rewritten away.**
