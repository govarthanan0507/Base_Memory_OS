import tempfile
import unittest
from pathlib import Path

from memory_os.continuity import conversation_context, render_reentry_brief
from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import Artifact, MemoryStore, Project


class ContinuityTests(unittest.TestCase):
    def test_reentry_includes_linked_project_and_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                cid = persist_conversation(store, Conversation(
                    source="chatgpt",
                    external_id="chat-1",
                    title="Video experiment",
                    messages=(Message("user", "Where did I leave this?", 1),),
                ))
                pid = store.add_project(Project("Video Understanding", str(Path(tmp) / "project")))
                aid = store.add_artifact(Artifact("collector.py", "code", str(Path(tmp) / "project" / "collector.py")))
                store.relate(pid, "discussed_in", cid)
                store.relate(pid, "contains", aid)

                packet = conversation_context(store, cid)
                self.assertEqual(packet["conversation"]["title"], "Video experiment")
                self.assertEqual({item["name"] for item in packet["related"]}, {"Video Understanding"})

                brief = render_reentry_brief(store, cid)
                self.assertIn("Video experiment", brief)
                self.assertIn("Video Understanding", brief)
            finally:
                store.close()

    def test_missing_conversation_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                with self.assertRaises(KeyError):
                    conversation_context(store, "missing")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
