import unittest

from memory_os.core import MemoryCandidateRecord, MemoryStore
from memory_os.consolidation import consolidate_accepted_candidates


class ConsolidationTests(unittest.TestCase):
    def test_same_accepted_fact_from_two_candidates_becomes_one_memory_with_evidence(self):
        store = MemoryStore(":memory:")
        store.add_candidate(MemoryCandidateRecord(
            content="I prefer local-first tools", memory_type="preference",
            source="conversation:one", source_message_id="m1", confidence=0.9,
            status="accepted", observed_at="2026-09-17T10:00:00+00:00",
            candidate_id="candidate-1", metadata={"conversation_id": "one"},
        ))
        store.add_candidate(MemoryCandidateRecord(
            content="I prefer local-first tools", memory_type="preference",
            source="conversation:two", source_message_id="m2", confidence=0.8,
            status="accepted", observed_at="2026-09-17T11:00:00+00:00",
            candidate_id="candidate-2", metadata={"conversation_id": "two"},
        ))

        result = consolidate_accepted_candidates(store)

        self.assertEqual(result["created"], 1)
        self.assertEqual(result["deduplicated"], 1)
        memories = store.list_memories()
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]["content"], "I prefer local-first tools")
        self.assertEqual(memories[0]["metadata_json"].count("candidate-"), 2)

    def test_rejected_candidates_never_become_durable_memory(self):
        store = MemoryStore(":memory:")
        store.add_candidate(MemoryCandidateRecord(
            content="Do not retain this", memory_type="preference",
            source="conversation:one", status="rejected",
            candidate_id="candidate-rejected",
        ))

        result = consolidate_accepted_candidates(store)

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["deduplicated"], 0)
        self.assertEqual(store.list_memories(), [])


if __name__ == "__main__":
    unittest.main()
