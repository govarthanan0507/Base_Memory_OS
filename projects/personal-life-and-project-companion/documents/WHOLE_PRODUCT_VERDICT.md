# Whole-Product Architecture Verdict — personal-life-and-project-companion

Per `CodeFoundry_Skill`'s `COUNCILS/Design-Council/WHOLE_PRODUCT_ARCHITECTURE_GATE.md`
(added this cycle). Issued once, before Development starts on E1/E2 —
not a second per-epic debate, and not a full `TRD.md`/`FRD.md` for E3-E5
(which haven't been picked up yet).

**Inputs reviewed**: `ROADMAP.md` (V1: E1+E2, V2: E3+E4, V3: E5),
`EPIC_SELECTION.md`'s epic decomposition and dependency table, E2's
full design (`E2_HARD_CONSTRAINTS_PRECHECK.md`, `E2_DEBATE.md`,
`E2_FRD.md`, `E2_TRD.md`). E1 has no `TRD.md`/`FRD.md` of its own —
confirmed by direct search of this project's documents folder; its
only description anywhere is `EPIC_SELECTION.md`'s one paragraph
("extends `continuity.py`/`timeline.py`, adds idea-hopping/completion-
signal fields"). This absence is itself relevant to Finding 1 below.

## 1. FORECLOSURE CHECK

**Finding — named, not generic**: `EPIC_SELECTION.md` describes E1 as
adding "idea-hopping ... fields" to `continuity.py`'s re-entry
briefing. `EPIC_SELECTION.md` also describes E3 as the epic that
actually tracks idea-to-idea relationships, via a **new semantic
relation type on the existing generic `relations` table**, specifically
so it can "surface through E1's briefing." These are two different
epics independently reasoning about the same concept (an idea-hop) at
different times, and **E1 has never actually been designed** — no
`TRD.md` exists to say what "idea-hopping fields" means concretely (a
column on an existing table? a new table? computed at query time?).

If E1's Development work invents its own ad hoc idea-hopping
representation now (because nothing stops it — E1 is Tier 1, no
Council debate required), and E3's later Tier-2/3 pass then designs
the *real* relation-type mechanism nine months from now, E3 will
either have to migrate away from whatever E1 built, or E1's "fields"
become dead weight. This is a real, specific foreclosure risk, not a
vague scalability worry — it names the exact two epics and the exact
concept in conflict.

**No other foreclosure found.** E2's schema (`artifact_project_candidates`,
additive-only, explicitly does not reuse `scan_workspace`'s auto-
`relate()`) does not touch E4's territory (conversation-text-only
signal extraction) or E5's (depends on E1+E3 data, not E2's). E4 and
E5 have no code yet to foreclose anything.

## 2. ARCHITECTURAL DIRECTION CHECK

All five epics point at one coherent system: local-only, SQLite,
zero network calls, CLI-only, propose-then-confirm for anything that
writes a link between two things, no new third-party dependency
introduced anywhere yet (E2 explicitly resolved Hard Constraint #9 as
"not triggered"). Nothing in E1-E5's descriptions implies a server
component, a cloud call, or a UI — consistent with `idea.md`'s own
inherited scope boundaries (read-only, local, personal-use ceiling).
No contradictory direction found.

## 3. KNOWN-UNKNOWN SURFACING

- **E4 (Emotional/Behavioral Signal Extraction)**: what technique
  actually extracts a behavioral signal from conversation text with
  zero new dependencies is genuinely undecided. E2 already
  demonstrated a heuristic, no-new-dependency approach is possible for
  a *different* classification problem — whether the same
  no-new-dependency discipline holds for language-based emotional
  signal (vs. needing a sentiment library or embeddings, which would
  re-open Hard Constraint #9) is exactly the kind of question this
  gate should surface rather than pre-answer. Named as open; E4's own
  Design Council pass, when it's picked up, resolves it.
- **E5 (Proactive Focus Guidance)**: depends on E1+E3 data being not
  just present but *reliable* enough that a proactive nudge ("you're
  idea-hopping again") is more helpful than annoying/wrong. No
  accuracy bar for this exists yet anywhere in the documents. Named as
  open; not resolvable before E1/E3 produce real data to evaluate
  against.

## Verdict

```text
GO WITH NOTED RISKS
```

Development may proceed on E1 and E2 as currently designed. One risk
is carried forward, not silently dropped:

- **E1's Development pass must not invent its own idea-hopping data
  shape informally.** Before writing any idea-hopping/completion-
  signal field into `continuity.py`, E1's implementer either (a) keeps
  the addition to genuinely E1-only concerns (completion/confidence
  signal, which has no overlap with E3) and defers anything that is
  actually an idea-to-idea relationship to E3's own future design, or
  (b) if an idea-hopping representation is truly needed now, files it
  as a placeholder explicitly labeled provisional-pending-E3, so E3's
  later Design Council pass treats it as a candidate to confirm or
  revise, not as settled ground it must work around. Either path is
  acceptable; silently building a permanent idea-hop schema with no E3
  awareness is not.

Two open questions (E4's dependency-free feasibility, E5's reliability
bar) are named for their own future Design Council passes to resolve
when picked up — not blocking V1's E1/E2 Development, and not
force-resolved now.

## What this verdict does not do

- Does not produce `TRD.md`/`FRD.md` for E3, E4, or E5 — they remain
  undesigned until picked up, per `DISCOVERY_PROTOCOL.md`'s
  just-in-time principle.
- Is not repeated per epic — this is the one whole-product check
  before V1's Development begins; E3/E4/E5 still get their own normal
  per-epic Tier 2/3 Design Council pass when their turn comes.
