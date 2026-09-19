# QA Contract — Windows Desktop Application Conversion (personal-life-and-project-companion)

Filled per `QA_Organization/HANDOFF_PACKAGE_TEMPLATE/01_QA_CONTRACT.md`'s
template, by the developer side of this handoff.

**Note on `qa-handoff/FINDINGS_RESPONSE.md`**: belongs to the prior
`V0.1-FIX-01` cycle, already closed and merged — not this cycle's scope.

**Note on cycle timing**: per the product owner's explicit direction,
this cycle's QA review is deferred to next week rather than run
immediately — this handoff package is filled and ready, but the
`FULL_AUDIT` itself has not yet happened as of this commit.

## Product

- **Name / version being tested:** base-memory-os — Windows desktop
  application conversion (service layer + rebuilt GUI + PyInstaller/
  Inno Setup packaging), on top of the already-merged E1-E5.
- **Exact commit or build identifier:** `ce69c09` on branch
  `feature/windows-desktop-app` (open a PR before sending) into `main`.
- **Cycle type:** `FULL_AUDIT`.
- **If `FIX_VERIFICATION`:** N/A.

## Scope

- **In scope:**
  - `src/memory_os/service.py` (new) — the shared façade both
    `cli.py` and `gui.py` now call into.
  - `src/memory_os/cli.py` — refactored onto the service layer;
    printed output is unchanged, no command removed or added except
    default `--db` now resolving to an OS-appropriate app-data
    directory when not given explicitly.
  - `src/memory_os/gui.py` — rebuilt: onboarding, Projects/Memory/
    Search sidebar, Settings dialog, human-phrased candidate review,
    guarded exception handling.
  - `tests/test_service.py` (new, 10 tests), `tests/test_gui.py`
    (updated to route through the service layer, +6 new tests).
  - `packaging/` (PyInstaller spec, Inno Setup script, launcher
    script) and `.github/workflows/build-windows.yml`.
  - `projects/.../documents/WINDOWS_APP_REQUIREMENTS.md` (tiering
    determination and explicit non-goals).
- **Out of scope, and why:** no semantic/model-backed understanding
  anywhere (chat routing and search are unchanged underneath — see
  `WINDOWS_APP_REQUIREMENTS.md`'s non-goals). No animated scan-
  progress UI. No custom application icon. No hands-on verification
  of the installer on a real Windows desktop — this session has no
  Windows machine; QA should independently verify the
  `build-windows` GitHub Actions run on this PR actually succeeded
  and produced both artifacts, and ideally download and run
  `BaseMemoryOS-Setup.exe` on a real Windows machine if one is
  available, since this developer could not.
- **Capabilities expected to apply:** functional correctness
  (service layer, GUI, CLI unchanged behavior) plus a real build
  verification (does `build-windows` actually succeed on
  `windows-latest`, do both artifacts exist).

## Authorization boundaries

- **Destructive/intrusive testing authorized?** No — local SQLite
  only, same isolation pattern as every prior cycle.
- **Product-modification mode authorized?** No.
- **Environment(s) authorized:** Local (Linux/macOS, for the Python
  test suite) plus GitHub Actions `windows-latest` (for the packaging
  build) — a real Windows desktop is optional/best-effort for this
  cycle, not required.
- **Data authorized for use:** Synthetic/local only.

## Security boundary acknowledgement

- [x] Baseline-only, not a penetration test. One real, new surface
      worth naming: the packaged app's Settings dialog explicitly
      discloses "no AI model or external API is used today" — QA
      should confirm this claim is still true by grepping
      `src/memory_os/` for any outbound network call, same
      discipline as every prior cycle's security acknowledgement.

## Release authority

- **Name/role:** Product owner (govarbank@gmail.com) — QA reports a
  verdict; this handoff does not itself authorize release or merge.

## Sign-off

- **Authorized by:** CodeFoundry Developer_Organization (this cycle)
- **Date:** 2026-09-19
