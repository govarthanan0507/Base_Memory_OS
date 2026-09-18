import tempfile
import unittest
from pathlib import Path

from memory_os.continuity import (
    conversation_context,
    find_project_by_name,
    project_completion_signal,
    project_context,
    render_project_reentry_brief,
    render_reentry_brief,
    submit_query,
)
from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import Artifact, Memory, MemoryCandidateRecord, MemoryStore, Project


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

    def test_project_reentry_surfaces_last_conversation_and_open_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                cid = persist_conversation(store, Conversation(
                    source="local", external_id="c-reentry", title="Research session",
                    messages=(Message("user", "We still need to test the importer.", 1),),
                ))
                pid = store.add_project(Project("Importer", str(Path(tmp) / "importer")))
                store.relate(pid, "discussed_in", cid)
                store.add_project_event(pid, "decision", "Keep importer deterministic", timestamp="2026-09-17T05:00:00+00:00")
                store.add_candidate(MemoryCandidateRecord(
                    content="Test the importer with a real ChatGPT export",
                    memory_type="task",
                    source="test",
                    source_message_id="msg-1",
                    confidence=0.9,
                    metadata={"project_id": pid},
                    observed_at="2026-09-17T05:01:00+00:00",
                ))

                packet = project_context(store, pid)
                self.assertEqual(packet["latest_conversation"]["id"], cid)
                self.assertEqual(len(packet["open_candidates"]), 1)
                brief = render_project_reentry_brief(store, pid)
                self.assertIn("Research session", brief)
                self.assertIn("Keep importer deterministic", brief)
                self.assertIn("Test the importer with a real ChatGPT export", brief)
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

    def test_completion_signal_unclear_for_freshly_created_project(self):
        # add_project always records its own "project_created" event, so a
        # brand-new project has activity but no artifacts/candidates yet —
        # the "unavailable" branch only applies if a project row somehow
        # existed with zero events at all, which add_project never produces.
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Bare Project", str(Path(tmp) / "bare")))
                signal = project_completion_signal(store, pid)
                self.assertTrue(signal["available"])
                self.assertEqual(signal["artifact_count"], 0)
                self.assertEqual(signal["open_candidate_count"], 0)
                self.assertIn("unclear", signal["label"])
            finally:
                store.close()

    def test_completion_signal_settled_when_no_open_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Importer", str(Path(tmp) / "importer")))
                aid = store.add_artifact(Artifact("importer.py", "code", str(Path(tmp) / "importer" / "importer.py")))
                store.relate(pid, "contains", aid)

                signal = project_completion_signal(store, pid)
                self.assertTrue(signal["available"])
                self.assertEqual(signal["artifact_count"], 1)
                self.assertEqual(signal["open_candidate_count"], 0)
                self.assertIn("settled", signal["label"])
            finally:
                store.close()

    def test_completion_signal_actively_evolving_with_many_open_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Sorter", str(Path(tmp) / "sorter")))
                aid = store.add_artifact(Artifact("sorter.py", "code", str(Path(tmp) / "sorter" / "sorter.py")))
                store.relate(pid, "contains", aid)
                store.add_candidate(MemoryCandidateRecord(
                    content="Classify a new file",
                    memory_type="task",
                    source="test",
                    source_message_id="msg-1",
                    confidence=0.6,
                    metadata={"project_id": pid},
                    observed_at="2026-09-18T00:00:00+00:00",
                ))

                signal = project_completion_signal(store, pid)
                self.assertTrue(signal["available"])
                self.assertEqual(signal["open_candidate_count"], 1)
                self.assertIn("actively evolving", signal["label"])

                brief = render_project_reentry_brief(store, pid)
                self.assertIn("## Completion signal", brief)
                self.assertIn("actively evolving", brief)
            finally:
                store.close()

    def test_completion_signal_missing_project_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                with self.assertRaises(KeyError):
                    project_completion_signal(store, "missing")
            finally:
                store.close()

    def test_submit_query_matches_project_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                pid = store.add_project(Project("Video Understanding", str(Path(tmp) / "video")))
                self.assertEqual(find_project_by_name(store, "status of Video Understanding"), pid)

                reply = submit_query(store, "what's the status of Video Understanding")
                self.assertIn("Video Understanding", reply)
                self.assertIn("## Completion signal", reply)
            finally:
                store.close()

    def test_submit_query_unmatched_text_is_explicit_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                store.add_project(Project("Video Understanding", str(Path(tmp) / "video")))
                reply = submit_query(store, "how is the weather")
                self.assertIn("couldn't match", reply)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
