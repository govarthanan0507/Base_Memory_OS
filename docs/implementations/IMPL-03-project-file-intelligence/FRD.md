# IMPL-03 FRD — Project & File Intelligence

**Version:** 0.1

## Functional requirements

- FR-01 The system shall discover likely project roots from recognized repository/build/document markers.
- FR-02 The system shall avoid known generated/dependency/cache directories during discovery.
- FR-03 The system shall classify discovered files as code or general artifacts without executing them.
- FR-04 The system shall register artifact location, modification time, and content hash when safely bounded by size.
- FR-05 The system shall associate discovered artifacts with their containing project.
- FR-06 The system shall detect lightweight structural evidence including dependency markers, likely entrypoints, imports, and code-file counts.
- FR-07 Rescanning an existing location shall update its project/artifact record rather than create duplicate locations.
- FR-08 Discovery shall be read-only with respect to the scanned filesystem.
- FR-09 Project confidence shall reflect available evidence and remain distinguishable from certainty.

## Acceptance behavior

Given a workspace with two code projects and unrelated files, scanning discovers the project roots, registers bounded artifact metadata, records project-to-artifact relationships, and reports structural evidence. Running the scan again does not duplicate artifacts by location. No source file is modified.
