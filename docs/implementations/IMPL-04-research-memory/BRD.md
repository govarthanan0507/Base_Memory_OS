# IMPL-04 BRD — Research Memory

**Version:** 0.4

## Why this milestone exists

Important research arrives as websites, videos, repositories and documents. The Memory OS must preserve these sources as first-class artifacts so an idea can later be traced back to the evidence that informed it.

## Business/user problem

Research is currently easy to lose: a useful video may lead to a repository, a downloaded artifact, a conversation and eventually a project. URL-only bookmarks do not preserve that evolving provenance inside the work-memory system.

## Outcome

A vendor-independent research-source layer that canonicalizes external HTTP(S) URLs, conservatively classifies common source types, preserves provenance, deduplicates repeated registration, captures bounded evidence on request, exposes deterministic structural observations, and produces conservative semantic candidates that remain explicitly reviewable and traceable to the exact captured evidence.

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
- conservative candidate extraction for referenced repositories, tools, ideas and topics;
- evidence-bound candidate provenance and review status;
- tests and audit logging.

## Non-goals

- scraping arbitrary websites at scale;
- bypassing access controls;
- treating heuristic candidates as verified facts;
- automatic durable-memory admission from research text;
- semantic summarization by an LLM in this slice;
- claiming source content is verified merely because it was fetched;
- automatic project linkage from URLs alone.

## Success criteria

A source can be registered once, optionally captured as bounded text evidence, traced to a content hash and local snapshot, structurally inspected, and converted into conservative reviewable candidates. Every candidate must retain the exact source URL, snapshot hash and capture timestamp needed to trace it back to evidence. Candidate extraction must not imply verification or durable memory admission.
