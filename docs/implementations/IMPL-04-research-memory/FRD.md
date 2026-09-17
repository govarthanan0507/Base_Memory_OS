# IMPL-04 FRD — Research Memory

**Version:** 0.1

## Functional requirements

- FR-01 Normalize absolute HTTP(S) research URLs deterministically.
- FR-02 Remove URL fragments without discarding query parameters.
- FR-03 Classify common research sources conservatively as video, repository, document or website.
- FR-04 Register research sources as first-class artifacts.
- FR-05 Preserve canonical URL, source type, capture timestamp and provenance metadata.
- FR-06 Re-registering an equivalent canonical URL shall not create a second artifact.
- FR-07 Source registration shall not fetch, execute or modify external content.
- FR-08 Source classification shall remain an observation derived from URL structure, not a claim about content.

## Acceptance behavior

Equivalent URL forms such as differing scheme/host case, default HTTPS port, trailing slash and fragment normalize to the same canonical source where appropriate. Registering the source repeatedly returns the same stable artifact identity and leaves one artifact record.
