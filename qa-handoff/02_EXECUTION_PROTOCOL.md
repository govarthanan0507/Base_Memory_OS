# Execution Protocol — V2 E4

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/02_EXECUTION_PROTOCOL.md`'s
template, by the developer. Unchanged from every prior cycle — E4
adds one new pure-Python module with zero new dependency
(`E4_HARD_CONSTRAINTS_PRECHECK.md`'s resolution) and no schema
change. This branch was also cut before PR #11 (GUI shell) merged, so
it carries no `gui` extra — a separate PR's concern, not missing.

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
  None. This tool has zero external service dependency by design (see
  README's "local-first, vendor-independent" framing).

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
`extract_behavioral_signal`'s cost scales with a conversation's total
message text length (the lexicon match is a linear scan) — not
evaluated against an unusually large conversation; flagged as a
scale ceiling, not measured as a hard limit.

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
