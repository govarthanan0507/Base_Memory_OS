# IMPL-06 — Continuity OS BRD v0.1

## Purpose

Provide one compact entry point into the user's known project continuity state.

## Outcome

The system can summarize each known project with status, latest linked conversation, unresolved candidate count and artifact count without changing stored data.

## Scope

- read-only continuity snapshot
- deterministic dashboard rendering
- CLI access
- explicit empty-state behavior

## Boundary

The dashboard reports stored evidence. It does not decide which project the user should work on or invent priorities.
