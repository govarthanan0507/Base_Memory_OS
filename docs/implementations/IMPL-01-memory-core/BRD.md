# IMPL-01 BRD — Memory Core

**Version:** 0.1

## Why
The user needs a durable place to preserve work context instead of reconstructing it from scattered agents, files and projects.

## Business/user problem
Context is lost across sessions and tools. Reconstructing what happened is expensive and causes unfinished work to disappear.

## Outcome
Create a local source of truth capable of storing durable memories, projects, artifacts and relationships with provenance.

## Scope
SQLite persistence, durable memory records, projects, artifacts, relationships, timestamps, confidence, lexical retrieval, and read-only discovery foundations.

## Non-goals
LLM reasoning, automatic file organization, cloud sync, destructive filesystem operations, full conversation import, and UI.

## Success criteria
A fresh installation can initialize a database, store/retrieve a memory, register project/artifact records, and perform a read-only project scan without modifying source files.
