import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore, Project
from memory_os.focus_guidance import (
    cross_project_completion,
    detect_idea_hopping,
    render_focus_guidance,
)


class FocusGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.tmp.name) / "memory.db")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def _project(self, name: str) -> str:
        return self.store.add_project(Project(name, str(Path(self.tmp.name) / name)))

    def test_alternating_projects_detected_as_idea_hopping(self):
        # Timestamps are set in the far future so they sort ahead of the
        # `project_created` events add_project() records at real "now".
        a = self._project("Video Understanding")
        b = self._project("Collector Tooling")
        for i, pid in enumerate([a, b, a, b, a, b]):
            self.store.add_project_event(pid, "chat_note", f"note {i}", timestamp=f"2099-01-01T00:00:{i:02d}Z")
        signal = detect_idea_hopping(self.store, window=6)
        self.assertTrue(signal.available)
        self.assertTrue(signal.detected)
        self.assertEqual(signal.switch_count, 5)
        self.assertEqual(set(signal.projects_involved), {a, b})

    def test_single_project_activity_is_not_hopping(self):
        a = self._project("Solo Project")
        for i in range(4):
            self.store.add_project_event(a, "chat_note", f"note {i}", timestamp=f"2099-01-01T00:00:{i:02d}Z")
        signal = detect_idea_hopping(self.store, window=8)
        self.assertTrue(signal.available)
        self.assertFalse(signal.detected)
        self.assertEqual(signal.switch_count, 0)

    def test_fewer_than_two_events_is_explicitly_unavailable(self):
        # add_project itself records exactly one `project_created` event.
        self._project("Lone Project")
        signal = detect_idea_hopping(self.store, window=8)
        self.assertFalse(signal.available)

    def test_no_events_at_all_is_unavailable(self):
        signal = detect_idea_hopping(self.store, window=8)
        self.assertFalse(signal.available)

    def test_window_below_two_raises(self):
        with self.assertRaises(ValueError):
            detect_idea_hopping(self.store, window=1)

    def test_cross_project_completion_reuses_project_completion_signal(self):
        a = self._project("Alpha")
        b = self._project("Beta")
        rollup = cross_project_completion(self.store)
        ids = {entry["project_id"] for entry in rollup}
        self.assertEqual(ids, {a, b})
        for entry in rollup:
            # add_project's own `project_created` event is enough for
            # project_completion_signal to consider a signal available.
            self.assertIn("signal", entry)
            self.assertTrue(entry["signal"]["available"])
            self.assertEqual(entry["signal"]["artifact_count"], 0)

    def test_render_includes_hop_and_completion_sections(self):
        a = self._project("Alpha")
        b = self._project("Beta")
        self.store.add_project_event(a, "chat_note", "a1", timestamp="2026-01-01T00:00:00Z")
        self.store.add_project_event(b, "chat_note", "b1", timestamp="2026-01-01T00:00:01Z")
        rendered = render_focus_guidance(self.store)
        self.assertIn("## Idea-hopping", rendered)
        self.assertIn("## Project completion signals", rendered)
        self.assertIn("Alpha", rendered)
        self.assertIn("Beta", rendered)

    def test_no_new_persistence_call_anywhere_in_module(self):
        import memory_os.focus_guidance as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        for banned in ("add_memory", "add_project(", "add_artifact", "add_candidate", "add_project_event", "INSERT"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
