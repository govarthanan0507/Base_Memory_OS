import tempfile
import unittest
from pathlib import Path

from memory_os.conversation import Conversation, Message, persist_conversation
from memory_os.core import MemoryStore
from memory_os.emotional_signal import extract_behavioral_signal, render_behavioral_signal


class EmotionalSignalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = MemoryStore(Path(self.tmp.name) / "memory.db")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_frustrated_language_produces_frustrated_label_with_matched_cues(self):
        cid = persist_conversation(self.store, Conversation(
            source="local", external_id="c1", title="Debug session",
            messages=(
                Message("user", "I'm so stuck on this bug, it's really frustrating.", 1),
                Message("user", "This is broken and I give up for tonight.", 2),
            ),
        ))
        signal = extract_behavioral_signal(self.store, cid)
        self.assertTrue(signal.available)
        self.assertEqual(signal.label, "frustrated")
        self.assertIn("stuck", signal.frustration_matches)
        self.assertIn("broken", signal.frustration_matches)

    def test_positive_language_produces_positive_label(self):
        cid = persist_conversation(self.store, Conversation(
            source="local", external_id="c2", title="Win session",
            messages=(
                Message("user", "Finally works! I figured it out and made great progress.", 1),
            ),
        ))
        signal = extract_behavioral_signal(self.store, cid)
        self.assertTrue(signal.available)
        self.assertEqual(signal.label, "positive")
        self.assertIn("finally", signal.positive_matches)

    def test_neutral_language_produces_neutral_label_not_a_guess(self):
        cid = persist_conversation(self.store, Conversation(
            source="local", external_id="c3", title="Plain session",
            messages=(
                Message("user", "The database has three tables and a scheduled backup.", 1),
            ),
        ))
        signal = extract_behavioral_signal(self.store, cid)
        self.assertTrue(signal.available)
        self.assertEqual(signal.label, "neutral")
        self.assertEqual(signal.frustration_matches, ())
        self.assertEqual(signal.positive_matches, ())

    def test_conversation_with_no_messages_is_explicitly_unavailable(self):
        cid = persist_conversation(self.store, Conversation(
            source="local", external_id="c4", title="Empty session", messages=(),
        ))
        signal = extract_behavioral_signal(self.store, cid)
        self.assertFalse(signal.available)
        self.assertEqual(signal.label, "unavailable")

    def test_missing_conversation_raises_keyerror(self):
        with self.assertRaises(KeyError):
            extract_behavioral_signal(self.store, "missing")

    def test_render_includes_label_and_matched_cues(self):
        cid = persist_conversation(self.store, Conversation(
            source="local", external_id="c5", title="Debug session",
            messages=(Message("user", "Ugh, I'm stuck again.", 1),),
        ))
        rendered = render_behavioral_signal(self.store, cid)
        self.assertIn("frustrated", rendered)
        self.assertIn("stuck", rendered)

    def test_no_new_persistence_call_anywhere_in_module(self):
        import memory_os.emotional_signal as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        for banned in ("add_memory", "add_project", "add_artifact", "add_candidate", "INSERT"):
            self.assertNotIn(banned, source)


if __name__ == "__main__":
    unittest.main()
