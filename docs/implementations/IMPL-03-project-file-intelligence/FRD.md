# IMPL-03 FRD — Project & File Intelligence

**Version:** 0.2

## Functional requirements

- FR-01 The system shall discover likely project roots from recognized repository/build/document markers.
- FR-02 The system shall avoid known generated/dependency/cache directories during discovery.
- FR-03 The system shall classify discovered files as code or general artifacts without executing them.
- FR-04 The system shall register artifact location, modification time, and content hash when safely bounded by size.
- FR-05 The system shall associate discovered artifacts with their containing project.
- FR-06 The system shall detect lightweight structural evidence including dependency markers, likely entrypoints, imports, and code-file counts.
- FR-07 The system shall record project-state evidence including README presence, test-file presence/count, bounded TODO/FIXME count, and recent code-file activity.
- FR-08 README-only workspace roots shall not suppress a stronger descendant project root; a Git repository root shall remain discoverable when it is itself the project boundary.
- FR-09 Rescanning an existing location shall update its project/artifact record rather than create duplicate locations.
- FR-10 Discovery shall be read-only with respect to the scanned filesystem.
- FR-11 Project confidence shall reflect available evidence and remain distinguishable from certainty.
- FR-12 Structural evidence shall not by itself assert production readiness or semantic project intent.

## Acceptance behavior

Given a workspace with a workspace-level README and a child project containing a dependency/repository marker, scanning selects the stronger child boundary rather than the README-only workspace. Given a code project with tests and TODO/FIXME markers, the project report records those as evidence. Running the scan again does not duplicate projects/artifacts by location, and no source file is modified.
