import json
import tempfile
import unittest
from pathlib import Path

from memory_os.candidates import persist_candidates
from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import MemoryStore, Project
from memory_os.evidence import link_conversation_to_project, record_conversation_candidates_as_project_events


class EvidenceTests(unittest.TestCase):
    def test_only_accepted_candidates_become_project_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                project_id = store.add_project(Project("Memory", "/memory"))
                persist_conversation(store, Conversation("test", "Conversation", (Message("user", "I decided to use SQLite.", 1, external_id="m1"),), external_id="conv-1"))
                candidate_ids = persist_candidates(store, "conv-1", [Message("user", "I decided to use SQLite.", 1, external_id="m1")], project_id=project_id)
                self.assertEqual(len(store.list_project_events(project_id)), 1)
                store.review_candidate(candidate_ids[0], "accepted")
                event_ids = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                self.assertEqual(len(event_ids), 1)
                events = store.list_project_events(project_id)
                self.assertEqual(events[0]["event_type"], "candidate_decision")
                metadata = json.loads(events[0]["metadata_json"])
                self.assertEqual(metadata["candidate_id"], candidate_ids[0])
                self.assertEqual(metadata["evidence_status"], "accepted")
            finally:
                store.close()

    def test_repeated_projection_is_idempotent_and_links_conversation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                project_id = store.add_project(Project("Memory", "/memory"))
                persist_conversation(store, Conversation("test", "Conversation", (Message("user", "I decided to use SQLite.", 1, external_id="m1"),), external_id="conv-1"))
                ids = persist_candidates(store, "conv-1", [Message("user", "I decided to use SQLite.", 1, external_id="m1")], project_id=project_id)
                store.review_candidate(ids[0], "accepted")
                first = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                second = record_conversation_candidates_as_project_events(store, "conv-1", project_id)
                self.assertEqual(first, second)
                self.assertEqual(len(store.list_project_events(project_id)), 2)
                links = store.related(project_id, "has_conversation")
                self.assertEqual(len(links), 1)
                canonical_id = store.conn.execute(
                    "SELECT conversation_id FROM conversations WHERE external_id=?",
                    ("conv-1",),
                ).fetchone()["conversation_id"]
                self.assertEqual(links[0]["target_id"], canonical_id)
            finally:
                store.close()

    def test_explicit_link_requires_existing_entities(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                project_id = store.add_project(Project("Memory", "/memory"))
                with self.assertRaises(KeyError):
                    link_conversation_to_project(store, "missing", project_id)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
