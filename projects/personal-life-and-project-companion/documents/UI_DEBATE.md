# Design Council Debate — Desktop GUI Architecture (cross-cutting: E1 + E2 delivery)

Roles convened: Architect, UX Designer, UI Designer, Frontend
Architect, Security-Architect. Backend/Data-Architect not convened —
E1/E2's underlying logic (`MemoryStore`, `discovery.py`'s
classification functions, `continuity.py`'s briefing functions) is
unchanged by this decision; only the presentation layer is being
decided.

## Inputs from the human gate

1. Desktop GUI, not CLI (the user cannot work in a terminal).
2. Windows target, polish preferred over zero-new-dependency
   (PySide6/Qt accepted — `UI_HARD_CONSTRAINTS_PRECHECK.md`).
3. **New, specific**: the interface should look and feel like this
   chat environment (Claude/ChatGPT-style) — a conversational thread,
   not a forms/tabs GUI.

## Positions

**UX Designer**: A chat-style interface actually fits this product's
own interaction model well, not just aesthetically — E1's story is
literally "ask a question, get a status answer" (E1-1), and E2's
candidate review is naturally a back-and-forth ("here's what I found,
accept or reject each one"). Proposes: one continuous conversation
thread as the entire app, no separate tabs for E1 vs E2 — the system
proactively posts scan results as messages, and the user asks status
questions in the same thread, matching how the user already described
wanting the product to "proactively guide," not passively sit in
separate screens.

**UI Designer**: To actually look like this chat environment (not just
"a chat app"), needs message bubbles with clear user/assistant
distinction, markdown rendering (the briefing text and candidate
lists benefit from headers/lists/bold, not plain text dumps), and
inline interactive elements *inside* a message (Accept/Reject buttons
directly on a candidate message, not a separate dialog) — closer to
how this environment renders tool results and questions inline than a
generic messaging app.

**Frontend Architect**: Recommends against building bubble-rendering,
markdown parsing, and inline-button layout from raw Qt widgets — that's
reinventing a lot of well-solved web rendering for a worse result.
Proposes: **PySide6's `QtWebEngineWidgets` (`QWebEngineView`)** — an
embedded Chromium view inside the native desktop window — rendering a
local HTML/CSS/JS chat UI (plain files bundled with the app, no
network fetch). This keeps the "one desktop app" delivery the user
asked for while getting genuine chat-interface fidelity cheaply. A
small local bridge (`QWebChannel`, part of the same PySide6 package —
no additional new dependency beyond what Category 9 already accepted)
lets the embedded page call back into Python for the actual scan/
accept/reject logic; nothing about this reaches the network — the
Chromium engine is only rendering local files.

**Architect**: Confirms this doesn't change E1/E2's actual architecture
underneath — `MemoryStore`, `discovery.py`, `continuity.py` are called
by the same Python process as before, just from a Qt/WebEngine event
handler instead of a CLI dispatch function (`cli.py`'s existing
pattern is *not* deleted — kept as-is for scripting/automation, per
"don't discard a working interface," the GUI becomes a second front
end calling the same underlying functions, never a fork of the logic).

**Security-Architect**: One finding. `QWebEngineView` must load only
the bundled local HTML/CSS/JS files (via `file://` or Qt's resource
system) — never remote content, and JavaScript's callback bridge
(`QWebChannel`) must expose only the specific accept/reject/scan/query
functions needed, not a general eval-style bridge. This preserves the
same "fully local, no network call anywhere in this feature's code
path" property `E2_TRD.md` already established — a chat-*styled* UI
must not quietly become a chat-*service* UI with a real network
dependency.

## Challenges

**Frontend Architect → UI Designer**: Full markdown+bubble rendering
from scratch is real UI work, not a small addition. UI Designer's
response: **accept** — scoped down for V1 to what E1/E2 actually need
(status text with basic formatting, a candidate card with
name/confidence/two buttons), not a general-purpose chat SDK; richer
formatting is a later-version concern if it turns out to be needed.

**Security-Architect → Frontend Architect**: confirm the `QWebChannel`
bridge is enumerated explicitly (a fixed, named set of callable
functions), not passed as a generic object. Frontend Architect's
response: **accept** — added to `UI_TRD.md` below as an explicit,
closed function list, not an open bridge.

## Synthesis

- One continuous chat-thread interface for both E1 (status queries)
  and E2 (scan results, candidate accept/reject), not tabs/forms
  (UX Designer's proposal).
- Rendered via `QWebEngineView` (local files only) inside a native
  PySide6 desktop window, with a closed-set `QWebChannel` bridge back
  to the existing Python logic (Frontend Architect's proposal,
  Security-Architect's bridge-scoping requirement accepted).
- `cli.py`'s existing commands are kept, not replaced — the GUI is a
  second, additional front end (Architect's finding).
- Message history is **session-only, not persisted to disk** —
  consistent with the inherited boundary that project status/
  documentation is maintained internally and surfaced conversationally,
  never written back to disk (`DECISION_CONTRACT.md`). Re-opening the
  app starts a fresh thread; nothing about *this* decision changes
  what data `MemoryStore` itself persists (artifacts, candidates,
  relations — unchanged, already persisted, exactly as before).

## Independent Critic

Reviewed the synthesis fresh. One finding: nothing above defines what
happens if `QWebEngineView`/Chromium fails to initialize on the user's
Windows machine (a real, non-trivial native dependency to bundle,
distinct from a pure-Python package). Does the app crash, or degrade?

**Resolution**: on `QWebEngineView` initialization failure, the app
falls back to a plain Qt-widgets error screen (no chat styling
needed for this one case) stating the GUI couldn't start and pointing
at `cli.py`'s existing commands as a working fallback — never a silent
crash, and never blocking the user from the tool entirely just because
the chat shell failed to load. Added to `UI_TRD.md` explicitly.

---

## Reconvene — `QWebEngineView` vs. native Qt widgets (dated addendum, supersedes the architecture choice above, not the whole debate)

Roles reconvened: Frontend Architect, UI Designer, Architect,
Security-Architect. Trigger: `REPO_CANDIDATES.md`'s UI-shell-candidate
research (checking whether an open-source precedent already existed
for this exact shape of app) surfaced real evidence never checked
against the original decision above — two verified, real PySide6
chat-GUI projects (`yjg30737/pyqt-openai`, 149★, MIT;
`BriannaThorez/NutellaLLM_GUI`, 7★, GPL-3.0), and **neither uses
`QWebEngineView`** — both render their chat UI from native Qt widgets.

**Frontend Architect (revising own prior position)**: The original
reasoning ("hand-built widgets would be worse than reusing web
rendering") was never checked against real precedent, and the
precedent that exists points the other way. Also newly relevant,
missed in the first pass: Qt's own `QTextBrowser`/`QTextEdit` support
a real subset of HTML4/CSS2 rich text **natively** — bold, lists,
headers, tables, basic styling, and clickable links via
`anchorClicked`/`linkActivated` — with no Chromium involved at all.
For E1/E2's actual content (status text with basic formatting, a
candidate card with a name/confidence line and two buttons), this
covers everything `UI_DEBATE.md`'s original UI Designer position
asked for. Revises the proposal: **native Qt widgets**, not
`QWebEngineView`.

**UI Designer**: Confirms the revised approach still satisfies the
original ask (chat bubbles, inline Accept/Reject on a candidate
message) — a `QScrollArea` holding a vertical stack of message
widgets: `QLabel`(`textFormat=Qt.RichText`) for assistant/user text
bubbles, and a small `QFrame` (label + two `QPushButton`s) for
candidate cards. Visually close enough to a chat thread for this
product's actual need; not claiming pixel-parity with this specific
chat environment's own CSS, which was never a stated requirement,
only a *feel* (`UI_DEBATE.md`'s original human-gate input).

**Architect**: No change to E1/E2's underlying logic either way — this
is still purely a presentation-layer decision. Notes the practical
win: removing `QWebEngineView` also removes `PySide6-Addons`'s
Chromium payload (a much heavier install than plain `PySide6`), and
removes an entire class of failure (Chromium failing to initialize)
the original synthesis had to define a fallback for at all.

**Security-Architect**: The `QWebChannel` bridge-scoping requirement
(a closed, named function list) is now **moot, not violated** — with
no embedded web content, there is no JS/Python bridge to scope in the
first place. The three functions (`submit_query`, `start_scan`,
`respond_to_candidate`) still exist, just as direct Python method
calls wired to Qt widget signals (button `clicked`, line-edit
`returnPressed`) instead of a `QWebChannel` object. No new finding.

## Revised synthesis

- **Native Qt widgets**, not `QWebEngineView` — a `QScrollArea` of
  message widgets (`QLabel` rich-text bubbles, `QFrame` candidate
  cards with inline buttons), a `QLineEdit` + send button for input.
- `PySide6` alone (no `PySide6-Addons`/QtWebEngine) — Hard Constraint
  #9's earlier acceptance still holds (one new dependency, PySide6),
  just a lighter one than originally scoped.
- The three bridge functions (`submit_query`, `start_scan`,
  `respond_to_candidate`) are unchanged in name and behavior — only
  their calling convention changes (direct Qt signal/slot, not
  `QWebChannel`).
- No fallback-on-initialization-failure design is needed — removed as
  a requirement, not just resolved, since the failure mode it existed
  for (Chromium failing to load) no longer exists.
- Everything else `UI_DEBATE.md`'s original synthesis decided (one
  continuous thread for E1+E2, `cli.py` kept as a second front end,
  session-only message history) is unchanged.

## What this reconvene does not do

- Does not reopen Hard Constraint #9 (new dependency) or #12
  (platform) — both already resolved and unaffected by this narrower,
  presentation-mechanism change.
- Does not claim native widgets look *identical* to this chat
  environment — the human gate's actual ask ("look and feel like
  this chat environment") is judged satisfiable by a competent
  chat-bubble layout, not pixel-for-pixel replication; if that turns
  out to be insufficient once built, that's real feedback for a
  follow-up pass, not assumed now.
