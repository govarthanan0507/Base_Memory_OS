# QA Contract — V1 E1-1/E1-2 (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff (CodeFoundry
`Developer_Organization`, acting on `base_memory_os`).

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: that file belongs to the
prior `V0.1-FIX-01` cycle (F-01/F-02/F-03/F-04), already closed and
merged. It is not part of this cycle's scope — kept in place per this
project's "preserve history, don't overwrite" discipline, not
mistakenly carried forward as if it applied here.

## Product

- **Name / version being tested:** base-memory-os — new feature work
  for the `personal-life-and-project-companion` project's V1 (epic E1,
  stories E1-1 and E1-2). This is not a fix cycle on top of V0/V0.1;
  it is the first Development work on the new project's roadmap.
- **Exact commit or build identifier:** `7a0bc3ed95dee1878a7eb0e7d765a710b56feb2f`
  on branch `feature/e1-status-briefing-and-completion-signal`
  ([PR #9](https://github.com/govarthanan0507/Base_Memory_OS/pull/9)
  into `main`). Not yet merged — this handoff targets the PR head, not
  `main`; QA should re-pull if the branch is updated before review.
- **Cycle type:** `FULL_AUDIT` (new functionality, not a fix-
  verification cycle — no prior QA findings are being re-checked here).
- **If `FIX_VERIFICATION`:** N/A for this cycle.

## Scope

- **In scope (components/features):**
  - `src/memory_os/continuity.py` — three new functions:
    `find_project_by_name`, `submit_query`, `project_completion_signal`,
    plus the new "## Completion signal" section added to the existing
    `render_project_reentry_brief`.
  - `tests/test_continuity.py` — 8 new tests covering the above.
- **Out of scope, and why:** every other module in the repository is
  untouched by this PR — QA should confirm this via `git diff main...feature/e1-status-briefing-and-completion-signal --stat`
  directly rather than take it on trust, same discipline as the prior
  V0.1-FIX-01 cycle. No GUI code exists yet (E1-1's `submit_query` is
  the backend function the future GUI's bridge will call — see
  `projects/personal-life-and-project-companion/documents/UI_TRD.md` —
  the GUI shell itself is a separate, not-yet-built ticket).
- **Capabilities expected to apply (Stage 2 will confirm, this is a
  starting hint, not binding):** functional correctness, data-integrity
  correctness (SQLite queries, no writes on read-only query paths).

## Authorization boundaries

- **Is destructive/intrusive testing authorized?** No. Local SQLite
  state under a scratch/test directory only — matches how the existing
  test suite already isolates state (`tempfile.TemporaryDirectory`).
- **Is any product-modification mode authorized for this cycle?** No.
- **Environment(s) authorized for testing:** Local, any environment
  matching `02_EXECUTION_PROTOCOL.md`'s required runtime. No production
  or shared environment involved.
- **Data authorized for use:** Synthetic/local test data only —
  fabricated project/artifact/candidate records, no real user data.

## Security boundary acknowledgement

- [x] I understand this cycle's security disposition will be
      baseline-only and does not constitute a penetration test or
      security audit.

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict per this cycle; this handoff does not itself authorize
  release or merge of PR #9.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
