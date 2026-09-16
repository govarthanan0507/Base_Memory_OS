import tempfile
import unittest
from pathlib import Path

from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import Artifact, MemoryStore, Project
from memory_os.timeline import project_timeline, render_project_timeline


class TimelineTests(unittest.TestCase):
    def test_project_timeline_includes_relations_and_artifact_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Video Project", str(Path(tmp) / "video")))
                cid = persist_conversation(store, Conversation(
                    source="chatgpt", external_id="timeline-1", title="Video discussion",
                    messages=(Message("user", "Continue the video project", 1),),
                ))
                aid = store.add_artifact(Artifact(
                    "collector.py", "code", str(Path(tmp) / "video" / "collector.py"),
                    modified_at="2026-09-17T10:00:00+00:00",
                ))
                store.relate(pid, "discussed_in", cid, {"reason": "project discussion"})
                store.relate(pid, "contains", aid)
                store.add_project_event(pid, "experiment", "Tested the collector", "2026-09-17T11:00:00+00:00")

                events = project_timeline(store, pid)
                summaries = [event["summary"] for event in events]
                self.assertTrue(any("Video Project" in item for item in summaries))
                self.assertTrue(any("discussed_in" in item for item in summaries))
                self.assertTrue(any("collector.py" in item for item in summaries))
                self.assertTrue(any("Tested the collector" in item for item in summaries))

                rendered = render_project_timeline(store, pid)
                self.assertIn("Video Project", rendered)
                self.assertIn("collector.py", rendered)
                self.assertIn("Tested the collector", rendered)
            finally:
                store.close()

    def test_missing_project_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                self.assertEqual(project_timeline(store, "missing"), [])
                self.assertIn("Project not found", render_project_timeline(store, "missing"))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
