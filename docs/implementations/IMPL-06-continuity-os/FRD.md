# IMPL-06 — Continuity OS FRD v0.1

## Functional requirements

1. `continuity_snapshot()` shall return one compact record per known project.
2. Each record shall include project identity, status and root.
3. Each record shall include the latest linked conversation when available.
4. Each record shall include unresolved candidate and artifact counts.
5. `render_continuity_dashboard()` shall render the snapshot deterministically.
6. The dashboard shall explicitly report an empty project set.
7. The operation shall be read-only.

## Acceptance

The full test suite remains green and the CLI exposes `memory-os dashboard`.
