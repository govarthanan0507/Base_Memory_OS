# QA Contract — V1 GUI shell (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff (CodeFoundry
`Developer_Organization`, acting on `base_memory_os`).

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: belongs to the prior
`V0.1-FIX-01` cycle, already closed and merged — not this cycle's scope.

## Product

- **Name / version being tested:** base-memory-os — the desktop GUI
  shell for the `personal-life-and-project-companion` project's V1
  (E1/E2 delivery mechanism, per `UI_TRD.md`). E1 and E2's backend
  (PRs #9, #10) are already merged to `main`; this cycle is the
  presentation layer calling that existing, already-audited logic —
  no new backend behavior beyond one small addition named below.
- **Exact commit or build identifier:** `9ac0787` on branch
  `feature/gui-shell`
  ([PR #11](https://github.com/govarthanan0507/Base_Memory_OS/pull/11)
  into `main`). Not yet merged.
- **Cycle type:** `FULL_AUDIT`.
- **If `FIX_VERIFICATION`:** N/A.

## Scope

- **In scope:**
  - `src/memory_os/gui.py` (new) — `ChatWindow`, `MessageBubble`,
    `CandidateCard`, `run_gui`. Two-pane layout (project sidebar +
    chat), native Qt widgets (no `QWebEngineView`, per `UI_DEBATE.md`'s
    reconvene addendum).
  - `src/memory_os/project_classification.py` — one addition,
    `list_candidate_details` (joins artifact/project names for
    display; read-only, does not touch review status).
  - `src/memory_os/cli.py` — new `gui` command, lazy-importing PySide6.
  - `pyproject.toml` — new optional `gui` extra (`PySide6-Essentials`,
    not the `PySide6` metapackage — see note below).
  - `.github/workflows/tests.yml` — installs the `gui` extra + system
    EGL/GL libs so GUI tests actually run in CI.
  - `tests/test_gui.py` (new, 11 tests).
- **Out of scope**: E1/E2's already-merged backend logic itself is not
  re-tested here — this cycle calls it, per the scope above, and does
  not modify its behavior. Voice dictation and a persistent per-project
  progress panel were both explicitly deferred by the human gate to a
  later cycle — neither exists in this PR; do not look for them.
- **A dependency-footprint note worth QA independently confirming**:
  `pip install base-memory-os[gui]` should NOT pull in
  `PySide6-Addons` (~175MB, QtWebEngine/Chromium) — only
  `PySide6-Essentials` + `shiboken6`. Verified directly this cycle
  (`pip show PySide6-Essentials` → `Requires: shiboken6` only); worth
  QA re-confirming via a clean-environment install, since this was the
  entire point of the native-widgets decision.

## Authorization boundaries

- **Destructive/intrusive testing authorized?** No — local SQLite/
  scratch filesystem only, same isolation the existing suite uses.
- **Product-modification mode authorized?** No.
- **Environment(s) authorized:** Local, matching
  `02_EXECUTION_PROTOCOL.md`. GUI tests require `QT_QPA_PLATFORM=offscreen`
  (no real display needed) and the system libraries named there
  (`libegl1`, `libgl1`, `libopengl0`) — without them, `import PySide6.QtWidgets`
  fails at the OS level (a real gap found this cycle, not a PySide6
  bug), before any test-level failure.
- **Data authorized for use:** Synthetic/local only. Same root-sandbox
  caveat as the prior E2 cycle applies to one pre-existing test
  (`test_unreadable_file_is_skipped_and_scan_continues`, unchanged
  this cycle) — unrelated to the GUI itself.

## Security boundary acknowledgement

- [x] Baseline-only, not a penetration test. One thing worth QA
      independently checking regardless: the GUI's markdown-to-HTML
      conversion (`gui._markdown_to_html`) HTML-escapes every text
      segment before any structural markup is applied — QA should try
      feeding a project/artifact name containing `<`, `&`, or `"` and
      confirm it renders as literal text, not interpreted markup.

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict; this handoff does not itself authorize release or merge.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-18
