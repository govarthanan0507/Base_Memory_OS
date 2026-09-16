import tempfile
import unittest
from pathlib import Path

from memory_os.continuity import conversation_context, project_context, render_project_reentry_brief, render_reentry_brief
from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import Artifact, Memory, MemoryStore, Project


class ContinuityTests(unittest.TestCase):
    def test_reentry_includes_project_and_transitive_artifact(self):
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
                self.assertEqual({item["name"] for item in packet["related"]}, {"Video Understanding", "collector.py"})

                brief = render_reentry_brief(store, cid)
                self.assertIn("Video experiment", brief)
                self.assertIn("Video Understanding", brief)
                self.assertIn("collector.py", brief)
            finally:
                store.close()

    def test_project_context_collects_conversations_artifacts_and_memories(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                cid = persist_conversation(store, Conversation(
                    source="local", external_id="c1", title="Build session",
                    messages=(Message("user", "We decided to keep this local.", 1),),
                ))
                pid = store.add_project(Project("Memory OS", str(Path(tmp) / "memory-os"), summary="Personal work continuity"))
                aid = store.add_artifact(Artifact("README.md", "document", str(Path(tmp) / "memory-os" / "README.md")))
                mid = store.add_memory(Memory("Keep the memory source of truth local.", memory_type="decision", source="test"))
                store.relate(pid, "discussed_in", cid)
                store.relate(pid, "contains", aid)
                store.relate(pid, "has_memory", mid)

                packet = project_context(store, pid)
                self.assertEqual(packet["project"]["name"], "Memory OS")
                self.assertEqual({x["id"] for x in packet["conversations"]}, {cid})
                self.assertEqual({x["id"] for x in packet["artifacts"]}, {aid})
                self.assertEqual({x["memory_id"] for x in packet["memories"]}, {mid})

                brief = render_project_reentry_brief(store, pid)
                self.assertIn("Memory OS", brief)
                self.assertIn("Build session", brief)
                self.assertIn("README.md", brief)
                self.assertIn("Keep the memory source of truth local.", brief)
            finally:
                store.close()

    def test_missing_entities_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                with self.assertRaises(KeyError):
                    conversation_context(store, "missing")
                with self.assertRaises(KeyError):
                    project_context(store, "missing")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
