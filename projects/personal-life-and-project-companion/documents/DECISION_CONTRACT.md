# Decision Contract — base-memory-os-personal-life-and-project-companion

Produced by: Synthesizer, from `BUSINESS_CASE.md`, `PRE_MORTEM.md`,
`FEASIBILITY_REPORT.md`, `MARKET_RESEARCH.md` (all present, all
non-empty — completeness gate satisfied). Supersedes the narrower
`pre-planning/base-memory-os-v1-hybrid-retrieval/DECISION_CONTRACT.md`
(preserved, not deleted).

## Fast-path status

Not fast-pathed — full debate, same reasoning as the prior cycle: the
scope is significant enough (four distinct capabilities, one novel)
to warrant the full four-role process, not a narrowed pass.

## Material disagreements and evidence used

Little real disagreement this cycle, unlike the v1 idea. Advocate,
Skeptic, Feasibility, and Market-Research converge: the combination
is genuinely not covered by any existing product (checked, not
assumed), three of its four pieces have real, adaptable reference
patterns, cost and hardware are non-issues, and the one real risk is
narrow and execution-specific (whether project-level file
classification reaches useful accuracy), not a reason to avoid
starting.

## Necessity verdict

**Necessary.** Unlike the prior narrower idea (where "necessary" was
answered but "build vs. adopt" stayed genuinely open), here both
questions point the same way: the underlying need is real and
specific to the user, and — checked directly this cycle — nothing
existing already meets it, so there is no adopt-instead-of-build
alternative to evaluate first.

## Shipping/distribution intent

**CONFIRMED**, not inferred: the user stated directly, in this
conversation, that this is a personal tool intended to run
indefinitely on their own machine, with the specific reason being
that it needs deep read authority over their own files — an
authority they are not willing to extend to anything beyond their own
local system. No commercial or distribution intent exists. Per
`SHARED/REUSE_AND_LICENSE_RULE.md`, this means the AGPL-3.0 finding on
AI File Sorter (recorded in `MARKET_RESEARCH.md` §4) does not block
anything today — it stays on record to resurface only if this intent
ever changes.

## Answering the user's original questions, updated for the real scope

- **Is it necessary?** Yes — see verdict above, stronger than the
  narrower idea's answer.
- **Cost?** $0 direct spend; time cost concentrated in one piece
  (file classification), not spread evenly.
- **Hardware?** Unchanged from the narrower idea's finding: ~4GB RAM,
  CPU-only, no GPU, for the local embedding component. No new
  hardware category introduced by the emotional-memory or file-
  classification pieces.
- **Shipping plans?** None — confirmed directly, not inferred, this
  cycle.
- **What else covers this?** MemPalace (retrieval), Graphiti (temporal
  state), OpenMemory (emotional memory) each cover one piece and are
  real adopt/study candidates. Nothing found covers project-level
  file/code classification specifically — checked directly (AI File
  Sorter, the closest match, does only generic category sorting).

## Verdict

**GO**

## Reasoning for verdict

Necessity is confirmed, the market gap is real and checked (not the
user's unverified impression), cost and hardware are non-issues, and
the one genuine unknown (file-classification accuracy) is exactly the
kind of thing this idea's own propose-then-confirm safety net — and
the user's own explicitly stated "not expecting this finished in V1,
an iterative process" framing — already exists to absorb. This does
not meet the bar for `NEEDS MORE EVIDENCE`: the missing evidence in
the prior cycle (evaluate the near-total match before building) has
no equivalent here, since no near-total match exists to evaluate.

**Sequencing note for the next stage** (not a blocking condition on
this verdict, but a real risk named by the Skeptic worth carrying
forward): Epic Selection should scope the three pattern-adaptable
pieces (retrieval, temporal state, emotional memory) and a *bounded*
first attempt at file classification separately, rather than treating
file-classification accuracy as a gate the whole idea waits on.

## Explicit missing evidence

None blocking this verdict. Carried forward as a build-time (not
pre-build) unknown: real classification accuracy against the user's
actual messy data, which can only be observed once built, not
estimated further in advance.

## Human-gate status

**Pending** — presented to the user via the same short-verdict,
advocacy-checkpoint mechanism as the prior cycle, per `COUNCILS/
Pre-Planning/COUNCIL.md`'s Human gate section.

---

### Addendum — 2026-09-18, GO verdict confirmed against additional evidence

The user provided a second, independent raw transcript (a parallel
conversation with a different AI, handed over in full — not a
summary) exploring the same idea. That transcript's own research
converged on largely the same conclusion this cycle already reached:
compose several existing pieces rather than adopt one, no single
project covers the combination. This session independently verified
four additional named candidates from that transcript (`Basic
Memory`, `PMB`, `Cognee`, `Persona` — recorded in the new
`REPO_CANDIDATES.md`), correcting one framing error along the way
(`Persona` depends on OpenAI's API for its LLM calls and is not
local-first, contrary to how the other transcript described it).

**This does not change the verdict.** `PMB` came closest of any
candidate found across either research pass to the still-open gap
(project-level file/code classification), but even it appears scoped
to indexing a codebase already pointed at, not classifying an
unsorted file against many candidate projects — the gap named in
`PRE_MORTEM.md` stands, not weakened or strengthened materially.

**GO stands**, on the same reasoning as the original verdict above.
This addendum exists per this project's own preserve-history
convention — the original verdict is left as written, not edited,
per `SHARED/DOCUMENT_GOVERNANCE.md`.
