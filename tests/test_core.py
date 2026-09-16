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

    def test_project_and_artifact_counts(self):
        self.store.add_project(Project("Demo", "/tmp/demo"))
        self.store.add_artifact(Artifact("main.py", "code", "/tmp/demo/main.py"))
        self.store.relate("project", "contains", "artifact")
        self.assertEqual(self.store.counts(), {"memories": 0, "projects": 1, "artifacts": 1, "relations": 1})

    def test_confidence_is_validated(self):
        with self.assertRaises(Exception):
            self.store.add_memory(Memory("bad", confidence=2.0))


if __name__ == "__main__":
    unittest.main()
