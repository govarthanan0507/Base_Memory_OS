# QA Contract — V3 E5 (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff.

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: belongs to the prior
`V0.1-FIX-01` cycle, already closed and merged — not this cycle's scope.

## Product

- **Name / version being tested:** base-memory-os — epic E5
  (Proactive Focus Guidance), V3's only epic. Ran while QA's review
  of PR #15 (E4) was still open — this PR touches none of the same
  code as E4 and has no dependency on it (E5's own hard dependency,
  per `EPIC_SELECTION.md`, is on E1 and E3, both already merged into
  `main`).
- **Exact commit or build identifier:** `94b3eee` on branch
  `feature/e5-proactive-focus-guidance` (open a PR before sending)
  into `main`.
- **Cycle type:** `FULL_AUDIT`.
- **If `FIX_VERIFICATION`:** N/A.

## Scope

- **In scope:**
  - `src/memory_os/focus_guidance.py` (new) — `detect_idea_hopping`,
    `cross_project_completion`, `render_focus_guidance`,
    `IdeaHopSignal`.
  - `src/memory_os/cli.py` — one new command, `focus-guidance
    [--window] [--limit]`.
  - `tests/test_focus_guidance.py` (new, 8 tests).
  - `projects/.../documents/E5_HARD_CONSTRAINTS_PRECHECK.md`,
    `E5_REQUIREMENTS.md` (Tier 2 design note — Backend-Architect +
    Data-Architect, no full debate; no disagreement to resolve).
- **Out of scope, and why:** no unprompted/background notification
  mechanism — explicitly resolved as out of scope in
  `E5_HARD_CONSTRAINTS_PRECHECK.md`'s Category 7 resolution (this is
  an on-demand CLI report only). No absolute time-to-finish estimate
  — `E5_REQUIREMENTS.md`'s non-goals name this directly. No use of
  embeddings/a model for hop detection — see
  `projects/.../documents/SEMANTIC_RETRIEVAL_DECISION.md`, a separate
  product-owner decision superseding an earlier feasibility
  assumption; not this PR's own scope to revisit.
- **Capabilities expected to apply:** functional correctness only —
  pure read path, no new write path, no new table.

## Authorization boundaries

- **Destructive/intrusive testing authorized?** No — local SQLite
  only, same isolation pattern as every prior cycle.
- **Product-modification mode authorized?** No.
- **Environment(s) authorized:** Local, matching
  `02_EXECUTION_PROTOCOL.md` (unchanged — no new runtime requirement).
- **Data authorized for use:** Synthetic/local only.

## Security boundary acknowledgement

- [x] Baseline-only, not a penetration test. Nothing new to flag —
      this feature adds no new input surface (it reads
      already-stored `project_events`/`projects` rows) and no new
      output surface beyond plain-text CLI output.

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict; this handoff does not itself authorize release or merge.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
