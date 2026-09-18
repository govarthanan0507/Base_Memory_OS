# QA Contract — V2 E3 (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff.

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: belongs to the prior
`V0.1-FIX-01` cycle, already closed and merged — not this cycle's scope.

## Product

- **Name / version being tested:** base-memory-os — epic E3 (Idea
  Relationship Tracking), the first V2 epic. Ran in parallel with
  QA's own review of PR #11 (the V1 GUI shell) — this PR does not
  depend on #11 and touches none of the same code.
- **Exact commit or build identifier:** `8194ffb` on branch
  `feature/e3-idea-relationships`
  ([PR — open one before sending]) into `main`.
- **Cycle type:** `FULL_AUDIT`.
- **If `FIX_VERIFICATION`:** N/A.

## Scope

- **In scope:**
  - `src/memory_os/continuity.py` — `_linked_entities` now tags
    direction (outgoing/incoming); new `_describe_relation` helper;
    `project_context` exposes `related_ideas`;
    `render_project_reentry_brief` adds a "## Related ideas" section.
  - `tests/test_continuity.py` (+6 tests).
  - `projects/.../documents/E3_REQUIREMENTS.md` (new — the Tier 1
    determination and requirement; no Design Council package exists
    for this epic, by design — see that file's own reasoning).
- **Out of scope, and why:** no schema change, no new CLI command (the
  existing `relate` command already covers creating the relation — QA
  should confirm no new command was added rather than assume it). No
  GUI wiring — E3_REQUIREMENTS.md explicitly defers that.
- **Capabilities expected to apply:** functional correctness only —
  this is a pure read-path/display addition, no new write path beyond
  what `relate()` already did.

## Authorization boundaries

- **Destructive/intrusive testing authorized?** No — local SQLite
  only, same isolation pattern as every prior cycle.
- **Product-modification mode authorized?** No.
- **Environment(s) authorized:** Local, matching
  `02_EXECUTION_PROTOCOL.md` (unchanged from prior cycles — no new
  runtime requirement).
- **Data authorized for use:** Synthetic/local only.

## Security boundary acknowledgement

- [x] Baseline-only, not a penetration test. Nothing new to flag —
      this epic adds no new input surface beyond the existing
      `relate` command's own (relation is an arbitrary string, already
      true before this change; this cycle only adds *display* logic
      for whatever string is already there).

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict; this handoff does not itself authorize release or merge.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
