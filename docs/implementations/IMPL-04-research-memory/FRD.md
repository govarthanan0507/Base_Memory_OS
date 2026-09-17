# IMPL-04 FRD — Research Memory

**Version:** 0.2

## Functional requirements

- FR-01 Normalize absolute HTTP(S) research URLs deterministically.
- FR-02 Remove URL fragments without discarding query parameters.
- FR-03 Classify common research sources conservatively as video, repository, document or website.
- FR-04 Register research sources as first-class artifacts.
- FR-05 Preserve canonical URL, source type, capture timestamp and provenance metadata.
- FR-06 Re-registering an equivalent canonical URL shall not create a second artifact.
- FR-07 Source registration shall not fetch, execute or modify external content.
- FR-08 Source classification shall remain an observation derived from URL structure, not a claim about content.
- FR-09 Optionally capture bounded text responses from a canonical HTTP(S) URL.
- FR-10 Reject captures that exceed the configured byte bound or cannot be decoded as text.
- FR-11 Compute a deterministic SHA-256 content hash for every captured text snapshot.
- FR-12 Persist snapshots separately from the source artifact and attach snapshot provenance to the artifact.
- FR-13 Re-attaching the same snapshot metadata shall be idempotent.
- FR-14 Snapshot capture shall record capture time, content type and HTTP status when available.

## Acceptance behavior

Equivalent URL forms such as differing scheme/host case, default HTTPS port, trailing slash and fragment normalize to the same canonical source where appropriate. Registering the source repeatedly returns the same stable artifact identity and leaves one artifact record.

A captured text response is stored as a separate evidence snapshot identified by its content hash. The artifact records where that snapshot lives and when it was captured. Capture is explicitly an evidence operation; it does not claim that the source is correct, authoritative or semantically understood.
