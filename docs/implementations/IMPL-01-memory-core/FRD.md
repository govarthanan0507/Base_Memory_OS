# IMPL-01 FRD — Memory Core

**Version:** 0.1

## Functional requirements

FR-01 The system shall persist memories with type, source, confidence, observed timestamp and metadata.

FR-02 The system shall persist projects with name, root, status, confidence, summary and metadata.

FR-03 The system shall persist artifacts with type, name, physical location, optional hash and modification time.

FR-04 The system shall persist typed relationships between records.

FR-05 The system shall support lexical memory search using SQLite FTS5 when available and a LIKE fallback otherwise.

FR-06 Project discovery shall be read-only: no move, rename, delete or overwrite operations.

FR-07 Discovery shall detect common project markers and code files and create project/artifact records.

FR-08 Repeated artifact locations shall update metadata rather than create duplicate locations.

FR-09 Invalid confidence values shall be rejected by the persistence layer.

## Acceptance behavior

Given an empty database, `memory-os init` creates the schema. `add-memory` persists a record. `search` retrieves it. `scan-projects <root>` discovers project roots and registers files without changing the scanned filesystem.
