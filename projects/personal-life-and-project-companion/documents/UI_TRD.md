# Technical Requirements — Desktop GUI (chat-style, cross-cutting: E1 + E2 delivery)

Per `UI_DEBATE.md`'s synthesis, **as revised by its "Reconvene —
`QWebEngineView` vs. native Qt widgets" addendum**. This does not
replace E1/E2's `FRD.md`/`TRD.md` functional behavior or data model —
it defines the new presentation layer calling the same, already-
designed logic.

**Revision note**: the original version of this file specified
`QWebEngineView` + `QWebChannel`. That was revised after
`REPO_CANDIDATES.md`'s UI-shell research found real open-source
precedent (two verified PySide6 chat GUIs) went the other way — native
Qt widgets, no Chromium. See `UI_DEBATE.md`'s reconvene addendum for
the full reasoning; this file reflects the current decision only, the
original reasoning is preserved there, not deleted.

## Architecture overview and decisions

```text
PySide6 native window (Windows target) — PySide6 only, no
PySide6-Addons/QtWebEngine
  └── QScrollArea, vertical layout of message widgets:
        - QLabel (textFormat=Qt.RichText) for assistant/user text
          bubbles — Qt's native rich-text subset (bold, lists,
          headers, basic styling) covers everything this content
          needs, no HTML/JS engine required.
        - QFrame (label + two QPushButton) for a candidate card —
          Accept/Reject wired directly to Qt signals.
  └── QLineEdit + send QPushButton, at the bottom, for typed queries
        and folder paths.
  └── Python side: existing MemoryStore / discovery.py / continuity.py
        (unchanged — called directly from Qt signal handlers instead
         of cli.py's dispatch; cli.py itself is kept, not removed)
```

**Rejected alternative**: `QWebEngineView` + `QWebChannel` (the
original decision). Rejected on reconvene — no verified open-source
precedent for this app's actual shape uses it; Qt's native rich-text
support already covers this project's real formatting needs; dropping
it also removes the `PySide6-Addons` Chromium payload and the whole
class of "Chromium fails to initialize" failure the original design
had to build a fallback for.

**Rejected alternative**: a full local web server + browser tab.
Rejected — the user asked for a desktop GUI specifically (confirmed at
the human gate); a browser tab is a different interface class, and a
local server introduces a listening process this design has no reason
to need.

## The three functions — unchanged in name and behavior, different calling convention

No `QWebChannel` bridge exists in the revised design — there's no
embedded web content to bridge to. These are direct Python methods,
wired to Qt widget signals (a button's `clicked`, a line edit's
`returnPressed`):

```text
submit_query(text: str) -> str
    Routes a typed status question to continuity.py's existing
    render_project_reentry_brief/project_context (via
    continuity.submit_query, already implemented — E1-1). Returns the
    answer as a rich-text string for a QLabel bubble.

start_scan(folder_path: str) -> list[dict]
    Calls project_classification.classify_artifacts_against_projects
    (already implemented — E2-1/E2-2) against the explicitly named
    folder. Returns candidate records (artifact name, project name,
    confidence, candidate_id) for the UI to render as candidate-card
    widgets. Never called with an unspecified/default path — the
    folder path must come from the user, per E2's inherited
    read-only/scoped-folder boundary.

respond_to_candidate(candidate_id: str, decision: "accept" | "reject") -> dict
    Calls core.MemoryStore.review_artifact_project_candidate (already
    implemented — E2-3). Returns the updated candidate state for the
    UI to reflect (e.g. gray out the buttons, show accepted/rejected).
```

No other bridge function exists. Adding one later is a Design Council
decision, not a Development-time convenience.

## Message rendering

- Assistant messages (status answers, candidate cards) render from the
  same plain text/dicts the Python side already returns — Qt's
  `Qt.RichText` mode on `QLabel` handles basic formatting (bold,
  lists, headers) directly; a candidate dict renders as a `QFrame`
  card with a name/confidence line and two buttons wired to
  `respond_to_candidate`.
- User messages (typed queries, folder paths for scanning) render as
  plain text, right-aligned, per the chat-environment feel the human
  gate asked for.
- No message persists to disk — session-only, per `UI_DEBATE.md`'s
  synthesis (unaffected by this revision). Refreshing/reopening the
  app starts a new thread; nothing about the user's actual project
  data is lost, since that lives in `MemoryStore` exactly as before.

## Failure behavior

No initialization-failure fallback is needed for this revision — the
failure mode it existed for in the original design (an embedded
Chromium engine failing to load) does not exist when there's no
embedded browser engine. A genuine, unexpected Qt/PySide6 startup
failure is still not swallowed silently: it surfaces via Python's
normal exception path (uncaught, visible), same as any other bug —
this is not a new resilience requirement invented for the GUI, just
the absence of a resilience requirement the rejected alternative
specifically needed.

## Security and reliability considerations

- Fully local: no network call anywhere in this feature's code path
  (unchanged from `E2_TRD.md`'s established property) — trivially
  true here since there's no embedded web content or bridge object to
  audit at all, a stronger guarantee than the original design's
  "scoped bridge" mitigation.
- The three functions above are the only entry points from the UI
  into `MemoryStore`/`project_classification`/`continuity` — verifiable
  directly by reading the signal-handler wiring code, a concrete QA
  check.

## Integration points

- `cli.py`'s existing commands (`classify-folder`,
  `review-artifact-candidate`, and E1's future CLI exposure, if any)
  are kept as-is — a second, scriptable front end, not superseded.
- New entrypoint: `memory-os gui` (or equivalent), launching the
  PySide6 window described above. Follows the same dispatch pattern
  `cli.py` already uses for adding a subcommand.
- Packaging (bundling PySide6 for a Windows user who may not have a
  Python environment set up) is a Development-time detail (e.g.
  PyInstaller) — noted here so it isn't missed, not designed further
  at this stage. Lighter than the original design's packaging concern,
  since `PySide6-Addons`/Chromium is no longer part of the bundle.
