# Execution Protocol — V3 E5

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/02_EXECUTION_PROTOCOL.md`'s
template, by the developer. Unchanged from every prior cycle — E5
adds one new pure-Python module with zero new dependency and no
schema change. This branch was cut from `main` after E1/E3/GUI-shell
all merged, so it carries the `gui` extra already — no gap there.

## Build / run instructions

- **Exact build command(s):** `pip install -e .` (setuptools, `src/`
  layout, no compiled/native dependencies — pure Python, zero runtime
  dependencies per `pyproject.toml`).
- **Exact run command(s):**
  - Test suite: `PYTHONPATH=src python -m unittest discover -s tests -v`
    (matches `.github/workflows/tests.yml` exactly — same command CI runs).
  - CLI: `memory-os <command>` once installed, or
    `python -m memory_os.cli <command>` from source.
- **Required runtime/OS/versions:** Python 3.11, 3.12, 3.13, or 3.14
  (CI matrix runs all four). No OS-specific dependency — pure Python,
  local SQLite only.
- **Required environment variables / secrets (names only):** None. No
  network calls, no external service credentials — fully local-first.
- **Required external services and how they're mocked/stubbed for QA:**
  None.

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

No new numeric targets this cycle. One real, cycle-specific note:
`detect_idea_hopping`'s `window` parameter bounds its own cost (a
single `ORDER BY timestamp DESC LIMIT window` query plus a linear
scan of that window) — not evaluated against an unusually large
`project_events` table; flagged as a scale ceiling, not measured as a
hard limit, same framing as E4's own note on `extract_behavioral_signal`.

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

- **Logging:** `src/memory_os/logging_setup.py` (unchanged this
  cycle) — file handler on the true root logger, writing to
  `.memory-os/memory-os.log`. `focus-guidance` logs an INFO entry on
  invocation (window/limit), matching every other command in
  `_dispatch`.
- **Metrics:** None — out of scope for this local-first CLI tool.
- **Tracing:** None — out of scope for this local-first CLI tool.
