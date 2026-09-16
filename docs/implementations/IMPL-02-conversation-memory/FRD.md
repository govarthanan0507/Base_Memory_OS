# IMPL-02 FRD — Conversation Memory

**Version:** 0.2

## Functional requirements

- FR-01 The system shall persist a normalized conversation record with stable identity, source, title and provenance.
- FR-02 The system shall persist ordered messages with role, content, source timestamp and stable message identity.
- FR-03 Imports shall be provider-neutral and map external records into a common normalized structure.
- FR-04 Re-importing the same source shall not duplicate an already imported conversation or message.
- FR-05 Source location and import metadata shall remain queryable for audit and future reprocessing.
- FR-06 Importers shall be read-only with respect to the source files.
- FR-07 The implementation shall support local JSON and line-oriented Markdown conversation formats plus the verified ChatGPT export shape.
- FR-08 Import failure shall be explicit and shall not silently create partial durable memory.
- FR-09 Candidate extraction shall produce reviewable evidence with source conversation/message provenance and confidence.
- FR-10 Candidate acceptance shall be explicit before promotion to durable memory or projection as project evidence.
- FR-11 Accepted candidates associated with a project shall be projectable into idempotent project events while retaining candidate, conversation and message provenance.
- FR-12 Conversation and project re-entry views shall remain evidence-based and distinguish current state from recorded historical events.

## Acceptance behavior

Given a normalized conversation document, import creates one conversation and its ordered messages. Running the same import again leaves counts unchanged. A source file remains byte-for-byte untouched. Explicitly extracted candidates remain candidates until reviewed. Accepted candidates can be projected into project history without duplication, while rejected or unreviewed candidates are excluded from project evidence.
