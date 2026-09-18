# QA Contract — V1 E2 (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff (CodeFoundry
`Developer_Organization`, acting on `base_memory_os`).

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: that file belongs to the
prior `V0.1-FIX-01` cycle (F-01/F-02/F-03/F-04), already closed and
merged. It is not part of this cycle's scope.

## Product

- **Name / version being tested:** base-memory-os — new feature work
  for the `personal-life-and-project-companion` project's V1, epic E2
  (stories E2-1, E2-2, E2-3: file/code → project classification). E1
  (E1-1/E1-2) already merged to `main` in the prior cycle (PR #9).
- **Exact commit or build identifier:** `628713b` on branch
  `feature/e2-file-classification`
  ([PR #10](https://github.com/govarthanan0507/Base_Memory_OS/pull/10)
  into `main`). Not yet merged — this handoff targets the PR head, not
  `main`; QA should re-pull if the branch is updated before review.
- **Cycle type:** `FULL_AUDIT` (new functionality, not a fix-
  verification cycle).
- **If `FIX_VERIFICATION`:** N/A for this cycle.

## Scope

- **In scope (components/features):**
  - `src/memory_os/core.py` — new `artifact_project_candidates` table
    (additive-only migration), `ArtifactProjectCandidateRecord`
    dataclass, and three new `MemoryStore` methods:
    `add_artifact_project_candidate`, `list_artifact_project_candidates`,
    `review_artifact_project_candidate`.
  - `src/memory_os/project_classification.py` (new module) —
    `classify_artifacts_against_projects`: folder scan, artifact
    registration, and confidence-scored project-candidate proposal.
  - `src/memory_os/cli.py` — two new commands: `classify-folder`,
    `review-artifact-candidate`.
  - `tests/test_core.py` (+7), `tests/test_project_classification.py`
    (new, 7 tests).
- **Out of scope, and why:** every other module is untouched — QA
  should confirm via `git diff main...feature/e2-file-classification --stat`
  directly. No GUI code exists yet — these are backend/CLI functions
  only; the GUI shell (`UI_TRD.md`) is a separate, not-yet-built ticket
  (#7's GUI-wiring half remains backlog).
- **Capabilities expected to apply (starting hint, not binding):**
  functional correctness, data-integrity correctness, security
  (symlink-scope containment, no binary content reads, no network
  calls — see `E2_TRD.md`'s Security-Architect requirements).

## Authorization boundaries

- **Is destructive/intrusive testing authorized?** No. Local SQLite
  and scratch filesystem state only (`tempfile.TemporaryDirectory`,
  matching the existing test suite's isolation pattern).
- **Is any product-modification mode authorized for this cycle?** No.
- **Environment(s) authorized for testing:** Local, matching
  `02_EXECUTION_PROTOCOL.md`'s required runtime.
- **Data authorized for use:** Synthetic/local test data only —
  fabricated files/folders, no real user data. If QA's environment
  runs as root (or another user that bypasses file permission checks),
  one test (`test_unreadable_file_is_skipped_and_scan_continues`)
  self-skips rather than false-passing or false-failing — flagged
  explicitly, not hidden; QA should independently verify the
  permission-error path in an environment where it's actually
  enforceable if that matters for this cycle's verdict.

## Security boundary acknowledgement

- [x] I understand this cycle's security disposition will be
      baseline-only and does not constitute a penetration test or
      security audit. One real, in-scope security requirement for
      *this* cycle specifically (symlink-scope containment) is covered
      by a functional test (`test_symlink_escaping_scan_root_is_skipped_not_followed`),
      not deferred to a future security-organization pass.

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict per this cycle; this handoff does not itself authorize
  release or merge of PR #10.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
