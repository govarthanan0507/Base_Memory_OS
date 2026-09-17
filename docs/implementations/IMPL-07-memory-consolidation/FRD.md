# IMPL-07 — Functional Requirements

## Version
v1.0

### FR-01 Candidate admission
Only candidates with explicit review status `accepted` may enter durable-memory consolidation.

### FR-02 Provenance
Every promoted memory must retain source candidate identity and available evidence provenance.

### FR-03 Duplicate handling
Equivalent durable memories must not create uncontrolled duplicates. The system must record the relationship to the existing memory.

### FR-04 Conflict handling
When a candidate conflicts with existing durable state, the system must preserve both historical evidence and the state transition. It must not silently overwrite the prior memory.

### FR-05 Supersession
A reviewed candidate may explicitly supersede an earlier memory while preserving the earlier memory as historical state.

### FR-06 Auditability
Consolidation operations must be deterministic, inspectable and repeat-safe.

### FR-07 Rejection safety
Rejected or unreviewed candidates must remain candidates and must not become durable memory.

### Acceptance
A complete test suite demonstrates admission, provenance, duplicate, conflict, supersession, rejection and idempotency behavior.
