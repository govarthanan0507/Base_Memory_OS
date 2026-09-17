import unittest

from memory_os.core import MemoryStore
from memory_os.research_registry import (
    list_research_entity_evidence,
    list_research_entities,
    register_research_candidates,
    review_research_entity,
)
from memory_os.research_semantic import ResearchCandidate


class ResearchRegistryTests(unittest.TestCase):
    def test_same_entity_from_multiple_sources_is_deduplicated_with_multiple_evidence_trails(self):
        store = MemoryStore(":memory:")
        candidates = [
            ResearchCandidate("repository", "Example/Memory", "https://github.com/Example/Memory", "https://a.example", "hash-a", "2026-09-17T00:00:00+00:00", 0.98),
            ResearchCandidate("repository", "example/memory", "https://github.com/example/memory", "https://b.example", "hash-b", "2026-09-17T01:00:00+00:00", 0.98),
            ResearchCandidate("repository", "Example/Memory", "https://github.com/Example/Memory", "https://a.example", "hash-a", "2026-09-17T00:00:00+00:00", 0.98),
        ]
        entities = register_research_candidates(store, candidates)
        self.assertEqual(len(entities), 1)
        evidence = list_research_entity_evidence(store, entities[0].entity_id)
        self.assertEqual(len(evidence), 2)
        self.assertEqual({row["source_url"] for row in evidence}, {"https://a.example", "https://b.example"})

    def test_different_kinds_remain_distinct(self):
        store = MemoryStore(":memory:")
        candidates = [
            ResearchCandidate("tool", "Memory", "Tool: Memory", "https://a.example", "hash-a", "2026-09-17T00:00:00+00:00"),
            ResearchCandidate("idea", "Memory", "Idea: Memory", "https://a.example", "hash-a", "2026-09-17T00:00:00+00:00"),
        ]
        entities = register_research_candidates(store, candidates)
        self.assertEqual({entity.kind for entity in entities}, {"tool", "idea"})

    def test_review_changes_status_without_creating_memory(self):
        store = MemoryStore(":memory:")
        entity = register_research_candidates(
            store,
            [ResearchCandidate("tool", "Graphiti", "Tool: Graphiti", "https://a.example", "hash-a", "2026-09-17T00:00:00+00:00")],
        )[0]
        review_research_entity(store, entity.entity_id, "accepted")
        row = list_research_entities(store, "accepted")[0]
        self.assertEqual(row["entity_id"], entity.entity_id)
        self.assertEqual(row["status"], "accepted")
        self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0], 0)
        with self.assertRaises(ValueError):
            review_research_entity(store, entity.entity_id, "rejected")


if __name__ == "__main__":
    unittest.main()
