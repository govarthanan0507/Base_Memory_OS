# Requirements — E4 (Emotional/Behavioral Signal Extraction)

Produced by: Product Owner + a short Tier 2 design pass (Backend-
Architect, Data-Architect), per `PROCESS_SCALING.md`.

## Tiering determination

**Tier 2 — small crew, short design note, no full debate.** Not
Tier 1: this is a genuinely new build (no existing pattern to reuse
directly), and `WHOLE_PRODUCT_VERDICT.md` explicitly named it as an
open feasibility question, not a settled extension — `PROCESS_SCALING.md`'s
own rule is to default one tier up when genuinely ambiguous. Not
Tier 3: it stays within one domain (backend/text-processing), resolves
to zero new dependency (`E4_HARD_CONSTRAINTS_PRECHECK.md`), and
touches only one Hard Constraint category. Backend-Architect and
Data-Architect reviewed; no disagreement arose, so the full
Synthesizer/Independent-Critic debate machinery was not invoked, per
`PROCESS_SCALING.md`'s Tier 2 process.

## Design note

**Backend-Architect**: A small, built-in lexicon (frustration/
negative cue words, positive/momentum cue words) matched against a
conversation's message text, case-insensitive substring/word
matching — no NLP library, no model download. Score = (matched
negative cues − matched positive cues) normalized by message count;
label derived from the score's sign/magnitude
(frustrated / neutral / positive), with the actual matched cue words
returned alongside the label — not a black-box score, so the
signal's basis is always inspectable (matches this project's
evidence-over-assertion discipline, applied to a heuristic instead of
a claim).

**Data-Architect**: No new table. Per `idea.md`'s own explicit
constraint ("no separate mood-logging mechanism"), the signal is
computed on demand from the existing `messages`/`conversations`
tables — nothing new is persisted. Consistent with E1's own
on-demand-computation pattern (`render_project_reentry_brief` recomputes
live every call).

## User story

```text
As a user reviewing a past conversation
I want to see a behavioral/emotional signal extracted from that conversation's own language
So that I have an honest, inspectable read on my state at the time, without a separate mood-tracking step
```

**Priority**: Should Have (V2)

**Acceptance criteria**:
- [ ] Given a conversation with clearly frustrated language (e.g.
      "stuck", "this is broken", "ugh"), when the signal is extracted,
      then the label is `frustrated` and the matched cue words are
      returned alongside it.
- [ ] Given a conversation with clearly positive language (e.g.
      "finally works", "great progress"), then the label is `positive`.
- [ ] Given a conversation with neither, then the label is `neutral`
      rather than a forced guess.
- [ ] Given a conversation with no messages, the signal says so
      explicitly (`unavailable`) rather than defaulting to `neutral`
      as if it had evidence.
- [ ] Nothing about this feature writes a new record anywhere —
      verifiable directly by absence of any new `INSERT`/`add_*` call
      in the implementing module.

## Non-goals (explicitly, not smoothed over)

- Does not aggregate a signal across multiple conversations into a
  per-project rollup — that combination (project-level guidance) is
  E5's territory, which has its own explicit dependency on this epic
  existing first, not this epic's job to pre-build.
- Does not use embeddings, a sentiment-analysis library, or any cloud
  call — resolved explicitly in `E4_HARD_CONSTRAINTS_PRECHECK.md`, not
  left implicit. If real usage later shows the lexicon approach is too
  shallow, upgrading is a future decision made with actual evidence,
  not assumed necessary now.
- Does not claim clinical or definitively accurate emotion detection —
  `FEASIBILITY_REPORT.md`'s own risk acknowledgment stands: this is
  guidance, a wrong read is a bad suggestion, not corrupted data.
