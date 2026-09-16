# Base Memory OS

A local-first, vendor-independent personal work memory system.

## Current milestone

**IMPL-01 — Memory Core v0.1**

The first implementation establishes a small, dependency-light memory core with SQLite persistence, provenance, temporal state, projects, artifacts, relationships, lexical retrieval, and read-only filesystem/project discovery.

The system is provider-neutral. Model runtimes such as Ollama are adapters, not the memory core itself.

## Design principles

1. Preserve raw evidence and provenance.
2. Prefer observed facts over unsupported inference.
3. Never move or delete user files during discovery.
4. Keep project understanding separate from physical filesystem organization.
5. Preserve temporal history rather than silently overwriting it.
6. Keep external model providers replaceable.
7. Build in small, testable increments.

## Repository map

```text
src/memory_os/
  core/          domain models and SQLite persistence
  discovery/     read-only filesystem/project intelligence
  cli.py         command-line interface

docs/
  governance/    project rules and roadmap
  implementations/IMPL-01-memory-core/
                 BRD / FRD / PRD / TRD + implementation log

tests/           automated tests
```

## Status

This is an actively evolving personal system. IMPL-01 is the foundation, not the finished Personal Memory OS.

Next milestones: conversation ingestion, richer artifact/project intelligence, research-memory integration, re-entry briefings, and cross-agent continuity.
