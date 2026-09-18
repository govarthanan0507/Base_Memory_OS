# Functional Requirements — E2 (File & Code → Project Classification)

Technology-agnostic — what the system does, observable from the
user's side. No UI/visual direction section: `CODE_DIGEST.md` and
this idea's own scope confirm no UI exists or is planned; this is a
CLI-only capability.

## Functional behavior

1. User points the system at a designated folder (e.g. Downloads, a
   code folder) via a CLI command, naming that folder explicitly —
   never a default/blanket scan.
2. The system reads that folder read-only, registering each file/code
   item found as an artifact (name, location, content hash, type).
3. For each newly-registered artifact, the system proposes which
   existing project it most likely belongs to, with a confidence
   score — never applies the mapping automatically.
4. The user reviews proposed mappings (accept/reject), one at a time
   or as a batch, through the CLI — same review pattern already used
   for memory candidates.
5. An accepted mapping becomes a real, queryable link between the
   artifact and the project (visible in that project's status/
   re-entry output, E1). A rejected mapping is recorded as rejected,
   not deleted — same "nothing overwritten" discipline used
   throughout this codebase.
6. Files the system can't confidently place against any existing
   project are surfaced as "unclassified," not silently dropped and
   not forced into a low-confidence guess.
7. Unreadable files (permission errors, etc.) are skipped with a
   logged reason; the scan continues rather than aborting.

## Acceptance criteria (traces to `EPIC_SELECTION.md`'s E2)

- Given a folder with files belonging to multiple existing projects,
  running the scan produces one proposed candidate per plausible
  artifact-project match, each with a confidence score.
- No artifact is linked to a project without an explicit accept.
- A rejected candidate does not resurface as a new proposal on a
  later scan of the same file (unless the file's content actually
  changes — same re-import-merges-richer-evidence pattern already
  used for conversations).
- A folder containing at least one permission-denied file still
  completes the scan for every other file in it.
- No file content or metadata leaves the local machine at any point.

## Design risks and unresolved issues (not smoothed over)

- Real classification accuracy against the user's actual messy data
  is unknown until tried — named explicitly in `PRE_MORTEM.md` and
  `AUDIT_REPORT.md`, unchanged by this design pass. The propose-then-
  confirm mechanic is the mitigation, not a guarantee of accuracy.
- The heuristic (token-matching) approach may under-perform on files
  with no textual hint of their project (e.g. a generically-named
  binary) — these correctly surface as "unclassified" per functional
  behavior #6, rather than a wrong guess, but that means real recall
  on hard cases is intentionally traded for avoiding false positives.
