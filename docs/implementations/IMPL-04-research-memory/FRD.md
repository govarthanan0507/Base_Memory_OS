# IMPL-04 FRD — Research Memory

**Version:** 0.9

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
- FR-19 When capture is requested, ingestion shall require a snapshot destination, perform bounded capture, persist the snapshot, and attach provenance.
- FR-20 Ingestion shall not perform network I/O when capture is disabled.
- FR-21 Extract deterministic structural observations from a captured snapshot without network access.
- FR-22 For HTML-like evidence, extract a page title, headings and hyperlinks; resolve relative links against the captured source URL.
- FR-23 Normalize and deduplicate observed links and headings while preserving first-observed order.
- FR-24 Structural observations shall carry the captured snapshot content hash and capture timestamp as provenance.
- FR-25 Structural extraction shall not infer semantic claims, verify source truth, or execute downloaded content.
- FR-26 Produce conservative, deterministic research candidates from preserved observations and snapshot text for repositories, tools, ideas and topics.
- FR-27 Every semantic candidate shall retain source URL, exact snapshot content hash, capture timestamp and candidate evidence text.
- FR-28 Semantic candidates shall be marked reviewable and shall not automatically become durable memories or verified claims.
- FR-29 Repeated identical repository references shall be deduplicated within one extraction result without losing provenance.
- FR-30 Semantic extraction shall perform no network I/O, LLM inference or downloaded-code execution.
- FR-31 The complete provenance chain shall be testable from source registration through snapshot attachment, structural observations and semantic candidates.
- FR-32 Provenance-chain tests shall use platform-independent temporary storage.
- FR-33 Persisted research candidate identity shall be deterministic from candidate kind and normalized value.
- FR-34 Repeated candidates across different source snapshots shall converge on one research entity.
- FR-35 Each distinct candidate/source-snapshot/evidence occurrence shall remain separately queryable as evidence.
- FR-36 Re-persisting the same candidate evidence shall be idempotent.
- FR-37 Candidate review shall support candidate → accepted/rejected without automatically creating durable memory.

## Acceptance behavior

Equivalent URL forms normalize to the same canonical source where appropriate. Registering a source repeatedly returns the same stable artifact identity and leaves one artifact record.

A captured response is stored as separate evidence identified by content hash. The artifact records its location and capture time. Capture does not claim correctness, authority or semantic understanding.

Provider metadata extraction remains network-free and deterministic. Its output describes URL structure only.

Structural extraction operates only on preserved evidence. Repeated identical content produces identical observations; malformed links are ignored rather than converted into invented identities.

Semantic extraction is conservative and provenance-bound. Repository candidates require observed GitHub/GitLab URLs; tool and idea candidates require explicit textual patterns; title/headings become topic candidates. No candidate is automatically treated as verified.

Persistent storage uses kind + normalized value as the entity identity. Distinct source/snapshot/evidence occurrences remain separate. Re-persistence is idempotent. Review changes only the research entity status and does not create a general durable-memory record.
