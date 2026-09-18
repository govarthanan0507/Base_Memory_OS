# Epic Selection — personal-life-and-project-companion

Produced by: Product Manager (Planning). Entry condition satisfied:
Pre-Planning verdict `GO`, all four documents present and complete
(`documents/BUSINESS_CASE.md`, `FEASIBILITY_REPORT.md`,
`MARKET_RESEARCH.md`, `PRE_MORTEM.md`), plus `AUDIT_REPORT.md`
(the mandatory existing-code audit) and `REPO_CANDIDATES.md`.

## PRE-PLANNING VERDICT RECEIVED

```text
Verdict: GO
Date / idea.md reference: 2026-09-18 / documents/idea.md
Path taken: FULL DEBATE
Scope boundaries inherited (verbatim from DECISION_CONTRACT.md):
  - Read-only file/folder access, scoped to user-designated folders
    — never blanket filesystem access.
  - Project status/documentation maintained internally, never
    written back to disk.
  - Code/file-to-project mapping is propose-then-confirm — never
    blind auto-mapping.
  - No commercial/distribution intent (CONFIRMED) — a personal-use
    ceiling, not a hypothetical to size for.
  - Not expected to be complete in V1 — an iterative process is the
    explicit expectation, stated directly by the user.
Cost ceiling inherited: $0 direct spend (FEASIBILITY_REPORT.md §2) —
  local-only, free/OSS components throughout.
Source documents: documents/BUSINESS_CASE.md, FEASIBILITY_REPORT.md,
  MARKET_RESEARCH.md, PRE_MORTEM.md, AUDIT_REPORT.md,
  REPO_CANDIDATES.md, DECISION_CONTRACT.md
```

## Epic decomposition

Applying the splitting discipline (INVEST pre-check, vertical slices,
multi-step/branching-rule patterns, estimation-spread sanity check):

### E1 — Project Status & Re-entry Briefing (extend, not build)

Ask "which projects am I working on and what's their status," get an
accurate answer. Per `AUDIT_REPORT.md`, `continuity.py`'s
`render_project_reentry_brief`/`project_context` and `timeline.py`'s
`project_timeline` already exist and do most of this — this epic
extends them (adds idea-hopping/completion-signal fields, doesn't
rebuild the mechanism). INVEST: independently valuable (answers a
real question today), small (extension, not new architecture),
testable against real project data.

### E2 — File & Code → Project Classification

Given an arbitrary file or code snippet, identify which project it
likely belongs to and propose that mapping via the existing
candidate-review state machine (`add_candidate`/`review_candidate`,
confirmed reusable per `AUDIT_REPORT.md`). Includes the read-only,
folder-scoped ingestion mechanism as part of this epic (a multi-step
process: scan designated folder → analyze file/code → propose
candidate → user confirms/rejects) rather than as a separate enabling
epic, since ingestion alone delivers no observable value without the
classification step it feeds. This is the one component
`REPO_CANDIDATES.md` confirms nothing existing fully covers — the
real, bounded new-build item named throughout Pre-Planning.

### E3 — Idea Relationship Tracking

Track idea-to-idea relationships (e.g. "idea B supports idea A"),
extending the existing generic `relations` table with a semantic
relation type for this specific case, surfaced through E1's briefing.
Small, INVEST-clean, depends on E1 existing to have somewhere to
surface in.

### E4 — Emotional/Behavioral Signal Extraction

Understand the user's emotional/behavioral state from conversation
transcript language alone (per `idea.md`'s explicit scope — no
separate mood-logging mechanism). Per `AUDIT_REPORT.md`, no existing
component covers this; `REPO_CANDIDATES.md`'s `OpenMemory` finding is
a design-pattern reference (multi-sector memory including an
emotional sector), not adoptable code as-is (low-visibility fork).
Genuinely new build, scoped to a bounded, well-defined signal
(behavioral state from language), not a general sentiment-analysis
platform.

### E5 — Proactive Focus Guidance

Surfaces idea-hopping as it happens and a per-project completion/
confidence signal, unprompted — the "guide me" layer the user
explicitly asked for. Depends on E1 (status data to reason over) and
E3 (relationship data — an idea-hop is only detectable relative to
existing ideas/projects) both existing first; this is a genuine
dependency, not an arbitrary sequencing choice, per the splitting
discipline's dependency check.

**Estimation-spread check**: each epic above, roughly sized, produces
a similar order-of-magnitude estimate spread whether reasoned about
by extension-cost (E1, E3) or new-build-cost (E2, E4, E5) — no further
splitting needed; E2 in particular was checked against being split
further (ingestion vs. classification vs. review-UI) and found to
fail the "Valuable" INVEST test if split that way, per the reasoning
above.

## Epic selection (`SHARED/EPIC_SELECTION_CRITERIA.md`'s 7 steps)

| Epic | Market check (Step 1) | Necessity (Step 2) | Constraint (Step 3) | Feasibility (Step 4) | Dependency (Step 5) | Confidence/Impact (Step 6) | Decision (Step 7) |
|---|---|---|---|---|---|---|---|
| **E1** Status & Re-entry | Not solved elsewhere as-is; largely already built here (`AUDIT_REPORT.md`) — adopting nothing, extending own code | Serves the core stated outcome directly | Fits ($0, read-only, no new hardware) | Pass — audit confirms low-risk extension | None — no dependency on other epics | High confidence (code already exists), high impact (core "where am I" question) | **MUST HAVE** |
| **E2** File/Code Classification | No candidate found fully covers this (`REPO_CANDIDATES.md`) — genuine gap, not duplicated effort | Serves the core stated outcome directly — named as the most important capability | Fits ($0, read-only, propose-then-confirm keeps risk bounded) | Pass, with the named unknown (real classification accuracy) carried forward per `PRE_MORTEM.md` | None blocking — reuses existing candidate pattern | Medium-high confidence (reuses proven pattern), high impact (the orphaned-file/abandoned-project problem named directly) | **MUST HAVE** |
| **E3** Idea Relationships | Not separately researched; low novelty (schema extension) | Serves a stated use case (idea-hopping structure), secondary to E1/E2 | Fits | Pass — small schema/logic addition | Depends on E1 (needs a briefing to surface into) | Medium confidence, medium impact | **SHOULD HAVE** |
| **E4** Emotional/Behavioral Signal | `OpenMemory`'s pattern is a reference, not adoptable as-is; no full match | Serves a stated use case, not the most emphasized one relative to E2 | Fits | Pass, but genuinely new/unproven work | None blocking, but naturally sequenced after E1/E2 prove the core loop | Lower confidence (unproven extraction quality), medium impact | **SHOULD HAVE** |
| **E5** Proactive Focus Guidance | No existing product does this combination (per both research passes) | Serves a stated use case, explicitly the most exploratory/least-specified one | Fits | Depends entirely on E1+E3 data existing and being reliable first | Depends on E1 and E3 (hard blocker, not soft preference) | Lowest confidence of the five (compound dependency), high potential impact once dependencies land | **COULD HAVE** |

## V1 release scope

```text
MUST HAVE:  E1 (Status & Re-entry), E2 (File/Code Classification)
SHOULD HAVE: E3 (Idea Relationships), E4 (Emotional/Behavioral Signal)
COULD HAVE: E5 (Proactive Focus Guidance)
WON'T HAVE (this release): none — nothing was found necessary to
  explicitly defer; the SHOULD/COULD labels already sequence the rest
```

This matches `idea.md`'s own explicit expectation — not complete in
V1, iterative. E1+E2 alone deliver real, observable value (an
accurate status answer, and the orphaned-file/code problem addressed)
using mostly-existing code for E1 and a bounded new build for E2.
E3/E4 extend naturally once E1/E2 are real. E5 is correctly the
farthest out — it has a genuine two-epic dependency, not just lower
priority.

## Handoff

Per `AGENTS/Product-Manager/AGENT.md`'s ownership: this finalized,
labeled epic list hands to the Product Owner
(`AGENTS/Product-Owner/AGENT.md`) next, for user-story/acceptance-
criteria detail on E1 and E2 first (the V1 MUST HAVEs).
