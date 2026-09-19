import tempfile
import unittest
from pathlib import Path

from memory_os.core import Artifact, ArtifactProjectCandidateRecord, MemoryStore, Project
from memory_os.service import MemoryOSService, default_data_dir


class ServiceLayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.tmp.name) / "memory.db")
        self.service = MemoryOSService(store=self.store)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_wrapping_an_existing_store_does_not_open_a_second_connection(self):
        self.assertIs(self.service.store, self.store)
        self.assertEqual(self.service.db_path, self.store.db_path)

    def test_default_data_dir_is_stable_and_absolute(self):
        first = default_data_dir()
        second = default_data_dir()
        self.assertEqual(first, second)
        self.assertTrue(first.is_absolute())

    def test_add_memory_and_search_round_trip(self):
        memory_id = self.service.add_memory("Decided to use SQLite over Postgres", memory_type="decision")
        self.assertTrue(memory_id)
        results = self.service.search_memories("SQLite")
        self.assertTrue(any(r["memory_id"] == memory_id for r in results))

    def test_list_projects_returns_plain_summaries_not_raw_rows(self):
        pid = self.store.add_project(Project("Base Memory OS", str(Path(self.tmp.name) / "bmo")))
        summaries = self.service.list_projects()
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].project_id, pid)
        self.assertEqual(summaries[0].name, "Base Memory OS")

    def test_project_brief_text_matches_continuity_rendering(self):
        pid = self.store.add_project(Project("Base Memory OS", str(Path(self.tmp.name) / "bmo")))
        from memory_os.continuity import render_project_reentry_brief

        self.assertEqual(
            self.service.project_brief_text(pid),
            render_project_reentry_brief(self.store, pid, 50),
        )

    def test_ask_without_project_routes_through_submit_query(self):
        self.store.add_project(Project("Base Memory OS", str(Path(self.tmp.name) / "bmo")))
        reply = self.service.ask("what's the status of Base Memory OS")
        self.assertIn("Base Memory OS", reply)

    def test_ask_with_project_logs_a_chat_note_event(self):
        pid = self.store.add_project(Project("Base Memory OS", str(Path(self.tmp.name) / "bmo")))
        self.service.ask("remember to refactor", project_id=pid)
        events = self.store.list_project_events(pid)
        notes = [e for e in events if e["event_type"] == "chat_note"]
        self.assertEqual(len(notes), 1)

    def test_classify_folder_and_review_artifact_candidate(self):
        folder = Path(self.tmp.name) / "downloads"
        folder.mkdir()
        pid = self.store.add_project(Project("Base Memory OS", str(Path(self.tmp.name) / "bmo")))
        (folder / "base_memory_os_notes.md").write_text("notes", encoding="utf-8")

        result = self.service.classify_folder(folder)
        self.assertGreaterEqual(result.artifacts_registered, 1)
        candidates = self.service.list_artifact_candidates("candidate")
        if candidates:
            outcome = self.service.review_artifact_candidate(candidates[0]["candidate_id"], "accepted")
            self.assertIsNotNone(outcome)

    def test_focus_guidance_text_is_callable_on_empty_store(self):
        text = self.service.focus_guidance_text()
        self.assertIn("Idea-hopping", text)

    def test_emotional_signal_text_on_missing_conversation_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.service.emotional_signal_text("does-not-exist")


if __name__ == "__main__":
    unittest.main()
