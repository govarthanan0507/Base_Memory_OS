# Technical Requirements — E2 (File & Code → Project Classification)

Per `E2_DEBATE.md`'s synthesis. No frontend/API-contract sections —
this is a local CLI extension to an existing local-first tool, no
client/server boundary exists or is introduced.

## Architecture overview and decisions

Reuses `discovery.py`'s existing `Artifact`/`MemoryStore.add_artifact`
for registration. Does **not** reuse `scan_workspace`'s auto-`relate()`
call for this feature — that call auto-links with no confirmation,
which conflicts with this idea's propose-then-confirm requirement
(see `AUDIT_REPORT.md`'s correction). A new function,
`classify_artifacts_against_projects`, is added to `discovery.py`
(or a new sibling module, `project_classification.py`, if
`discovery.py` grows too large — a Development-time judgment call,
not an architectural one) for this specific case.

**Rejected alternative**: embedding-based similarity matching.
Rejected for V1 to avoid a new dependency without first proving the
simpler heuristic approach insufficient (Hard Constraint #9,
`E2_HARD_CONSTRAINTS_PRECHECK.md`) — named as a real option for a
later version if heuristic accuracy proves too low in practice, not
dismissed permanently.

## Data model

New table, additive-only migration (`CREATE TABLE IF NOT EXISTS`, no
alteration to any existing table):

```sql
CREATE TABLE IF NOT EXISTS artifact_project_candidates (
    candidate_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
    status TEXT NOT NULL CHECK(status IN ('candidate', 'accepted', 'rejected')),
    observed_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(artifact_id, project_id)
);
```

Mirrors `memory_candidates`'s exact shape and `CHECK`-constraint
discipline (Data-Architect's proposal, per `E2_DEBATE.md`). The
`UNIQUE(artifact_id, project_id)` constraint is what satisfies
`E2_FRD.md`'s acceptance criterion that a rejected candidate doesn't
resurface unchanged — a re-scan re-uses `INSERT OR REPLACE` against
this key, only producing a new row when the artifact's content hash
actually changes (same re-import-merges-richer-evidence pattern
`conversation.py` already uses).

## Classification logic

1. For each newly-registered (or content-changed) artifact, tokenize
   its filename, containing folder name, and — only for text-readable
   files under a size cap (reuse `discovery.py`'s existing
   `MAX_HASH_BYTES` constant as the cap, per Security-Architect's
   accepted refinement in `E2_DEBATE.md`) — a content snippet.
2. Score against each existing project's name, root path, and any
   artifact/relation already linked to it, using the same additive-
   weighted-signal shape `inspect_project` already uses for its own
   confidence score (Architect's finding — reuse the pattern, don't
   invent a new one).
3. Any score above a floor threshold produces a row in
   `artifact_project_candidates` with `status: candidate`. No score
   above the floor for any project → the artifact is left
   unclassified (`E2_FRD.md` #6) — no row is forced.
4. On user accept: `status → accepted`, and a real `relations` row is
   written (`relate(project_id, "contains", artifact_id)`) — this is
   the one place `relate()` is called for this feature, and only
   after explicit confirmation.
5. On user reject: `status → rejected`. Never deleted.

## Security and reliability considerations

Per `E2_DEBATE.md`'s Security-Architect findings, all three carried
in as explicit requirements, not left implicit:

1. **Symlink scope containment**: when walking a designated folder,
   any symlink whose resolved target falls outside that folder's
   resolved root is skipped, not followed — logged at WARNING, not
   silently ignored.
2. **No binary content reads**: content-snippet extraction only
   attempts on files identified as text (by extension/MIME sniff,
   reusing whatever check `discovery.py`'s existing `CODE_EXTENSIONS`
   set already establishes as precedent), and only up to the size cap
   named above. Binary/oversized files still get registered as
   artifacts (name/path/hash/type) — just no content-based signal.
3. **Fully local**: no artifact content or metadata is transmitted
   anywhere. No network call exists anywhere in this feature's code
   path — verifiable directly by the absence of any networking import
   in the relevant module(s), a concrete QA check, not just a stated
   intent.

## Failure behavior (per the Independent Critic's resolved finding)

A permission error or other `OSError` on any single file during the
scan is caught, logged at WARNING with the specific path and reason
(reusing `logging_setup.py`), and the scan continues to the next file
— it never aborts the whole scan for one unreadable file. This
satisfies `E2_FRD.md`'s acceptance criterion directly.

## Integration points

CLI: two new subcommands, following `cli.py`'s existing dispatch
pattern exactly (inherits F-01/F-02's centralized error handling and
logging for free, no new error-handling code needed):
- `memory-os classify-folder <path>` — runs the scan + classification,
  reports how many candidates were produced and how many artifacts
  were left unclassified.
- `memory-os review-artifact-candidate <candidate_id> <accept|reject>`
  — mirrors the existing `review-candidate` command's shape exactly.

No hosting/platform decision needed — this is a local CLI addition to
an already-local tool; no new environment, no deployment change.
