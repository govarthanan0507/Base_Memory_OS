# Design Council Debate — E2 (File & Code → Project Classification)

Roles convened: Architect, Backend-Architect, Data-Architect,
Security-Architect (per Ingestion Mode C's finding — no UI exists or
is planned; Frontend/UI/UX roles not convened).

## Positions

**Backend-Architect**: Propose reusing `discovery.py`'s `Artifact`/
`add_artifact` primitives for registering scanned files — proven,
tested, no reason to duplicate. For classification itself, propose a
heuristic matcher: tokenize the artifact's filename, containing
folder name, and (for text-readable files under a size cap) a content
snippet, then score against each existing project's name, root path,
and any artifact/relation already linked to it. No embeddings, no
LLM call — keeps this at zero new dependencies for V1.

**Data-Architect**: Agrees with reusing `Artifact`/`add_artifact`.
Disagrees on where classification results land: `scan_workspace`'s
existing pattern (`store.relate(pid, "contains", aid)`) auto-links
with no confirmation — confirmed by direct read this pass, and a real
conflict with `idea.md`'s propose-then-confirm requirement (recorded
as a correction in `AUDIT_REPORT.md`). Proposes a new table,
`artifact_project_candidates` (`artifact_id`, `project_id`,
`confidence REAL CHECK(0-1)`, `status CHECK(candidate/accepted/
rejected)`, `observed_at`, `metadata_json`) — same shape and same
`CHECK`-constraint discipline as the existing `memory_candidates`
table, additive-only migration, no rollback complexity since nothing
existing is altered.

**Security-Architect**: Three findings, each reasoned from this
product's actual deployment (local-only, single user, personal
files), not a generic checklist:
1. Symlinks inside a designated scan folder must not be followed to a
   location *outside* that folder — otherwise the read-only/
   folder-scoped boundary (`idea.md`'s own constraint) is silently
   bypassed by a symlink pointing elsewhere. Real, specific attack
   surface for this product: a stray symlink in Downloads (common —
   many installers create them) could otherwise leak scope.
2. Binary/oversized files must not have their content read for
   classification — only metadata (name, path, size, type) and, for
   text-readable files under a size cap, a snippet. Reasoning: this
   product's whole premise is trust ("full authority to read deep
   into documents") — reading arbitrary binary content adds risk
   (resource exhaustion on a huge file, no classification value from
   binary bytes) with no offsetting benefit.
3. Everything stays local — no content or metadata from this scan is
   ever sent anywhere, reinforcing Backend-Architect's zero-new-
   dependency, no-cloud-LLM proposal. Not a new decision, a
   confirmation that the *architecture* actually delivers on the
   privacy boundary already promised, not just the policy on paper.

**Architect**: Notes the confidence-scoring pattern Backend-Architect
proposes (heuristic token matching) already has precedent in this
exact codebase — `discovery.py`'s `inspect_project` computes a
confidence score from weighted signals (code presence, README
summary, markers, entrypoints) the same way. Proposes reusing that
same additive-scoring shape for artifact-to-project confidence,
rather than inventing a different scoring mechanism.

## Challenges

**Backend-Architect → Data-Architect**: A new table adds a join for
every classification query. Data-Architect's response: **defend** —
the existing `memory_candidates` table already accepts this same
tradeoff for the same reason (a clean state machine with a `CHECK`
constraint is worth one join); consistency with the established
pattern outweighs the marginal query cost at this product's actual
scale (single user, not a high-QPS service).

**Security-Architect → Backend-Architect**: The content-snippet read
(for text files) still needs a defined size cap and a defined "is
this text-readable" check — an unbounded read on a disguised file
(e.g. a huge text file with a misleading small-looking name) could
still cause the resource-exhaustion problem finding 2 raises.
Backend-Architect's response: **accept** — adds an explicit cap
(matching the existing `MAX_HASH_BYTES` pattern already used in
`discovery.py` for content hashing) to the TRD below, rather than
leaving it as an implementation detail for Development to invent
(per this role's own Rule 3).

## Synthesis

- Reuse `Artifact`/`add_artifact` for registration (no disagreement).
- New table `artifact_project_candidates`, mirroring
  `memory_candidates`'s shape (Data-Architect's proposal, Backend-
  Architect's join-cost challenge accepted as a worthwhile tradeoff,
  same reasoning already applied to the existing table).
- Heuristic, no-new-dependency classification (Backend-Architect's
  proposal), using the same additive confidence-scoring shape already
  proven in `inspect_project` (Architect's finding) — **rejected
  alternative**: embedding-based similarity, rejected for V1
  specifically to avoid a new dependency (Hard Constraint #9) without
  first proving the simpler approach is insufficient; recorded as a
  named option for a future version if heuristic accuracy proves too
  low in practice.
- Symlink-scope-escape prevention, binary/oversized-content
  exclusion, and a defined size cap for content snippets (Security-
  Architect's findings, with Backend-Architect's accepted refinement)
  — all three carried into `TRD.md` as explicit design requirements,
  not left implicit for Development.

## Independent Critic

Reviewed the synthesized design fresh. One finding: **the synthesis
does not address failure behavior for a folder scan that encounters a
permission error partway through** (a real, likely scenario — a
Downloads folder often has files a normal user process can't read).
Does the whole scan abort, or does it skip and continue?

**Resolution**: skip and continue, logging a WARNING per-file (reusing
`logging_setup.py`'s existing pattern from the F-01/F-02 fix cycle) —
a partial scan of a messy real folder is expected and useful; aborting
on the first unreadable file would make this feature nearly useless
against the actual mess `idea.md` describes. Added to `TRD.md`
explicitly, closing the Critic's finding — not carried forward as an
open risk.

## Hard Constraint #9 resolution (from the pre-check)

**No new third-party dependency required.** The synthesized design
uses only Python's standard library (`os.walk`/`pathlib`, matching
`discovery.py`'s existing pattern) plus the existing `MemoryStore`.
This closes category 9 from `E2_HARD_CONSTRAINTS_PRECHECK.md` without
needing to route to the human — nothing was silently decided; the
category was checked and the answer is "not triggered."
