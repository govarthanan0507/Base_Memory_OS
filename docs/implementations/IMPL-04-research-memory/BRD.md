# IMPL-04 BRD — Research Memory

**Version:** 0.2

## Why this milestone exists

Important research arrives as websites, videos, repositories and documents. The Memory OS must preserve these sources as first-class artifacts so an idea can later be traced back to the evidence that informed it.

## Business/user problem

Research is currently easy to lose: a useful video may lead to a repository, a downloaded artifact, a conversation and eventually a project. URL-only bookmarks do not preserve that evolving provenance inside the work-memory system.

## Outcome

A vendor-independent research-source layer that canonicalizes external URLs, classifies common source types conservatively, preserves provenance, deduplicates repeated registration, and can optionally capture bounded text evidence without silently treating capture as interpretation or verification.

## Scope

- canonical HTTP(S) URL normalization;
- research-source classification for common websites, videos, repositories and documents;
- first-class artifact registration;
- source provenance metadata;
- deterministic source identity;
- duplicate-safe repeated registration;
- optional bounded text capture;
- content hashing and local snapshot persistence;
- snapshot provenance attached to the source artifact;
- tests and audit logging.

## Non-goals

- scraping arbitrary websites at scale;
- bypassing access controls;
- semantic summarization;
- claiming source content is verified merely because it was fetched;
- automatic project linkage from URLs alone.

## Success criteria

A source can be registered once, optionally captured as bounded text evidence, and later traced to a content hash and local snapshot with capture metadata. Capture failures or unsupported content must not be represented as successful understanding.
