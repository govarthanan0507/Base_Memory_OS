# IMPL-06 — Continuity OS TRD v0.1

## Architecture

```text
SQLite source of truth
       ↓
project_context()
       ↓
continuity_snapshot()
       ↓
render_continuity_dashboard()
       ↓
CLI: memory-os dashboard
```

## Implementation paths

- `src/memory_os/continuity_os.py`
- `src/memory_os/continuity.py`
- `src/memory_os/cli.py`
- `tests/test_continuity_os.py`

## Safety

The dashboard performs reads only. No filesystem movement, memory promotion, project mutation or automatic prioritization occurs.

## Verification

The existing CI matrix executes the full unittest suite on Python 3.11–3.14.
