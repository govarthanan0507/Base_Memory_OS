# Hard Constraints Pre-Check — E2 (File & Code → Project Classification)

Per `COUNCILS/Design-Council/COUNCIL.md`: loaded before debate begins,
determines whether a decision was ever the Council's to make.

| # | Category | In play? | Status |
|---|---|---|---|
| 1 | Money | No | Already resolved ($0, `FEASIBILITY_REPORT.md`) |
| 2 | Data privacy | **Yes** | **Inherited, not open** — `idea.md`/`DECISION_CONTRACT.md` already set this: read-only, scoped to user-designated folders, never blanket access. The Council operates within this, does not re-decide it. |
| 3 | Irreversible operations | No | Read-only + propose-then-confirm by design; nothing is destructive |
| 4 | Security posture/exposure | No (inherited) | Local-only, no network exposure planned; flagged if that changes |
| 5 | Licensing | Not yet triggered | No candidate is being structurally adopted (per `REPO_CANDIDATES.md`, none fully cover this piece); would trigger if that changes |
| 6 | Vendor lock-in | Not yet triggered | No new vendor/platform dependency proposed below |
| 7 | Scope of AI autonomy | **Yes** | **Inherited, not open** — `idea.md` already set the leash: propose-then-confirm, never blind auto-mapping. The Council operates within this. |
| 8 | Naming/branding | No | N/A |
| 9 | New third-party dependencies | **Open — must be flagged if triggered** | Not yet decided; the debate below resolves this explicitly rather than deciding silently |
| 10 | Performance/reliability commitments | No | No uptime/real-time promise to the user |
| 11 | Timeline/deadlines | No | None stated; `idea.md` explicitly expects iteration |
| 12 | Platform/device support | No (inherited) | Single user's own machine; not a multi-platform product |
| 13 | Operational capacity | No (inherited) | Solo project, no ops team — already the working assumption throughout |

**Result**: two categories (2, 7) are materially relevant but already
resolved by the human upstream — the Council respects them, does not
re-open them. One category (9) is genuinely undecided and must be
resolved explicitly in the debate below, not silently.
