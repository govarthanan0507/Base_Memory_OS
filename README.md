# Base Memory OS

A local-first, vendor-independent personal work memory system.

## V0 status

**V0 COMPLETE — IMPL-01 through IMPL-06 implemented and verified.**

The V0 system provides a local SQLite memory core, normalized conversation imports, read-only project/file discovery, artifact history, research-source provenance, deterministic research candidates and cross-source evidence retention, project re-entry briefings, and a compact continuity dashboard.

## Verification status

CI run #261 (`35188547700`) passed the full unit-test matrix on Python 3.11, 3.12, 3.13 and 3.14 after the IMPL-06 implementation. Earlier failures remain preserved in the implementation logs rather than being rewritten away.

## V0 capabilities

- **IMPL-01 Memory Core:** SQLite source of truth, durable memories, candidates, projects, artifacts, relations, provenance and deterministic IDs.
- **IMPL-02 Conversation Memory:** provider-neutral conversation/message model, ChatGPT export normalization, duplicate-safe import and provenance-preserving re-import.
- **IMPL-03 Project & File Intelligence:** read-only filesystem discovery, project boundaries, code structure signals, Git evidence, artifact registration/history and project timelines.
- **IMPL-04 Research Memory:** canonical URL identity, bounded evidence capture, SHA-256 snapshots, provider URL metadata, structural observations, semantic candidates, persistent research registry and source-aware evidence migration.
- **IMPL-05 Re-entry:** project-centric briefing with latest linked conversation, recent recorded activity, open unresolved candidates, artifacts and durable memories.
- **IMPL-06 Continuity OS:** compact project continuity snapshot and `memory-os dashboard` CLI surface.

## Evidence boundary

```text
SOURCE / CONVERSATION / FILE
            ↓
       RAW EVIDENCE
            ↓
   EXTRACTED OBSERVATION
            ↓
  REVIEWABLE CANDIDATE
            ↓
 DEDUPLICATED MEMORY/ENTITY
            ↓
   EXPLICIT HUMAN REVIEW
            ↓
       DURABLE STATE
```

The system preserves provenance and does not treat observation as verification. Candidate review is explicit. Project/file discovery is read-only and does not move or delete user files.

## Main CLI surfaces

```text
memory-os init
memory-os dashboard
memory-os scan-projects <root>
memory-os import-chatgpt-export <path>
memory-os reentry <conversation_id>
memory-os reentry-project <project_id>
memory-os timeline-project <project_id>
memory-os add-research-source <url>
memory-os capture-research-source <url> --snapshot-dir <dir>
```

## Documentation

Each implementation has its own BRD → FRD → PRD → TRD package and implementation log under `docs/implementations/`. Failures, root causes, fixes and verification evidence remain part of the engineering history.

## Roadmap

V0: **IMPL-01 → IMPL-02 → IMPL-03 → IMPL-04 → IMPL-05 → IMPL-06 — COMPLETE**.

Post-V0 work can add richer adapters, stronger codebase understanding, optional local LLM assistance, broader research providers, UI, and cross-agent connectors without replacing the provenance-first core.

## Development rule

**Small change → test → verify → document → commit → next small change.** README and the relevant implementation log are updated as each milestone closes.
