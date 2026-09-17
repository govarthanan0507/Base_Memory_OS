# IMPL-03 BRD — Project & File Intelligence

**Version:** 0.2

## Why this milestone exists

The user's actual work exists as many repositories, scripts, folders, downloads and generated artifacts. Conversation memory alone cannot reconstruct work continuity if the filesystem remains semantically unknown.

## Business/user problem

Memory OS must discover existing work without forcing manual folder cleanup. It must explain what a project appears to be, where it lives, what technologies and files it contains, and how artifacts relate to the project.

## Outcome

A read-only project and artifact intelligence layer that creates a semantic overlay on the filesystem while preserving original paths and evidence.

## Scope

- project-root discovery and boundary heuristics
- file/artifact registration
- code-file classification
- lightweight project structure analysis
- entrypoint and dependency-marker detection
- bounded project-state evidence such as test presence, TODO/FIXME counts and recent code activity
- project metadata and confidence
- repeatable, non-destructive rescans
- project↔conversation evidence links
- tests and versioned documentation

## Non-goals

- moving or renaming user files
- deleting files
- executing discovered project code
- claiming semantic understanding from filenames alone
- automatically declaring a project production-ready from structural evidence
- automatic cleanup of the filesystem
- destructive repository operations

## Success criteria

Given a workspace containing multiple projects, Memory OS can discover likely project roots, avoid a workspace-level README swallowing a stronger child project, register files as artifacts, attach artifacts to projects, and provide evidence-backed project metadata without modifying source files. Structural state evidence must remain explicitly evidence rather than a definitive project-status claim.
