# Hard Constraints Pre-Check — E5 (Proactive Focus Guidance)

Per `COUNCILS/Design-Council/COUNCIL.md`: loaded before any design
decision, determines whether a decision was ever this pass's to make.

| # | Category | In play? | Status |
|---|---|---|---|
| 1 | Money | No | $0 — no paid tooling, no API calls |
| 2 | Data privacy | No (inherited) | Signal is computed from data already stored locally (project_events, relations); nothing new leaves the machine |
| 3 | Irreversible operations | No | Read-only computation, no write path beyond what already exists |
| 4 | Security posture | No (inherited) | No new network exposure |
| 5 | Licensing | No | No third-party component adopted |
| 6 | Vendor lock-in | No | N/A |
| 7 | Scope of AI autonomy | No | Surfaced only when the user asks (a CLI command), never an unprompted interruption/notification — see resolution below |
| 8 | Naming/branding | No | N/A |
| 9 | New third-party dependencies | No | Reuses E1's/E3's existing data (`project_completion_signal`, `related_ideas`) and a plain, inspectable counting heuristic — no library |
| 10 | Performance/reliability commitments | **Open — resolved below** | The real, named open question from `WHOLE_PRODUCT_VERDICT.md`'s Finding for E5 |
| 11 | Timeline/deadlines | No | None stated |
| 12 | Platform/device support | No (inherited) | Unchanged — local, single-user |
| 13 | Operational capacity | No (inherited) | Solo project |

## Category 7 — resolved (scope-narrowing decision, named explicitly)

`idea.md`'s original vision described E5 as flagging idea-hopping "as
it happens" — read literally, that could mean an unprompted, live
interruption (a notification firing mid-conversation). This CLI-only
product has no mechanism for that today (no background process, no
notification surface), and building one would be a new architectural
pattern with its own Category 7/12 questions this epic's own scope
doesn't need to answer. **Resolution**: E5 delivers the guidance as
an on-demand report (`focus-guidance` CLI command), computed fresh
each time the user asks — the same "surfaced when asked, not
volunteered unprompted" pattern E1's `reentry-project` and E4's
`emotional-signal` already use. "As it happens" is satisfied by the
signal always reflecting the *current* state the moment it's asked
for, not by an autonomous push. If true unprompted notification is
wanted later, that is a new epic with its own Category 7/12 pass, not
a silent expansion of this one.

## Category 10 — resolved

**The real open question, named in `WHOLE_PRODUCT_VERDICT.md`**: "no
accuracy bar for this exists yet ... not resolvable before E1/E3
produce real data to evaluate against." E1 and E3 are now merged
(`main` at `d8ae659`), so real data exists. Resolution, consistent
with E4's own precedent (a heuristic is acceptable if its basis is
inspectable, not black-box): E5 makes **no accuracy promise** to the
user at all — every output names its own evidence (which specific
projects, which specific recent events, in what order) so the user
can judge it themselves rather than trust an implied score. This
sidesteps rather than satisfies a numeric reliability bar, which is
the correct outcome per `FEASIBILITY_REPORT.md`'s own risk framing
("a wrong read is a bad suggestion, not corrupted data") — the same
standard already accepted for E4. No performance/uptime commitment is
made anywhere in this feature.

**Result**: two categories required resolution and are now resolved
and recorded above, not decided silently.
