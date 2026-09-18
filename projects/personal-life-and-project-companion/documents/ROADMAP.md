# Roadmap — personal-life-and-project-companion

Produced by: Product Manager (Planning), per `AGENTS/Product-Manager/
AGENT.md`'s versioned-roadmap requirement. Sequences every epic from
`EPIC_SELECTION.md` into a named version, using that same MoSCoW/
dependency reasoning — no new judgment call made here.

**No durations or dates appear below, on purpose.** Per
`DEPARTMENTS/Developer_Organization/SHARED/PROJECT_TIMELINE.md`'s
existing rule, Product Manager does not estimate duration — that
comes from Design Council (at scoping time) and Development (once
building), recorded separately in `PROJECT_TIMELINE.md`'s own
DURATION/START/FINISH fields once this project reaches that stage.

## V1

- **E1 — Project Status & Re-entry Briefing** (MUST HAVE)
- **E2 — File & Code → Project Classification** (MUST HAVE)

No dependency on any other epic — both selected `MUST HAVE` directly
in `EPIC_SELECTION.md`, with E1 mostly extending code that already
exists (per `AUDIT_REPORT.md`).

## V2

- **E3 — Idea Relationship Tracking** (SHOULD HAVE)
- **E4 — Emotional/Behavioral Signal Extraction** (SHOULD HAVE)

E3's dependency (E1 — "needs a briefing to surface into," per
`EPIC_SELECTION.md`) is satisfied once V1 lands. E4 has no hard
dependency (`EPIC_SELECTION.md`: "None blocking") but is placed here
rather than V1 per that same document's own sequencing note — it's
naturally ordered after E1/E2 prove the core loop, not blocked by
them.

## V3

- **E5 — Proactive Focus Guidance** (COULD HAVE)

Hard dependency on **both** E3 and E1 (per `EPIC_SELECTION.md`:
"Depends on E1 and E3 — a hard blocker, not soft preference"). Since
E3 doesn't land until V2, E5 cannot land before V3 — this is a
mechanical consequence of the dependency, not an independent priority
call.

## Not yet versioned

None — every epic from `EPIC_SELECTION.md` is sequenced above; no
epic was labeled `WON'T HAVE (this release)` in that document, so
there is nothing to carry forward as explicitly deferred.

## Summary

```text
V1 → E1, E2   (MUST HAVE, no dependency)
V2 → E3, E4   (SHOULD HAVE, E3's dependency on E1 satisfied by V1)
V3 → E5       (COULD HAVE, hard dependency on E1 + E3)
```
