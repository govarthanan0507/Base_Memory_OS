# Execution Protocol — V1 GUI shell

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/02_EXECUTION_PROTOCOL.md`'s
template, by the developer. Re-confirmed against
`.github/workflows/tests.yml` and `pyproject.toml` for this cycle, not
copied blind — this is the first cycle with a real environment
dependency beyond pure Python.

## Build / run instructions

- **Exact build command(s):**
  - Base CLI (unchanged): `pip install -e .` — still zero required
    dependencies.
  - GUI (new this cycle): `pip install -e ".[gui]"` — installs
    `PySide6-Essentials` (not the `PySide6` metapackage; see
    `01_QA_CONTRACT.md`'s dependency-footprint note).
- **Exact run command(s):**
  - Test suite: `PYTHONPATH=src python -m unittest discover -s tests -v`
    (matches `.github/workflows/tests.yml` exactly).
  - CLI: `memory-os <command>` once installed, or
    `python -m memory_os.cli <command>` from source.
  - GUI: `memory-os gui` (requires the `gui` extra installed; a clean
    `ValueError` with the install instructions if it isn't).
- **Required runtime/OS/versions:** Python 3.11, 3.12, 3.13, or 3.14.
  The GUI's target platform is Windows (per `UI_HARD_CONSTRAINTS_PRECHECK.md`'s
  Category 12), but development/CI runs on Linux — `PySide6-Essentials`
  is cross-platform, no Windows-specific code exists yet.
- **New this cycle — system-level requirement for the `gui` extra**:
  on Linux, `PySide6.QtWidgets` fails to import at all
  (`ImportError: libEGL.so.1: cannot open shared object file`) without
  `libegl1`/`libgl1`/`libopengl0` installed at the OS level — a real
  gap found and fixed in `.github/workflows/tests.yml` this cycle, not
  a PySide6 bug. QA's environment needs these too, or GUI tests will
  fail at import time rather than at a test assertion. Not expected to
  be an issue on the actual Windows target (EGL/OpenGL ship with
  standard graphics drivers there) — flagged as a Linux dev/CI/QA
  environment note, not a product requirement.
- **Headless testing**: `QT_QPA_PLATFORM=offscreen` (set in CI, must
  be set manually if QA runs tests directly) lets Qt run with no real
  display — no `Xvfb` needed for the test suite itself, though `Xvfb`/
  `xvfb-run` are also available in this dev environment if QA wants an
  actual rendered screenshot for visual verification (this is how the
  developer side verified the redesign — see PR #11's description for
  the before/after screenshots referenced there).
- **Required environment variables / secrets:** None beyond
  `QT_QPA_PLATFORM=offscreen` for headless test runs. No network
  calls, no external service credentials — fully local-first,
  unchanged.
- **Required external services:** None.

## Known environment differences from production

There is no separate "production" environment — this is a local CLI
tool installed and run directly on the user's own machine. No
environment-parity gap exists to document.

- **Scale/data volume difference:** N/A (single-user local SQLite).
- **Infrastructure topology difference:** N/A (single process, single
  local DB file).
- **Configuration differences:** None — same code path runs identically
  in CI, QA's environment, and end-user installs.
- **Third-party service differences:** N/A — no third-party services.

## Numeric targets for Stage 8 (Non-Functional/Scale)

No new numeric targets this cycle — the GUI is a thin presentation
layer over already-scoped backend calls. One new, real note: the
project sidebar calls `store.list_projects(limit=200)` on every
window open — not evaluated past 200 projects, same ceiling
`continuity.find_project_by_name` already carries.

- **Expected peak concurrency:** Single local user, single process —
  not applicable in the multi-user sense.
- **Target latency (p50/p95/p99):** Not formally targeted — these are
  interactive, in-process function calls (sub-second expected).
- **Target throughput:** Not applicable (interactive local CLI, not a
  service).
- **Target error rate ceiling:** N/A for this cycle's scope.
- **Soak duration:** Not applicable.

## Observability

For Stage 9 — what instrumentation exists today, and where:

- **Logging:** New as of this fix cycle (F-02) —
  `src/memory_os/logging_setup.py`. File handler on the true root
  logger, writing to `.memory-os/memory-os.log` (created beside the
  SQLite db path passed to the CLI). INFO level by default; `--verbose`
  flag raises to DEBUG and mirrors to stderr. Every write-path command
  (init, add-memory, scan-projects, import-conversation,
  import-chatgpt-export, relate, link-project-conversation,
  extract-candidates, review-candidate, project-evidence) logs an INFO
  entry. Caught errors log WARNING with `exc_info=True`; genuinely
  unexpected exceptions log via `logger.exception` before re-raising.
- **Metrics:** None — out of scope for this local-first CLI tool.
- **Tracing:** None — out of scope for this local-first CLI tool.
