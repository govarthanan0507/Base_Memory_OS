# Execution Protocol — Windows Desktop Application Conversion

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/02_EXECUTION_PROTOCOL.md`'s
template, by the developer.

## Build / run instructions

- **Exact build command(s), Python package:** `pip install -e ".[gui]"`
  (setuptools, `src/` layout).
- **Exact build command(s), Windows packaged app:**
  1. On Windows: `pip install -e ".[gui]" && pip install pyinstaller`
  2. `pyinstaller packaging\BaseMemoryOS.spec --noconfirm` →
     `dist\BaseMemoryOS.exe`
  3. Install Inno Setup 6, then
     `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\installer.iss`
     → `dist\installer\BaseMemoryOS-Setup.exe`
  4. Or: download both from the `build-windows` GitHub Actions run's
     artifacts on this PR — same build, already run in CI.
- **Exact run command(s):**
  - Test suite: `PYTHONPATH=src python -m unittest discover -s tests -v`
    (matches `.github/workflows/tests.yml` exactly).
  - CLI (unchanged): `memory-os <command>`, or
    `python -m memory_os.cli <command>` from source.
  - Desktop app from source: `memory-os gui`, or
    `python packaging/launch_app.py`.
  - Packaged app: double-click `BaseMemoryOS.exe`, or run
    `BaseMemoryOS-Setup.exe` and launch from the Start Menu.
- **Required runtime/OS/versions:** Python 3.11-3.14 for the test
  suite (CI matrix, unchanged). The packaged `.exe` requires nothing
  beyond a 64-bit Windows machine — it bundles its own Python runtime
  and every dependency (PySide6 included).
- **Required environment variables / secrets (names only):** None.
- **Required external services and how they're mocked/stubbed for QA:**
  None — still fully local-first; the Settings dialog states this
  explicitly to the user.

## Known environment differences from production

- **This developer's environment is Linux, not Windows** — the real,
  material gap this cycle. PyInstaller does not cross-compile, so
  the `.exe`/installer were built and verified only on the
  `windows-latest` GitHub Actions runner, never on a physical Windows
  desktop. QA independently confirming the `build-windows` run
  succeeded, and ideally a hands-on run of the installer on a real
  Windows machine, is the actual gap-closing step for this cycle —
  named explicitly, not glossed over.
- **Scale/data volume difference:** N/A (single-user local SQLite),
  unchanged.
- **Configuration differences:** The packaged app's data directory
  (`%LOCALAPPDATA%\BaseMemoryOS`) differs from a from-source run's
  default (`~/.local/share/BaseMemoryOS` on Linux, or wherever
  `--db` points when passed explicitly) — this is intentional
  OS-appropriate behavior (`service.default_data_dir()`), not a bug,
  but QA should confirm both paths actually initialize correctly.

## Numeric targets for Stage 8 (Non-Functional/Scale)

No new numeric targets. Same framing as every prior cycle: single
local user, interactive in-process calls, no throughput/soak targets
apply to a desktop app like this.

## Observability

- **Logging:** unchanged (`logging_setup.py`) — the packaged app's
  `launch_app.py` calls `configure_logging` against the same
  app-data directory, so its log file lands at
  `%LOCALAPPDATA%\BaseMemoryOS\memory-os.log` on Windows.
- **Metrics / Tracing:** None — unchanged, out of scope.
