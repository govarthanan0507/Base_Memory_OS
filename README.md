# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-04 — Research Memory v1.0 — provenance-preserving research registry**

IMPL-03 established read-only filesystem/project intelligence, artifact registration and history, project timelines, explicit project↔conversation continuity, deterministic nested-project boundaries, and an evidence-labelled project view.

IMPL-04 establishes a provider-neutral research-source boundary: canonical HTTP(S) URLs become deduplicated artifacts with provenance. Optional bounded capture creates SHA-256-addressed local evidence snapshots. URL metadata, structural observations and deterministic semantic candidates remain explicitly separated from verification.

The semantic layer identifies conservative candidates for referenced repositories, explicitly named tools, ideas and source topics. The research registry gives those candidates durable identity using `kind + normalized value`, while retaining every distinct source/snapshot/evidence occurrence separately. Candidates can be explicitly accepted or rejected without automatically creating general durable memory.

## Verification status

CI run #242 (`35187252449`) passed all unit-test matrix jobs on Python 3.11, 3.12, 3.13 and 3.14 for the evidence-preservation fix. The regression confirms identical evidence from distinct sources retains separate provenance trails.

Earlier failures remain recorded in the implementation log: run #200 exposed an invalid malformed-link fixture; run #211 exposed an uncaught `urljoin()` `ValueError`; run #223 exposed a test API mismatch; run #241 exposed the lower-level research-store evidence uniqueness bug. Each was corrected without removing the failure history.

## Status

- **IMPL-01 foundation:** implemented.
- **IMPL-02 conversation normalization:** implemented; runtime verification exercised through CI.
- **Conversation continuity:** implemented for conversation ↔ project ↔ artifact relationships and re-entry briefs.
- **Candidate extraction/review:** implemented with explicit review and provenance.
- **Project activity timeline:** implemented from project events, relationships and artifact evidence.
- **IMPL-03 project discovery:** implemented as a non-executing structural intelligence layer.
- **IMPL-03 state evidence:** tests, TODO/FIXME and recent activity signals implemented.
- **IMPL-03 root hardening:** strong-marker precedence, code-only discovery and nested project boundaries implemented.
- **IMPL-03 artifact history:** append-only discovery/change events implemented.
- **Canonical identity boundary:** provider-facing conversation external IDs resolve to stable internal conversation IDs before graph linking.
- **Compact project evidence:** snapshot/history/continuity/artifact view implemented with explicit evidence semantics.
- **IMPL-04 research identity:** URL normalization, source classification, deterministic artifact identity and duplicate-safe registration implemented.
- **IMPL-04 source capture:** bounded text capture, SHA-256 snapshots, local JSON evidence persistence and idempotent provenance attachment implemented.
- **IMPL-04 URL metadata:** provider-neutral YouTube/GitHub/GitLab identity hints implemented without network access.
- **IMPL-04 ingestion pipeline:** register → metadata → optional capture → snapshot → provenance implemented.
- **IMPL-04 structural evidence:** deterministic title/headings/link/URL observations implemented with malformed URL-resolution hardening.
- **IMPL-04 semantic candidates:** deterministic repository/tool/idea/topic candidates implemented with provenance, confidence, review status and local deduplication.
- **IMPL-04 persistent research registry:** cross-source candidate identity, separate evidence multiplicity, idempotent persistence and explicit accepted/rejected review implemented.
- **IMPL-04 evidence migration:** legacy research-evidence uniqueness is upgraded in place so older databases retain provenance while adopting source-aware uniqueness.
- **IMPL-04 provenance verification:** source → snapshot → observation → candidate → registry evidence chain is covered by offline tests and CI.

## Evidence boundary

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
RESEARCH ENTITY         ← deduplicated identity + evidence history
      ↓
DURABLE MEMORY / CLAIM  ← not automatic
      ↓
SOURCE VERIFIED         ← not implied
```

## Roadmap

IMPL-01 Memory Core → IMPL-02 Conversation Memory → IMPL-03 Project & File Intelligence → IMPL-04 Research Memory → IMPL-05 Re-entry → IMPL-06 Continuity OS

## Development rule

**README and the implementation log must be updated after every implementation iteration, before the next `go on` cycle is considered complete. Failures and remediation remain in the log rather than being rewritten away.**
