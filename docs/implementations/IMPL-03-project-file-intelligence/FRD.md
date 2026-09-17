# IMPL-03 FRD — Project & File Intelligence

**Version:** 0.3

## Functional requirements

- FR-01 The system shall discover likely project roots from recognized repository/build/document markers.
- FR-02 The system shall avoid known generated/dependency/cache directories during discovery.
- FR-03 The system shall classify discovered files as code or general artifacts without executing them.
- FR-04 The system shall register artifact location, modification time, and content hash when safely bounded by size.
- FR-05 The system shall associate discovered artifacts with their containing project.
- FR-06 The system shall detect lightweight structural evidence including dependency markers, likely entrypoints, imports, and code-file counts.
- FR-07 The system shall record project-state evidence including README presence, test-file presence/count, bounded TODO/FIXME count, and recent code-file activity.
- FR-08 README-only workspace roots shall not suppress stronger descendant project roots; nested strong project roots shall remain independently discoverable.
- FR-09 A parent project scan shall not attribute artifacts belonging to a selected nested project to the parent.
- FR-10 Rescanning an existing location shall update its project/artifact record rather than create duplicate locations.
- FR-11 Artifact rescans shall preserve append-only change evidence including old/new hashes and modification timestamps.
- FR-12 The system shall expose current project evidence, historical evidence, explicit continuity and current artifacts as separate view sections.
- FR-13 Project↔conversation linking shall validate entities and resolve provider external conversation IDs to canonical internal IDs.
- FR-14 Discovery shall be read-only with respect to the scanned filesystem.
- FR-15 Project confidence shall reflect available evidence and remain distinguishable from certainty.
- FR-16 Structural evidence shall not by itself assert production readiness, code quality or semantic project intent.

## Acceptance behavior

Given a workspace with a workspace-level README and child projects containing stronger repository/dependency markers, scanning retains the selected nested boundaries and isolates child artifacts. Given a code project with tests and TODO/FIXME markers, the project record exposes those as evidence. Repeated scans do not duplicate locations and changed artifacts retain historical evidence. Explicitly linked conversations appear in project continuity/evidence views. No source file is moved, renamed, deleted or executed by discovery.
