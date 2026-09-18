# Execution Protocol — V1 E2

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/02_EXECUTION_PROTOCOL.md`'s
template, by the developer. Build/run/environment facts below are
unchanged from the prior cycles (this PR adds one new module,
`project_classification.py`, plus a new table — no new third-party
dependency, no runtime change, per `E2_HARD_CONSTRAINTS_PRECHECK.md`'s
resolution of Hard Constraint #9) and are re-confirmed against
`.github/workflows/tests.yml` and `pyproject.toml` for this cycle, not
copied blind.

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

This cycle adds a write path (`classify_artifacts_against_projects`
registers an artifact and scores it against every existing project
per scanned file). No new numeric targets are introduced beyond what
prior cycles already set, but two real, cycle-specific scale notes:

- `classify_artifacts_against_projects`'s per-file cost scales with
  the number of existing projects (it re-tokenizes every project's
  linked-artifact names per file scanned, per project) — not
  evaluated against a large project count or a large folder; flagged
  as a scale ceiling, not measured as a hard limit.
- Content-snippet reads are capped at `MAX_HASH_BYTES` (reused from
  `discovery.py`), consistent with the E2_TRD.md's Security-Architect
  requirement against unbounded reads.

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
