# Requirements — E5 (Proactive Focus Guidance)

Produced by: Product Owner + a short Tier 2 design pass (Backend-
Architect, Data-Architect), per `PROCESS_SCALING.md`.

## Tiering determination

**Tier 2 — small crew, short design note, no full debate.** Not
Tier 1: idea-hop detection is genuinely new logic (no existing
pattern to reuse directly), and `E5_HARD_CONSTRAINTS_PRECHECK.md`
resolves two Hard Constraint categories (7, 10) rather than zero —
`PROCESS_SCALING.md`'s own rule defaults one tier up when ambiguous.
Not Tier 3: it stays within one domain (backend/continuity logic),
introduces zero new dependency, and Backend-Architect/Data-Architect
reviewed with no disagreement, so the full Synthesizer/Independent-
Critic debate machinery was not invoked.

## Design note

**Backend-Architect**: Two independent signals, composed into one
report, both purely additive reads over data E1/E3 already produce:

1. **Idea-hop detection** — look at the most recent `window`
   `project_events` rows *across all projects* (not scoped to one
   project, unlike everything E1 built), ordered by timestamp
   descending. Count how many consecutive pairs in that window belong
   to different projects ("switches"). If the switch ratio
   (switches / (window size − 1)) is at or above a fixed, named
   threshold (0.5), report hopping detected, naming the actual
   project names/timestamps involved as evidence — never a bare
   score. Fewer than 2 events, or fewer than 2 distinct projects in
   the window, means hopping is explicitly not detected rather than
   guessed.
2. **Cross-project completion rollup** — call E1's existing
   `project_completion_signal` for every known project and list them
   together, so "how much of each is done, how many are active" is
   answered in one place instead of one project at a time.

Both signals return their own evidence alongside the label (same
inspectable-not-black-box discipline as E4), and both are computed
fresh on every call — no caching, no background job.

**Data-Architect**: No new table. `project_events` (has a
`project_id` and a `timestamp` already) and `projects` are queried
directly; nothing new is persisted, consistent with E1's own
on-demand-computation pattern and `idea.md`'s "maintained internally,
never written back to disk" constraint.

## User story

```text
As a user who tends to rapidly switch between projects and ideas
I want a report that flags when I've been idea-hopping and shows how
each of my active projects is progressing, without having to ask
project-by-project
So that I can notice the pattern and refocus, with the actual
evidence in front of me rather than a bare verdict
```

**Priority**: Could Have (V3)

**Acceptance criteria**:
- [ ] Given recent `project_events` across 3+ different projects in
      close succession, when the guidance report is generated, then
      idea-hopping is reported as detected, naming the specific
      projects and timestamps that triggered it.
- [ ] Given recent `project_events` all on one project, then hopping
      is explicitly reported as not detected, not silently omitted.
- [ ] Given fewer than 2 recorded project events anywhere, then the
      hop signal says so explicitly (`unavailable`) rather than
      defaulting to "not hopping" as if it had evidence either way.
- [ ] Given 2+ known projects, the report includes each project's own
      `project_completion_signal` output (reusing E1's function
      directly, not reimplementing it).
- [ ] Nothing about this feature writes a new record anywhere, and no
      new table is created — verifiable by a test that greps the
      implementing module for persistence calls, same pattern as
      E4's own regression test.

## Non-goals (explicitly, not smoothed over)

- Does not push an unprompted notification — resolved explicitly in
  `E5_HARD_CONSTRAINTS_PRECHECK.md` (Category 7): this is an
  on-demand CLI report, not a background/interrupting mechanism. A
  true unprompted-notification feature is a separate future epic with
  its own Hard Constraints pass.
- Does not estimate "how much time is needed to finish" a project in
  absolute terms (hours/days) — `project_completion_signal`'s own
  label (`unclear` / `settled` / `actively evolving` / `mostly
  settled`) is the only completion signal available today; a time
  estimate would need its own evidence base this project doesn't have
  yet, and isn't invented here.
- Does not use embeddings or any model to detect the idea-hop pattern
  — resolved in `SEMANTIC_RETRIEVAL_DECISION.md`: a plain count over
  existing timestamped events, matching this project's established
  "prove the simple approach insufficient before adding a dependency"
  discipline.
- Does not touch E4's emotional/behavioral signal — that stays scoped
  to one conversation at a time, per E4's own non-goals; this epic's
  "focus" signal is structural (events/relations), not linguistic.
