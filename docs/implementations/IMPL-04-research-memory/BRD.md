# IMPL-04 BRD — Research Memory

**Version:** 0.3

## Why this milestone exists

Important research arrives as websites, videos, repositories and documents. The Memory OS must preserve these sources as first-class artifacts so an idea can later be traced back to the evidence that informed it.

## Business/user problem

Research is currently easy to lose: a useful video may lead to a repository, a downloaded artifact, a conversation and eventually a project. URL-only bookmarks do not preserve that evolving provenance inside the work-memory system.

## Outcome

A vendor-independent research-source layer that canonicalizes external URLs, classifies common source types conservatively, preserves provenance, deduplicates repeated registration, captures bounded evidence on request, and exposes deterministic structural observations from captured evidence before any semantic model is invoked.

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
- deterministic extraction of titles, headings and links from captured HTML/text evidence;
- tests and audit logging.

## Non-goals

- scraping arbitrary websites at scale;
- bypassing access controls;
- semantic summarization or LLM-generated conclusions;
- claiming source content is verified merely because it was fetched;
- automatic project linkage from URLs alone.

## Success criteria

A source can be registered once, optionally captured as bounded text evidence, traced to a content hash and local snapshot, and structurally inspected for reproducible observations. Structural observations must retain their source snapshot provenance and must not be represented as verified semantic claims.
