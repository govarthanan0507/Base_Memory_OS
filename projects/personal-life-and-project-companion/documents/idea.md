# idea.md — base-memory-os-personal-life-and-project-companion

**Supersedes**: `ingestion/base-memory-os-v1-hybrid-retrieval/idea.v1.md`
(preserved, not deleted, per `SHARED/DOCUMENT_GOVERNANCE.md`). That
version was built from a *summary* of a discussion with another
session, not the raw transcript — the summary silently dropped
explicit user instructions (naming Graphiti and MemPalace as adopt
candidates, "adapt, don't build from scratch"). Caught live during
Pre-Planning's human advocacy checkpoint (`COUNCILS/Pre-Planning/
COUNCIL.md`'s Human gate), when the user advocated for their idea
against the v1 verdict. Root cause and fix, per the user directly:
future input will be raw `.md` conversation transcripts, not
summaries.

## Idea summary

WHAT THE USER SAID (direct, this conversation, not inferred): not
"better search" — a local-first system that builds a real, ongoing
model of the user across **both work projects and personal life**,
using conversation transcripts as its evidence source, that proactively
helps the user manage a tendency to rapidly hop between many
overlapping ideas and projects, some abandoned partway through.

## Problem

WHAT THE USER SAID: the user has a "hyperactive brain" — many parallel
projects and sub-ideas (idea B often exists specifically to support
idea A), frequent context-switching between them, and a real pattern
of dropping a project at ~75% completion. Code and files from these
projects end up scattered and orphaned, especially in a messy
Downloads folder, with nothing that automatically figures out which
project a given file or piece of code actually belongs to. The
existing system (V0) only offers keyword search — no cross-project
awareness, no emotional/behavioral modeling, no proactive guidance.

## Target user

The user themselves — a personal, single-user, local-first tool, not
a multi-tenant product. (Same as v1's target user; unchanged by this
correction.)

## Intended outcome

WHAT THE USER SAID: a system that knows the user's full project
landscape and behavioral/emotional patterns well enough to proactively
help them focus and finish things, rather than one more place the user
has to manually organize.

## Use cases (all direct from this conversation)

1. Ask "which projects am I working on and what's their status" and
   get an accurate answer without manually searching.
2. Hand it an arbitrary piece of code or a file from the Downloads
   folder; it identifies which project it belongs to and **proposes**
   that mapping as a candidate for the user to confirm or correct —
   never applies it blindly. This reuses `base_memory_os`'s own
   existing IMPL-01/02 candidate-review pattern directly, not new
   architecture.
3. Track idea-to-idea relationships (e.g. "idea B supports idea A"),
   not just a flat list of unrelated projects.
4. Proactively flag rapid idea-hopping as it happens (not just when
   asked), and surface a per-project completion/confidence signal
   (how many active projects, how much of each is done, roughly how
   much time is needed to finish) — a focus aid, not just a report.
5. Understand the user's emotional/behavioral state (e.g. frustration)
   purely from the language used in conversation transcripts — no
   separate mood-logging mechanism.

## Known assumptions (explicitly marked)

- ASSUMED, per the user's direct statement: Graphiti and MemPalace are
  real adopt/adapt candidates — **the user proposed these by name in
  the original conversation with another session; CodeFoundry did not
  discover them independently.** The v1 Ingestion pass found them via
  its own market check without knowing the user had already named
  them — the two lines of evidence agree, which is worth noting, but
  the user's own prior naming of them is the primary fact here, not a
  coincidence to attribute to this system's research.
- ASSUMED: file/code access should be **read-only**, scoped to specific
  folders the user designates (e.g. Downloads, a conversations/code
  folder) — not blanket filesystem access. Stated directly by the
  user, and reasoned from a concrete, just-observed risk (a summary
  in this very conversation silently lost real content; write access
  to real files carries the same risk with on-disk consequences).
- ASSUMED: project status/documentation is maintained **internally**
  (queryable, conversational) — never written back to disk as files,
  for the same read-only reasoning above.
- ASSUMED: **not expected to be complete in V1.** The user stated this
  directly — an iterative, improving process over time is the actual
  expectation, not a one-shot finished product.

## Known uncertainties

- UNKNOWN, explicitly not yet resolved: whether the user's own claim
  ("I don't think any product does this level of file/code-to-project
  retrieval combined with personal-life memory") actually holds. This
  is a real, honest claim, not dismissed — but it has not yet been
  checked with a fresh market search against this specific, fuller
  combination. The v1 Ingestion pass's Market-Research findings
  (MemPalace, Graphiti) were scoped to conversational memory and
  temporal-fact handling specifically — not to autonomous code/file-
  to-project classification or combined emotional+project modeling.
  This is the next required step, not something to assume either
  direction.

## Scope signals

- Personal, local-first, intended to run indefinitely ("forever," per
  the user directly) — CONFIRMED, not inferred, this time: the reason
  given is specific (deep read authority over the user's own files
  should never leave the user's machine), not just a vague hobby-
  project framing.
- No stated commercial/distribution intent — CONFIRMED directly in
  this conversation (the user frames this entirely as their own tool).

## WHAT THE NEXT STAGE MUST DO

1. Run a fresh Market-Research pass specifically against the combined,
   real scope (autonomous code/file-to-project classification +
   emotional/behavioral modeling + project-relationship tracking) —
   not reuse the v1 pass's narrower findings as if they already
   answered this.
2. Re-run the full Pre-Planning cycle (all four roles + Synthesizer)
   against this corrected `idea.md`.
3. Per `SHARED/EXISTING_CODE_AUDIT_GATE.md`, the existing-code audit
   still applies once Pre-Planning clears — this idea builds on
   `base_memory_os`'s current code, same as v1.
4. Present the verdict via the same human-advocacy-checkpoint
   mechanism (`COUNCILS/Pre-Planning/COUNCIL.md`'s Human gate) — a
   short plain verdict, not a document dump, with room for the user
   to advocate again if needed.

## Status

**CLEAR WITH OPEN ITEMS** — the vision itself is now unambiguous and
directly confirmed with the user, not inferred. Open item: the fresh
market check named above, required before any verdict.
