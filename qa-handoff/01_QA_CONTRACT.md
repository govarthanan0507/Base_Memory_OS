# QA Contract — V2 E4 (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff.

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: belongs to the prior
`V0.1-FIX-01` cycle, already closed and merged — not this cycle's scope.

## Product

- **Name / version being tested:** base-memory-os — epic E4
  (Emotional/Behavioral Signal Extraction), V2's second epic. Ran in
  parallel with QA's review of PRs #11 (GUI shell) and #13 (E3) —
  this PR touches none of the same code as either.
- **Exact commit or build identifier:** `3fb102f` on branch
  `feature/e4-behavioral-signal` (open a PR before sending) into `main`.
- **Cycle type:** `FULL_AUDIT`.
- **If `FIX_VERIFICATION`:** N/A.

## Scope

- **In scope:**
  - `src/memory_os/emotional_signal.py` (new) —
    `extract_behavioral_signal`, `render_behavioral_signal`,
    `BehavioralSignal`.
  - `src/memory_os/cli.py` — one new command, `emotional-signal`.
  - `tests/test_emotional_signal.py` (new, 7 tests).
  - `projects/.../documents/E4_HARD_CONSTRAINTS_PRECHECK.md`,
    `E4_REQUIREMENTS.md` (Tier 2 design note — Backend-Architect +
    Data-Architect, no full debate; no disagreement to resolve).
- **Out of scope, and why:** no cross-conversation/per-project
  aggregation (explicitly E5's territory per `E4_REQUIREMENTS.md`'s
  non-goals). No new dependency, no new table — QA should confirm
  both via `git diff main...feature/e4-behavioral-signal --stat` and
  the module's own source (a test already greps for this, but
  independent confirmation is the point of QA existing).
- **Capabilities expected to apply:** functional correctness only —
  pure read path, no new write path.

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
      already-stored conversation text) and no new output surface
      beyond plain-text CLI output (no HTML/rich-text rendering here,
      unlike `gui.py`'s candidate cards — nothing analogous to F-06
      applies to this module).

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict; this handoff does not itself authorize release or merge.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
