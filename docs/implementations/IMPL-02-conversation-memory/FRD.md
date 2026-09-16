# IMPL-02 FRD — Conversation Memory

**Version:** 0.1

## Functional requirements

- FR-01 The system shall persist a normalized conversation record with stable identity, source, title and provenance.
- FR-02 The system shall persist ordered messages with role, content, source timestamp and stable message identity.
- FR-03 Imports shall be provider-neutral and map external records into a common normalized structure.
- FR-04 Re-importing the same source shall not duplicate an already imported conversation or message.
- FR-05 Source location and import metadata shall remain queryable for audit and future reprocessing.
- FR-06 Importers shall be read-only with respect to the source files.
- FR-07 The implementation shall support a small local JSON contract and line-oriented Markdown conversation format.
- FR-08 Import failure shall be explicit and shall not silently create partial durable memory.

## Acceptance behavior

Given a normalized conversation document, import creates one conversation and its ordered messages. Running the same import again leaves counts unchanged. A source file remains byte-for-byte untouched.
