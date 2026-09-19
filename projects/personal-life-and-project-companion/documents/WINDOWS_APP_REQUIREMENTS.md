# Requirements — Windows desktop application conversion

Produced by: Product Owner, from a fully-specified request the
product owner (govarbank@gmail.com) supplied directly — CLI to
Windows-application conversion, not a new capability.

## Tiering determination

**Tier 3 — new architecture pattern, full pass, but no Council debate
theater given the requester already specified the design in detail.**
Triggers: a new architectural pattern not already established (a
dedicated service layer between GUI/CLI and core; a packaged-binary
distribution pipeline via PyInstaller + Inno Setup) and a new
third-party build-time dependency (PyInstaller, Inno Setup — build
tooling only, never shipped as a runtime dependency of the product
itself). Per the product owner's explicit direction to stop spending
on process overhead this cycle, the Tier 3 architectural questions
were resolved directly against the requester's own detailed spec
rather than run through the full 7-role debate — recorded here as a
deliberate scope trade-off, not a silently skipped step.

## What this delivers

1. A `service.py` façade — every operation the CLI or GUI needs, in
   one place. Neither talks to `core.py`/`continuity.py`/etc.
   directly any more (`GUI -> service layer -> core`, never
   `GUI -> subprocess -> CLI`, per the explicit architectural
   constraint in the request).
2. `cli.py` refactored to call the service layer, with identical
   printed output — no CLI behavior change, no command removed.
3. `gui.py` rebuilt: onboarding (once, `QSettings`-tracked), a
   Projects/Memory/Search sidebar, a Settings dialog (data location,
   AI-processing disclosure, developer mode), human-phrased candidate
   review ("Remember"/"Ignore", no raw IDs unless Developer Mode is
   on), and a guarded-exception wrapper so no action handler can
   surface a raw traceback to a normal user.
4. Auto-init: `MemoryOSService()`'s own constructor creates the
   database/schema in an OS-appropriate app-data directory
   (`%LOCALAPPDATA%\BaseMemoryOS` on Windows) if it doesn't exist —
   no manual `memory-os init` step for a packaged app's user.
5. Packaging: a PyInstaller spec producing a windowed
   `BaseMemoryOS.exe` (no console window, bundles its own Python
   runtime), an Inno Setup script producing
   `BaseMemoryOS-Setup.exe` (Start Menu entry, Desktop shortcut,
   uninstall entry), and a `windows-latest` GitHub Actions workflow
   that actually builds both and uploads them as CI artifacts — the
   verification mechanism, since PyInstaller cannot cross-compile a
   Windows binary from this session's Linux sandbox.

## Non-goals (explicitly, not smoothed over)

- Does not add semantic/model-backed understanding anywhere — chat
  routing (`service.ask`) is the same name-matching `submit_query`
  logic as before, and Search is still the existing FTS/keyword
  `search`. The Memory screen shows each stored memory's *actual*
  recorded type, not an invented Preferences/Decisions/Goals
  categorization this product does not compute — per the request's
  own explicit constraint not to overclaim semantic capability while
  doing this conversion.
- Does not attempt an animated multi-step scan progress UI (the
  request's mockup for folder scanning) — the existing single-action
  scan-then-summarize flow is kept; a richer progress indicator is a
  cosmetic follow-up, not an architectural requirement.
- Does not report fabricated import-summary numbers ("N project
  signals detected," "N candidates detected") that the current
  `import_chatgpt_export` return value doesn't actually provide —
  only the real, computed conversation count is shown. Inventing the
  other numbers would repeat exactly the kind of unverified-claim
  mistake this project has already been burned by once this session.
- Does not include a custom application icon — `BaseMemoryOS.exe`
  currently uses PyInstaller's default; a real `.ico` asset is a
  follow-up, not fabricated here without a real design asset to use.
- Does not verify the installer's actual double-click experience on a
  real Windows desktop — this session has no Windows machine. CI on
  `windows-latest` verifies the .exe and installer *build*
  successfully; a hands-on check by the product owner on their own
  machine is still required and is named as an open item, not
  claimed as done.
