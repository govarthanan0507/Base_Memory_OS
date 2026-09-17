import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore, Project
from memory_os.project_evidence import render_project_evidence


class ProjectEvidenceTests(unittest.TestCase):
    def test_compact_view_labels_snapshot_history_and_continuity(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                project_id = store.add_project(Project(
                    "Demo", "/demo", status="PARTIALLY BUILT", confidence=0.8,
                    metadata={"file_count": 3, "code_file_count": 2,
                              "state_evidence": {"test_file_count": 1, "todo_fixme_count": 2,
                                                  "recent_code_file_count_30d": 1},
                              "git": {"git_branch": "main", "git_head": "abc123"}},
                ))
                store.add_project_event(project_id, "decision", "Use SQLite", "2026-01-01T00:00:00+00:00")
                output = render_project_evidence(store, project_id)
                self.assertIn("## Current snapshot", output)
                self.assertIn("## Historical evidence", output)
                self.assertIn("## Explicit continuity", output)
                self.assertIn("Structural signals do not prove project intent", output)
                self.assertIn("Use SQLite", output)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
