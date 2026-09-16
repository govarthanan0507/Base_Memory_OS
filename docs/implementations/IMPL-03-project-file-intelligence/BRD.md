# IMPL-03 BRD — Project & File Intelligence

**Version:** 0.1

## Why this milestone exists

The user's actual work exists as many repositories, scripts, folders, downloads and generated artifacts. Conversation memory alone cannot reconstruct work continuity if the filesystem remains semantically unknown.

## Business/user problem

Memory OS must discover existing work without forcing manual folder cleanup. It must explain what a project appears to be, where it lives, what technologies and files it contains, and how artifacts relate to the project.

## Outcome

A read-only project and artifact intelligence layer that creates a semantic overlay on the filesystem while preserving original paths and evidence.

## Scope

- project-root discovery
- project boundary detection
- file/artifact registration
- code-file classification
- lightweight project structure analysis
- entrypoint and dependency-marker detection
- project metadata and confidence
- repeatable, non-destructive rescans
- tests and documentation

## Non-goals

- moving or renaming user files
- deleting files
- executing discovered project code
- claiming semantic understanding from filenames alone
- automatic cleanup of the filesystem
- destructive repository operations

## Success criteria

Given a workspace containing multiple projects, Memory OS can discover likely project roots, register their files as artifacts, attach artifacts to projects, and provide evidence-backed project metadata without modifying source files.
