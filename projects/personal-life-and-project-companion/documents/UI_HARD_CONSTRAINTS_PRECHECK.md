# Hard Constraints Pre-Check — Desktop GUI (cross-cutting: E1 + E2 delivery mechanism)

Per `COUNCILS/Design-Council/COUNCIL.md`: loaded before debate begins.
This is a **re-entry**, not a new epic — E1 and E2's functional scope
(what they do) is unchanged; this decides how the user interacts with
them, which was previously assumed CLI-only (`AUDIT_REPORT.md`'s
finding that no UI existed or was planned) and is now explicitly
changed by the user's own request.

| # | Category | In play? | Status |
|---|---|---|---|
| 1 | Money | No | Still $0 — PySide6 is free/open-source, no paid tooling |
| 2 | Data privacy | No (inherited, unchanged) | Still local-only; a GUI process reads the same local SQLite store, no new data leaves the machine |
| 3 | Irreversible operations | No | Unchanged — GUI accept/reject calls the same propose-then-confirm functions E2 already designed |
| 4 | Security posture/exposure | No (inherited) | Still no network exposure; a desktop GUI window is not a listening service |
| 5 | Licensing | **Yes — resolved below** | PySide6 is LGPLv3 (official Qt for Python bindings) |
| 6 | Vendor lock-in | No | Qt/PySide6 is a widely-used, actively maintained, cross-platform toolkit; no proprietary vendor dependency |
| 7 | Scope of AI autonomy | No (inherited) | Unchanged — GUI still requires explicit user accept/reject, same as CLI did |
| 8 | Naming/branding | No | N/A |
| 9 | New third-party dependencies | **Yes — the point of this decision** | PySide6 is a new dependency, explicitly accepted below per the user's own stated preference (polish over zero-dependency) |
| 10 | Performance/reliability commitments | No | No uptime/real-time promise |
| 11 | Timeline/deadlines | No | None stated |
| 12 | Platform/device support | **Yes — resolved below** | User confirmed Windows as the target platform |
| 13 | Operational capacity | No (inherited) | Solo project, unchanged |

## Category 5 — Licensing, resolved

PySide6 is distributed under LGPLv3 by The Qt Company. For a
personal-use, non-commercial, non-distributed application (per
`DECISION_CONTRACT.md`'s confirmed no-distribution-intent boundary),
LGPLv3 imposes no obligation that matters here — its notice/relinking
requirements apply to *redistributing* the library, which doesn't
happen for a tool that never leaves this user's own machine. Recorded
per `REUSE_AND_LICENSE_RULE.md`'s pattern: **not blocking now**, but
this finding must resurface automatically if shipping/distribution
intent ever changes (the same rule already governing every other
license finding in this project).

## Category 9 — New dependency, resolved

**Accepted.** The user explicitly chose "better look and feel" over
"zero new dependency" when asked directly (Hard Constraint categories
route to the human regardless of Council confidence — this was not a
Council judgment call, it was asked and answered). PySide6 is the
concrete dependency this unlocks.

## Category 12 — Platform, resolved

**Windows**, confirmed directly by the user. PySide6 supports Windows,
macOS, and Linux equally — no Windows-specific packaging blocker is
introduced by this choice, and the same codebase would run unmodified
on the other platforms if that ever changes.

**Result**: two categories (5, 9) required an explicit decision and
both are now resolved and recorded above, not decided silently by the
Council. Category 12 required a fact only the user could supply, now
confirmed.

**Revision note**: `UI_DEBATE.md`'s later reconvene (native Qt widgets
instead of `QWebEngineView`) narrows the dependency to plain `PySide6`
— `PySide6-Addons`/QtWebEngine's Chromium payload is no longer needed.
This makes Category 9's already-accepted dependency lighter, not a new
one; nothing above changes as a result.
