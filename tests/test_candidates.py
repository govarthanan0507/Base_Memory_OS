import unittest

from memory_os.candidates import extract_candidates
from memory_os.conversation import Message


class CandidateTests(unittest.TestCase):
    def test_extracts_explicit_signals(self):
        messages = [
            Message("user", "We decided to use SQLite for V0.", 1),
            Message("user", "I prefer local-first tools.", 2),
            Message("user", "TODO: add Claude import later.", 3),
            Message("assistant", "This is ordinary explanatory text.", 4),
        ]
        candidates = extract_candidates(messages)
        self.assertEqual([c.memory_type for c in candidates], ["decision", "preference", "task"])
        self.assertTrue(all(c.status == "candidate" for c in candidates))
        self.assertEqual(candidates[0].source_message_sequence, 1)

    def test_assistant_personal_claims_have_lower_confidence(self):
        messages = [
            Message("user", "I prefer SQLite.", 1),
            Message("assistant", "You prefer SQLite.", 2),
        ]
        candidates = extract_candidates(messages)
        self.assertEqual(len(candidates), 2)
        self.assertGreater(candidates[0].confidence, candidates[1].confidence)

    def test_project_context_is_preserved(self):
        candidates = extract_candidates(
            [Message("user", "We decided to keep this local.", 1)],
            project_id="project-123",
        )
        self.assertEqual(candidates[0].metadata["project_id"], "project-123")
        self.assertEqual(candidates[0].metadata["source_message_id"], candidates[0].metadata["source_message_id"])

    def test_does_not_emit_empty_messages(self):
        self.assertEqual(extract_candidates([Message("user", "   ", 1)]), [])

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            extract_candidates([], 0)


if __name__ == "__main__":
    unittest.main()
