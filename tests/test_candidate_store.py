import tempfile
import unittest
from pathlib import Path

from memory_os.candidates import persist_candidates
from memory_os.conversation import Message
from memory_os.core import MemoryStore


class CandidateStoreTests(unittest.TestCase):
    def test_persist_and_review_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                messages = [Message("user", "We decided to use SQLite for V0.", 1)]
                ids = persist_candidates(store, "conv-1", messages)
                self.assertEqual(len(ids), 1)
                self.assertEqual(len(store.list_memories()), 0)
                self.assertEqual(store.list_candidates()[0]["status"], "candidate")

                store.review_candidate(ids[0], "accepted")
                self.assertEqual(len(store.list_memories()), 1)
                self.assertEqual(store.list_candidates()[0]["status"], "accepted")
                self.assertTrue(store.list_memories()[0]["source"].startswith("candidate:"))
            finally:
                store.close()

    def test_rejection_does_not_create_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                ids = persist_candidates(store, "conv-1", [Message("user", "I prefer local-first tools.", 1)])
                store.review_candidate(ids[0], "rejected")
                self.assertEqual(len(store.list_memories()), 0)
                self.assertEqual(store.list_candidates("rejected")[0]["status"], "rejected")
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
