# IMPL-04 FRD — Research Memory

**Version:** 0.6

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
- FR-15 Extract provider-neutral identity hints from supported URL structures without network access.
- FR-16 Recognize YouTube watch/Shorts, `youtu.be`, GitHub and GitLab repository URL patterns.
- FR-17 Unknown URL patterns shall return only generic canonical URL/host hints rather than invented provider metadata.
- FR-18 Provide an explicit ingestion operation that composes source registration and URL metadata derivation.
- FR-19 When capture is requested, the ingestion operation shall require a snapshot destination, perform bounded capture, persist the snapshot, and attach its provenance.
- FR-20 The ingestion operation shall not perform network I/O when capture is disabled.
- FR-21 Extract deterministic structural observations from a captured snapshot without network access.
- FR-22 For HTML-like evidence, extract a page title, headings and hyperlinks; resolve relative links against the captured source URL.
- FR-23 Normalize and deduplicate observed links and headings while preserving first-observed order.
- FR-24 Structural observations shall carry the captured snapshot content hash and capture timestamp as provenance.
- FR-25 Structural extraction shall not infer semantic claims, verify source truth, or execute downloaded content.
- FR-26 Produce conservative, deterministic research candidates from preserved observations and snapshot text for repositories, tools, ideas and topics.
- FR-27 Every semantic candidate shall retain source URL, exact snapshot content hash, capture timestamp and candidate evidence text.
- FR-28 Semantic candidates shall be marked as reviewable candidates and shall not automatically become durable memories or verified claims.
- FR-29 Repeated identical repository references shall be deduplicated within one extraction result without losing provenance.
- FR-30 Semantic extraction shall perform no network I/O, LLM inference or downloaded-code execution.

## Acceptance behavior

Equivalent URL forms such as differing scheme/host case, default HTTPS port, trailing slash and fragment normalize to the same canonical source where appropriate. Registering the source repeatedly returns the same stable artifact identity and leaves one artifact record.

A captured text response is stored as a separate evidence snapshot identified by its content hash. The artifact records where that snapshot lives and when it was captured. Capture is explicitly an evidence operation; it does not claim that the source is correct, authoritative or semantically understood.

Provider metadata extraction must remain network-free and deterministic for the same canonical URL. Its output describes URL structure only.

The ingestion operation provides the complete deterministic-to-optional boundary in one call: source registration → URL metadata → optional network capture → local snapshot → artifact provenance. Capture errors must surface to the caller rather than being represented as successful ingestion.

Structural extraction operates only on already-captured evidence. Repeated identical content produces identical observations, and every observation result can be traced back to the snapshot hash. Malformed links are ignored rather than converted into invented source identities.

Semantic candidate extraction operates after structural evidence inspection. A repository candidate is grounded in an observed GitHub/GitLab URL; tool and idea candidates are produced only by explicit conservative textual patterns; title/headings become topic candidates rather than authoritative summaries. Candidates retain exact evidence provenance and a review status. They are not written to durable memory automatically.
