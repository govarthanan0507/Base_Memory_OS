import tempfile
import unittest
from pathlib import Path

from memory_os.core import Artifact, Memory, MemoryStore, Project


class MemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.tmp.name) / "memory.db")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_memory_round_trip_and_search(self):
        mid = self.store.add_memory(Memory("The collector feeds the video analyzer", source="chatgpt"))
        rows = self.store.search("collector")
        self.assertEqual(rows[0]["memory_id"], mid)

    def test_project_and_artifact_counts_and_relation_traversal(self):
        project_id = self.store.add_project(Project("Demo", "/tmp/demo"))
        artifact_id = self.store.add_artifact(Artifact("main.py", "code", "/tmp/demo/main.py"))
        self.store.relate(project_id, "contains", artifact_id)
        self.assertEqual(self.store.counts(), {
            "memories": 0, "memory_candidates": 0, "projects": 1,
            "project_events": 1, "artifacts": 1, "relations": 1,
        })
        relation = self.store.related(project_id, "contains")[0]
        self.assertEqual(relation["target_id"], artifact_id)

    def test_project_status_changes_are_historical_events(self):
        project_id = self.store.add_project(Project("Demo", "/tmp/demo", status="DISCOVERED"))
        self.store.add_project(Project("Demo", "/tmp/demo", status="PARTIALLY BUILT"))
        events = self.store.list_project_events(project_id)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "status_change")
        self.assertIn("DISCOVERED → PARTIALLY BUILT", events[0]["summary"])
        project = self.store.conn.execute(
            "SELECT status FROM projects WHERE project_id=?", (project_id,)
        ).fetchone()
        self.assertEqual(project["status"], "PARTIALLY BUILT")

    def test_manual_project_event_is_idempotent(self):
        project_id = self.store.add_project(Project("Demo", "/tmp/demo"))
        first = self.store.add_project_event(project_id, "milestone", "Prototype imported", "2026-01-01T00:00:00+00:00")
        second = self.store.add_project_event(project_id, "milestone", "Prototype imported", "2026-01-01T00:00:00+00:00")
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.list_project_events(project_id)), 2)

    def test_confidence_is_validated(self):
        with self.assertRaises(ValueError):
            self.store.add_memory(Memory("bad", confidence=2.0))

    def test_duplicate_relation_is_idempotent(self):
        self.store.relate("project-1", "contains", "artifact-1")
        self.store.relate("project-1", "contains", "artifact-1")
        self.assertEqual(self.store.counts()["relations"], 1)

    def test_negative_limit_search_is_empty(self):
        self.assertEqual(self.store.search("anything", -1), [])


if __name__ == "__main__":
    unittest.main()
