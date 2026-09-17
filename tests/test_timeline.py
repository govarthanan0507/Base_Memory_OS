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
                cid = persist_conversation(store, Conversation(source="chatgpt", external_id="timeline-1", title="Video discussion", messages=(Message("user", "Continue the video project", 1),)))
                aid = store.add_artifact(Artifact("collector.py", "code", str(Path(tmp) / "video" / "collector.py"), modified_at="2026-09-17T10:00:00+00:00"))
                store.relate(pid, "discussed_in", cid, {"reason": "project discussion"}); store.relate(pid, "contains", aid)
                store.add_project_event(pid, "experiment", "Tested the collector", "2026-09-17T11:00:00+00:00")
                summaries = [e["summary"] for e in project_timeline(store, pid)]
                self.assertTrue(any("discussed_in" in x for x in summaries)); self.assertTrue(any("collector.py" in x for x in summaries)); self.assertTrue(any("Tested the collector" in x for x in summaries))
                rendered = render_project_timeline(store, pid); self.assertIn("Video Project", rendered); self.assertIn("collector.py", rendered); self.assertIn("Tested the collector", rendered)
            finally: store.close()

    def test_artifact_change_event_is_exposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Artifact Project", str(Path(tmp) / "artifact")))
                aid = store.add_artifact(Artifact("app.py", "code", str(Path(tmp) / "artifact" / "app.py"), content_hash="new-hash", modified_at="2026-09-17T12:00:00+00:00"))
                store.relate(pid, "contains", aid)
                store.add_artifact_event(aid, "changed", "old-hash", "new-hash", "2026-09-17T11:00:00+00:00", "2026-09-17T12:00:00+00:00", timestamp="2026-09-17T13:00:00+00:00")
                changes = [e for e in project_timeline(store, pid) if e["event_type"] == "artifact_change" and e["metadata"]["old_hash"] == "old-hash"]
                self.assertEqual(len(changes), 1); self.assertEqual(changes[0]["metadata"]["new_hash"], "new-hash")
            finally: store.close()

    def test_missing_project_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                self.assertEqual(project_timeline(store, "missing"), []); self.assertIn("Project not found", render_project_timeline(store, "missing"))
            finally: store.close()

if __name__ == "__main__": unittest.main()
