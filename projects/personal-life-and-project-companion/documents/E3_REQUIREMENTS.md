# Requirements — E3 (Idea Relationship Tracking)

Produced by: Product Owner, per `AGENTS/Product-Owner/AGENT.md`. Entry
condition satisfied: E3 carries a MoSCoW label (SHOULD HAVE) and
selection reasoning in `EPIC_SELECTION.md`.

## Tiering determination (`PROCESS_SCALING.md`)

**Tier 1 — solo/pair, no Council.** All four Tier 1 triggers hold:
- Touches exactly one domain (backend/data — no new UI surface; the
  existing `relate`/`reentry-project` CLI commands and `continuity.py`
  functions already cover the interaction shape).
- Reuses an existing pattern already established in the codebase:
  `MemoryStore.relate(source_id, relation, target_id)` already accepts
  any relation string — no schema change, no new table.
- Touches zero `HARD_CONSTRAINTS.md` categories (no money, no new
  dependency, no security-sensitive surface, no irreversible
  operation — a relation row is additive and reviewable).
- Easily reversible (a mis-recorded relation is just another `relate`
  call, or left as historical fact — nothing is deleted or migrated).

No Design Council debate, no `_HARD_CONSTRAINTS_PRECHECK.md`/
`_DEBATE.md`/`_FRD.md`/`_TRD.md` package — per `PROCESS_SCALING.md`'s
own Tier 1 process, this file is the complete requirement.

## Real gap this closes (found by reading the actual code, not assumed)

`continuity.py`'s `_entity()`/`_linked_entities()` already resolve a
relation between two *projects* correctly (tagged `kind="project"`) —
the generic relation mechanism already works end to end. But
`project_context()` only keeps `kind in {conversation, artifact,
memory}` from `_linked_entities()`'s output; a `kind="project"` link
is silently dropped, and `render_project_reentry_brief()` never shows
it. Recording "idea B supports idea A" via the existing `relate`
command already works — it just never surfaced anywhere.

## User story

```text
As a user tracking multiple, related ideas/projects
I want to record that one idea supports another, and see that relationship in either project's status briefing
So that I can understand how my ideas connect without holding it all in my head
```

**Priority**: Should Have (V2)

**Acceptance criteria**:
- [ ] Given two existing projects, when the user runs the existing
      `memory-os relate <project_a_id> supports <project_b_id>`
      command (no new CLI command — reuses what already exists), then
      that relation is recorded exactly as any other relation is.
- [ ] Given a project with a recorded `supports`/`supported_by`
      relation to another project, when that project's re-entry brief
      is rendered, then a new "## Related ideas" section lists the
      other project by name, with the relation's direction and type
      shown plainly (e.g. "supports Video Understanding" vs.
      "supported by Video Understanding").
- [ ] Given a project with no such relation, the section says so
      plainly ("No related ideas recorded") rather than being omitted
      silently — same "explicit absence, not silence" discipline
      every other section of the brief already follows.
- [ ] No new relation *type* is enforced by a schema constraint —
      `relate()`'s existing behavior (any non-empty relation string)
      is unchanged; `supports` is a documented convention this feature
      recognizes for direction-labeling, not a new CHECK constraint.

## Non-goals (explicitly, not smoothed over)

- Does not build a semantic-relation-type enum/CHECK constraint —
  `EPIC_SELECTION.md`'s "extending the... table with a semantic
  relation type" is satisfied by a documented convention (the string
  `"supports"`), not a schema change; a real need for stricter typing
  is a future decision, not assumed now.
- Does not add GUI wiring for creating a `supports` relation (no
  button/dialog in `gui.py`) — this pass is backend/CLI only, matching
  how E1/E2 phased backend-then-GUI. Surfacing existing relations in
  the GUI's chat brief comes for free (the GUI already renders
  whatever `render_project_reentry_brief` returns); *creating* one
  from the GUI is a separate, smaller follow-up if wanted.
- Does not implement E5's idea-hop *detection* (noticing a pattern
  across relations) — this epic only records and displays a single
  relation; E5 remains its own, later epic with its own dependency on
  this one existing first.
