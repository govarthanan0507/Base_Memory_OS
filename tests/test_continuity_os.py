import tempfile
import unittest
from pathlib import Path

from memory_os.continuity_os import continuity_snapshot, render_continuity_dashboard
from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import MemoryCandidateRecord, MemoryStore, Project


class ContinuityOSTests(unittest.TestCase):
    def test_snapshot_and_dashboard_summarize_project_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                cid = persist_conversation(store, Conversation(
                    source="local", external_id="c1", title="Last build",
                    messages=(Message("user", "Continue later", 1),),
                ))
                pid = store.add_project(Project("Memory OS", str(Path(tmp) / "memory-os")))
                store.relate(pid, "discussed_in", cid)
                store.add_candidate(MemoryCandidateRecord(
                    content="Test the next unresolved thread",
                    memory_type="task",
                    source="test",
                    confidence=0.8,
                    metadata={"project_id": pid},
                ))

                snapshot = continuity_snapshot(store)
                self.assertEqual(len(snapshot), 1)
                self.assertEqual(snapshot[0]["latest_conversation_title"], "Last build")
                self.assertEqual(snapshot[0]["open_candidate_count"], 1)

                dashboard = render_continuity_dashboard(store)
                self.assertIn("Memory OS", dashboard)
                self.assertIn("Last build", dashboard)
                self.assertIn("open threads: 1", dashboard)
            finally:
                store.close()

    def test_empty_workspace_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                self.assertEqual(continuity_snapshot(store), [])
                self.assertIn("No projects recorded.", render_continuity_dashboard(store))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
