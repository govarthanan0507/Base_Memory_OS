import tempfile
import unittest
from pathlib import Path

from memory_os.candidates import persist_candidates
from memory_os.conversation import Message
from memory_os.core import MemoryStore, Project
from memory_os.evidence import record_conversation_candidates_as_project_events


class EvidenceTests(unittest.TestCase):
    def test_only_accepted_candidates_become_project_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                project_id = store.add_project(Project("Memory", "/memory"))
                messages = [Message("user", "I decided to use SQLite.", 1, message_id="m1")]
                candidate_ids = persist_candidates(store, "conv-1", messages, project_id=project_id)
                self.assertEqual(len(store.list_project_events(project_id)), 1)  # project_created only
                store.review_candidate(candidate_ids[0], "accepted")
                event_ids = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                self.assertEqual(len(event_ids), 1)
                events = store.list_project_events(project_id)
                self.assertEqual(events[-1]["event_type"], "candidate_decision")
                self.assertEqual(events[-1]["metadata_json"].count(candidate_ids[0]), 1)
            finally:
                store.close()

    def test_repeated_projection_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                project_id = store.add_project(Project("Memory", "/memory"))
                ids = persist_candidates(store, "conv-1", [Message("user", "I decided to use SQLite.", 1, message_id="m1")], project_id=project_id)
                store.review_candidate(ids[0], "accepted")
                first = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                second = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                self.assertEqual(first, second)
                self.assertEqual(len(store.list_project_events(project_id)), 2)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
