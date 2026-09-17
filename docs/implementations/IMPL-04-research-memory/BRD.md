# IMPL-04 BRD — Research Memory

**Version:** 0.1

## Why this milestone exists

Important research arrives as websites, videos, repositories and documents. The Memory OS must preserve these sources as first-class artifacts so an idea can later be traced back to the evidence that informed it.

## Business/user problem

Research is currently easy to lose: a useful video may lead to a repository, a downloaded artifact, a conversation and eventually a project. URL-only bookmarks do not preserve that evolving provenance inside the work-memory system.

## Outcome

A vendor-independent research-source layer that canonicalizes external URLs, classifies common source types conservatively, preserves provenance, and deduplicates repeated captures of the same canonical source.

## Scope

- canonical HTTP(S) URL normalization;
- research-source classification for common websites, videos, repositories and documents;
- first-class artifact registration;
- source provenance metadata;
- deterministic source identity;
- duplicate-safe repeated registration;
- tests and audit logging.

## Non-goals

- scraping arbitrary websites;
- bypassing access controls;
- claiming source content without actually ingesting it;
- automatic semantic conclusions about the research;
- automatic project linkage from URLs alone.

## Success criteria

Registering the same research source through equivalent URL forms produces one stable artifact, preserves canonical provenance, and records the source category without executing or modifying external content.
