# Requirements — personal-life-and-project-companion (V1: E1, E2)

Produced by: Product Owner (Planning), per `AGENTS/Product-Owner/AGENT.md`.

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
Cost ceiling inherited: $0 direct spend (FEASIBILITY_REPORT.md §2).
Source documents: documents/BUSINESS_CASE.md, FEASIBILITY_REPORT.md,
  MARKET_RESEARCH.md, PRE_MORTEM.md, AUDIT_REPORT.md,
  REPO_CANDIDATES.md, DECISION_CONTRACT.md, EPIC_SELECTION.md,
  ROADMAP.md, WHOLE_PRODUCT_VERDICT.md
```

## Design Council human gate — approval receipt

Both E1 (Tier 1) and E2 (Tier 3, full Council debate) design packages
were presented to the human gate and **approved as designed** — no
requested revisions to either. Per `COUNCILS/Design-Council/COUNCIL.md`'s
"silence is never approval" rule, this is an explicit approval record,
not an inferred one, given directly in this conversation.

The one condition carried forward is not a revision to either design —
it's the `WHOLE_PRODUCT_ARCHITECTURE_GATE.md` verdict's own named risk,
inherited into E1's story below (see E1-2's non-goal and constraint).

## Epic: E1 — Project Status & Re-entry Briefing

Traces to: `EPIC_SELECTION.md`'s E1 (MUST HAVE), extending
`continuity.py`'s `render_project_reentry_brief`/`project_context` and
`timeline.py`'s `project_timeline` (per `AUDIT_REPORT.md` — these
already exist and cover most of this epic's ground).

### E1-1

```text
As a returning user who has stepped away from a project
I want an accurate, up-to-date status briefing for that project when I ask
So that I don't have to reconstruct context from memory before I can resume work
```

**Priority**: Must Have (V1)

**Acceptance criteria**:
- [ ] Given a project with existing artifacts/relations/timeline data,
      when the user asks for that project's status, then the briefing
      reflects the current state of that data (no stale cache).
- [ ] Given a project with no recorded activity yet, when the user asks
      for its status, then the briefing says so plainly rather than
      returning an empty or misleading response.
- [ ] The briefing is generated on demand, from internal state only —
      nothing about project status is written back to disk as a
      separate document (per the inherited scope boundary above).

**Non-goals**: does not track relationships *between* different ideas/
projects — that is E3's territory, not this story's (see E1-2).

### E1-2

```text
As a user with several projects in flight
I want each project's briefing to include a completion/confidence signal
So that I can quickly see which projects need attention without inspecting each one in detail
```

**Priority**: Must Have (V1)

**Acceptance criteria**:
- [ ] Given a project with a mix of finished and open work, when its
      briefing is generated, then it includes a completion/confidence
      indicator derived from that project's own artifacts/timeline data
      (not a guess with no traceable basis).
- [ ] Given a project with too little data to compute a meaningful
      signal, then the briefing says the signal is unavailable rather
      than fabricating one.

**Constraint (from `WHOLE_PRODUCT_VERDICT.md`'s Finding 1 — required,
not optional)**: this story's "completion/confidence signal" is scoped
strictly to a single project's own internal state (its artifacts,
timeline, relation count). It must **not** implement any
idea-to-idea relationship or idea-hopping data shape — that concept
belongs to E3's future design (a semantic relation type on the
existing `relations` table). If, during implementation, a
completion/confidence signal turns out to genuinely require knowing
about idea-hops between projects, that requirement is not built
informally here — it is filed as a **CHANGE REQUEST** to the Product
Owner/Design Council naming the conflict with E3's territory, per
`COUNCILS/Design-Council/COUNCIL.md`'s post-handoff accountability
mechanism, rather than resolved silently.

**Non-goals**: idea-relationship tracking (E3), proactive/unprompted
notification of idea-hopping (E5) — this story is query-driven only.

## Epic: E2 — File & Code → Project Classification

Traces to: `EPIC_SELECTION.md`'s E2 (MUST HAVE), designed in full by
Design Council per `E2_HARD_CONSTRAINTS_PRECHECK.md`, `E2_DEBATE.md`,
`E2_FRD.md`, `E2_TRD.md`. Stories below restate `E2_FRD.md`'s
functional behavior and acceptance criteria as tickets — this does not
re-derive them, it packages them for the board per
`DEPARTMENTS/Developer_Organization/SHARED/AGILE_WORKFLOW.md`'s
one-ticket-per-story rule.

### E2-1

```text
As a user with files scattered across a folder like Downloads
I want to point the system at that folder and have it scan for files
So that every file in it gets registered and considered for project classification
```

**Priority**: Must Have (V1)

**Acceptance criteria**:
- [ ] Given a folder path named explicitly by the user, when the scan
      runs, then every file in it is registered as an artifact (name,
      location, content hash, type) — never a default/blanket scan of
      unspecified locations.
- [ ] Given a file the process cannot read (permission error), when
      the scan encounters it, then it is skipped with a logged reason
      at WARNING and the scan continues to the next file (per
      `E2_TRD.md`'s failure-behavior design).
- [ ] Given a symlink inside the designated folder whose resolved
      target falls outside that folder's root, when the scan
      encounters it, then it is skipped and logged at WARNING, never
      followed (per `E2_TRD.md`'s Security-Architect requirement).
- [ ] No file content or metadata is transmitted anywhere at any point
      (verifiable by absence of any networking import in the relevant
      module, per `E2_TRD.md`).

### E2-2

```text
As a user who just scanned a folder
I want the system to propose which existing project each new file most likely belongs to, with a confidence score
So that I don't have to manually sort files myself
```

**Priority**: Must Have (V1)

**Acceptance criteria**:
- [ ] Given a folder with files belonging to multiple existing
      projects, when the scan completes, then one candidate mapping
      per plausible artifact-project match is produced, each with a
      confidence score.
- [ ] Given a file with no textual hint of project affiliation, when
      scored against every existing project, then it is surfaced as
      "unclassified" rather than forced into a low-confidence guess.
- [ ] Content-snippet scoring is only attempted on text-readable files
      under the defined size cap (`MAX_HASH_BYTES`, per `E2_TRD.md`) —
      binary/oversized files are registered by metadata only.

### E2-3

```text
As a user reviewing proposed file-to-project mappings
I want to accept or reject each candidate mapping through the CLI
So that nothing gets linked to a project without my explicit confirmation
```

**Priority**: Must Have (V1)

**Acceptance criteria**:
- [ ] No artifact is linked to a project without an explicit accept —
      verified directly: a `relate()` call only ever occurs after a
      user-issued accept (per `E2_TRD.md`'s classification logic step
      4), never during the scan itself.
- [ ] Given the user accepts a candidate, when the acceptance is
      recorded, then a real, queryable link is created and visible in
      that project's status briefing (E1).
- [ ] Given the user rejects a candidate, when the rejection is
      recorded, then it is marked rejected, never deleted, and does
      not resurface unchanged on a later scan of the same,
      content-unchanged file.
- [ ] `memory-os review-artifact-candidate <candidate_id> <accept|reject>`
      mirrors the existing `review-candidate` command's shape, per
      `E2_TRD.md`'s integration points.

**Trace**: E1-1's briefing (E1) is the surface where E2-3's accepted
links become visible — E2 depends on E1 existing for this
observability, consistent with `ROADMAP.md`'s V1 grouping both
together with no epic-level dependency ordering required between them.

## Open items

None — both E1 and E2 stories above are fully resolved from
`idea.md`, `EPIC_SELECTION.md`, and E2's own Design Council package;
no business rule was invented to write these acceptance criteria.
