# Decision record — semantic/embedding-based retrieval (superseded, not silently dropped)

## What was found

`FEASIBILITY_REPORT.md`/`DECISION_CONTRACT.md` (Pre-Planning, GO
verdict) assumed a local embedding component (a model like
`nomic-embed-text` via Ollama) as part of this product's hardware
requirements, framed around MemPalace's/Graphiti's semantic-retrieval
patterns. `EPIC_SELECTION.md`'s actual epic decomposition (E1-E5)
never turned this into a built epic — every subsequent epic (E2, E4,
now E5) independently chose a zero-dependency heuristic instead,
without anyone flagging the mismatch against the approved plan. This
was raised directly with the user as a real gap, not assumed either
way.

## Decision

**Superseded, not built, on the user's explicit direction.** Given a
`test it and see if it's good first` posture, and given this exact
codebase's own repeated precedent (E2_DEBATE.md's heuristic-over-
embeddings call, E4_HARD_CONSTRAINTS_PRECHECK.md's same reasoning),
introducing Ollama now — a new runtime dependency, a new hardware
assumption, a new architectural pattern (Category 9/12 in
`HARD_CONSTRAINTS.md`) — is not justified without first observing
whether the already-built heuristic approaches (E2's structural
classification, E4's lexicon, E5's counting) actually prove
insufficient in real use.

**This is a real decision, recorded so it is not silently lost
again**: `FEASIBILITY_REPORT.md`'s embedding-component hardware
assumption is explicitly superseded for this product as currently
scoped. If real usage later shows keyword-only search
(`memory_fts`) or the heuristic signals are genuinely insufficient,
reopening this is a new, evidence-backed Design Council pass — not
an assumption to silently carry forward or silently drop a second
time.

## Status

No epic (E6 or otherwise) created for this. `EPIC_SELECTION.md`
remains E1-E5 as already decomposed; no ROADMAP.md change needed.
