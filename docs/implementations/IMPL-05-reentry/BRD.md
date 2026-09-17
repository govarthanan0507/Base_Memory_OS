# IMPL-05 — Re-entry BRD v0.1

## Purpose

Restore a user's working context after an interruption without inventing history.

## Problem

Existing memory can contain conversations, projects, artifacts, events and candidates, but the user still needs a compact answer to “where did I leave this?”

## Business/user outcome

A project re-entry view should reconstruct the latest known working state from stored evidence and expose unresolved candidate threads for manual continuation.

## Scope

- project-centric re-entry
- latest linked conversation
- recent project activity
- open reviewable candidates explicitly tagged to the project
- linked artifacts and durable memories
- evidence-labelled output

## Boundaries

Re-entry must not claim that an inferred next step is fact. It must not silently modify memory or project state.

## Success criteria

A user can open a project and see its latest known conversation, recent recorded activity, unresolved candidate threads, artifacts and linked memories in one deterministic brief.
