# IMPL-03 BRD — Project & File Intelligence

**Version:** 0.3

## Why this milestone exists

The user's actual work exists as many repositories, scripts, folders, downloads and generated artifacts. Conversation memory alone cannot reconstruct work continuity if the filesystem remains semantically unknown.

## Business/user problem

Memory OS must discover existing work without forcing manual folder cleanup. It must explain what a project appears to be, where it lives, what technologies and files it contains, how artifacts change over time, and how explicitly connected conversations contribute to project continuity.

## Outcome

A read-only project and artifact intelligence layer that creates a semantic overlay on the filesystem while preserving original paths, provenance and historical evidence.

## Scope

- project-root discovery and boundary heuristics;
- nested strong-project/monorepo boundary preservation;
- file/artifact registration and bounded hashing;
- code-file classification;
- lightweight project structure analysis;
- entrypoint and dependency-marker detection;
- bounded project-state evidence such as test presence, TODO/FIXME counts and recent code activity;
- Git branch/HEAD evidence;
- append-only artifact change history;
- project timeline integration;
- project↔conversation evidence links;
- compact evidence-labelled project views;
- repeatable, non-destructive rescans; and
- tests and versioned documentation.

## Non-goals

- moving or renaming user files;
- deleting files;
- executing discovered project code;
- claiming semantic understanding from filenames alone;
- automatically declaring a project production-ready from structural evidence;
- automatic filesystem cleanup;
- destructive repository operations; or
- silently guessing project↔conversation ownership.

## Success criteria

Given a workspace containing multiple projects, Memory OS can discover likely project roots, preserve legitimate nested project boundaries, register files as artifacts, track artifact changes, attach artifacts to projects, expose explicit conversation continuity, and provide evidence-backed project views without modifying source files. Structural state evidence remains explicitly evidence rather than a definitive project-status claim.
