# IMPL-05 — Re-entry TRD v0.1

## Architecture

IMPL-05 builds on the existing SQLite source of truth and continuity layer.

```text
projects
  ├── relations ── conversations
  ├── relations ── artifacts
  ├── relations ── memories
  ├── project_events
  └── memory_candidates.metadata_json.project_id
                 ↓
          project_context()
                 ↓
      render_project_reentry_brief()
```

## Implementation paths

- `src/memory_os/continuity.py`
- `tests/test_continuity.py`

## Evidence rules

Project candidates are selected from the existing `memory_candidates` table and matched through the explicit `project_id` metadata field. No schema expansion is required for this slice.

Recent activity is read from `project_events`, preserving persisted timestamps and summaries. The renderer displays only recorded evidence.

## Testing

The CI matrix runs the complete unittest suite on Python 3.11–3.14. Re-entry tests cover existing continuity, project/artifact/memory linkage, unresolved candidate surfacing and missing-entity behavior.
