# Hard Constraints Pre-Check — E4 (Emotional/Behavioral Signal Extraction)

Per `COUNCILS/Design-Council/COUNCIL.md`: loaded before any design
decision, determines whether a decision was ever this pass's to make.

| # | Category | In play? | Status |
|---|---|---|---|
| 1 | Money | No | $0 — no paid tooling, no API calls |
| 2 | Data privacy | No (inherited) | Signal is computed from conversation text already stored locally; nothing new leaves the machine |
| 3 | Irreversible operations | No | Read-only computation, no write path beyond what already exists |
| 4 | Security posture | No (inherited) | No new network exposure |
| 5 | Licensing | Not triggered | No third-party lexicon/library adopted — see Category 9 |
| 6 | Vendor lock-in | No | N/A |
| 7 | Scope of AI autonomy | No (inherited) | This is a read-only signal surfaced to the user, not an autonomous action |
| 8 | Naming/branding | No | N/A |
| 9 | New third-party dependencies | **Open — resolved below** | The real, named open question from `WHOLE_PRODUCT_VERDICT.md`'s Finding for E4 |
| 10 | Performance/reliability commitments | No | No uptime/real-time promise |
| 11 | Timeline/deadlines | No | None stated |
| 12 | Platform/device support | No (inherited) | Unchanged — local, single-user |
| 13 | Operational capacity | No (inherited) | Solo project |

## Category 9 — resolved

**No new dependency required.** Per `E2_DEBATE.md`'s own precedent
(a heuristic, no-embeddings approach proved sufficient for file
classification, with embeddings explicitly named as a future option
only if heuristic accuracy proves too low in practice — not assumed
insufficient in advance), the same discipline applies here: a small,
built-in lexicon of frustration/positive/negative cue words, matched
against message text, produces a bounded, explainable signal with
zero new runtime dependency. This directly answers the open question
`WHOLE_PRODUCT_VERDICT.md` named for E4 ("what technique actually
extracts a behavioral signal... with zero new dependencies") —
resolved: yes, a lexicon-based heuristic is sufficient for this
epic's scope, per the accuracy tradeoff already accepted in
`FEASIBILITY_REPORT.md` ("a wrong read is a bad suggestion, not
corrupted data").

**Result**: one category required resolution and is now resolved and
recorded above, not decided silently.
