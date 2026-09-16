import json
import tempfile
import unittest
from pathlib import Path

from memory_os.candidates import persist_candidates
from memory_os.continuity import render_project_reentry_brief
from memory_os.conversation import get_messages
from memory_os.core import Artifact, MemoryStore, Project
from memory_os.evidence import record_conversation_candidates_as_project_events
from memory_os.importers import import_chatgpt_export
from memory_os.timeline import render_project_timeline


class IntegrationTests(unittest.TestCase):
    def test_chatgpt_import_can_be_linked_to_project_and_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            export = root / "conversations.json"
            export.write_text(json.dumps([{
                "id": "conv-1",
                "title": "Build the collector",
                "create_time": 1000,
                "update_time": 1100,
                "mapping": {
                    "a": {"message": {"id": "m1", "author": {"role": "user"}, "content": {"parts": ["I decided to build the collector locally"]}, "create_time": 1000}},
                    "b": {"message": {"id": "m2", "author": {"role": "assistant"}, "content": {"parts": ["Start with the importer"]}, "create_time": 1100}},
                },
            }]), encoding="utf-8")
            store = MemoryStore(root / "memory.db")
            try:
                count = import_chatgpt_export(store, export)
                self.assertEqual(count, 1)
                conversations = store.conn.execute("SELECT * FROM conversations").fetchall()
                self.assertEqual(len(conversations), 1)
                cid = conversations[0]["conversation_id"]
                self.assertEqual(len(get_messages(store, cid)), 2)

                pid = store.add_project(Project("Collector", str(root / "collector")))
                aid = store.add_artifact(Artifact("collector.py", "code", str(root / "collector.py")))
                store.relate(pid, "contains", aid)
                store.relate(pid, "discussed_in", cid)

                candidate_ids = persist_candidates(store, cid, get_messages(store, cid), project_id=pid)
                self.assertEqual(len(candidate_ids), 1)
                store.review_candidate(candidate_ids[0], "accepted")
                event_ids = record_conversation_candidates_as_project_events(store, cid, pid)
                self.assertEqual(len(event_ids), 1)

                timeline = render_project_timeline(store, pid)
                self.assertIn("candidate_decision", timeline)
                self.assertIn("collector.py", timeline)

                reentry = render_project_reentry_brief(store, pid)
                self.assertIn("Collector", reentry)
                self.assertIn(cid, reentry)
                self.assertIn("collector.py", reentry)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
