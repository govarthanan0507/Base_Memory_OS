# Technical Requirements — Desktop GUI (chat-style, cross-cutting: E1 + E2 delivery)

Per `UI_DEBATE.md`'s synthesis. This does not replace E1/E2's `FRD.md`/
`TRD.md` functional behavior or data model — it defines the new
presentation layer calling the same, already-designed logic.

## Architecture overview and decisions

```text
PySide6 native window (Windows target)
  └── QWebEngineView (Chromium, local files only — no network)
        └── chat_ui/index.html + style.css + chat.js
              (bundled with the app, never fetched remotely)
        ↕ QWebChannel bridge (closed function set, below)
  └── Python side: existing MemoryStore / discovery.py / continuity.py
        (unchanged — called from the bridge instead of cli.py's
         dispatch, cli.py itself is kept, not removed)
```

**Rejected alternative**: hand-built Qt widgets (bubbles via
`QListView` + custom delegate). Rejected per `UI_DEBATE.md`'s
Frontend Architect finding — reinvents web-rendering primitives
(markdown, inline buttons in a message) for a worse visual result than
reusing HTML/CSS for the same purpose they're already good at.

**Rejected alternative**: a full local web server + browser tab
instead of an embedded view. Rejected — the user asked for a desktop
GUI specifically (already confirmed at the human gate); a browser tab
is a different interface class, and a local server introduces a
listening process this design has no reason to need when
`QWebEngineView` renders local files directly.

## QWebChannel bridge — closed function list (Security-Architect's requirement)

Only these functions are exposed to the embedded page's JavaScript —
no general object, no eval-style bridge:

```text
submit_query(text: str) -> str
    Routes a typed status question to continuity.py's existing
    render_project_reentry_brief/project_context. Returns the answer
    as a chat message (markdown string) for the JS side to render.

start_scan(folder_path: str) -> list[dict]
    Calls discovery.py's classify_artifacts_against_projects
    (E2_TRD.md) against the explicitly named folder. Returns
    candidate records (artifact name, project name, confidence,
    candidate_id) for the JS side to render as candidate-card
    messages. Never called with an unspecified/default path — the
    folder path must come from the user, per E2's inherited
    read-only/scoped-folder boundary.

respond_to_candidate(candidate_id: str, decision: "accept" | "reject") -> dict
    Calls the existing review flow (E2_TRD.md step 4/5 — relate() on
    accept, status update on reject). Returns the updated candidate
    state for the JS side to reflect (e.g. gray out the buttons,
    show accepted/rejected).
```

No other bridge function exists. Adding one later is a Design Council
decision (this same debate's territory), not a Development-time
convenience.

## Message rendering

- Assistant messages (status answers, candidate cards) render from
  markdown-ish structure the Python side already returns as plain
  text/dicts — `chat.js` handles basic formatting (bold, lists,
  headers) and renders a candidate dict as a card with two buttons
  wired to `respond_to_candidate`.
- User messages (typed queries, folder paths for scanning) render as
  plain text, right-aligned per the chat-environment look the human
  gate asked for.
- No message persists to disk — session-only, per `UI_DEBATE.md`'s
  synthesis. Refreshing/reopening the app starts a new thread; nothing
  about the user's actual project data is lost, since that lives in
  `MemoryStore` exactly as before, unaffected by this UI decision.

## Failure behavior (per the Independent Critic's resolved finding)

If `QWebEngineView` fails to initialize (missing/broken Chromium
runtime on the user's machine), the app shows a plain `QLabel`/
`QPushButton`-only fallback screen stating the chat UI couldn't start,
naming the specific error, and pointing at `cli.py`'s existing
commands as a working alternative. The app never crashes silently on
this failure, and the CLI path is never removed as a fallback option.

## Security and reliability considerations

Per `UI_DEBATE.md`'s Security-Architect findings:
1. `QWebEngineView` loads only bundled local files (`file://` or Qt's
   resource system) — remote URL loading is disabled at the view's
   settings level, not just "not used by convention."
2. The `QWebChannel` bridge is the three functions above, nothing
   else — verifiable directly by reading the bridge's registration
   code, a concrete QA check.
3. No new network-facing code path is introduced anywhere by this
   decision — the embedded Chromium engine renders local content only,
   consistent with E2_TRD.md's existing "fully local" property.

## Integration points

- `cli.py`'s existing commands (`classify-folder`,
  `review-artifact-candidate`, and whatever E1 exposes) are kept
  as-is — a second, scriptable front end, not superseded.
- New entrypoint: `memory-os gui` (or equivalent), launching the
  PySide6 window described above. Follows the same dispatch pattern
  `cli.py` already uses for adding a subcommand.
- Packaging (bundling PySide6 + WebEngine for a Windows user who may
  not have a Python environment set up) is a Development-time detail
  (e.g. PyInstaller), not an architecture decision — noted here so it
  isn't missed, not designed further at this stage.
