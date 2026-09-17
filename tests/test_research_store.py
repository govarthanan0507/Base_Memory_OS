import unittest

from memory_os.core import MemoryStore
from memory_os.research_content import SourceSnapshot
from memory_os.research_extract import extract_observations
from memory_os.research_semantic import extract_semantic_candidates
from memory_os.research_store import (
    list_research_candidate_evidence,
    list_research_candidates,
    persist_research_candidates,
    review_research_candidate,
)


class ResearchStoreTests(unittest.TestCase):
    def _candidates(self, url: str, content: str, captured_at: str):
        snapshot = SourceSnapshot(url, content, captured_at, "text/html", 200)
        return extract_semantic_candidates(snapshot, extract_observations(snapshot))

    def test_same_entity_from_two_sources_is_deduplicated_but_evidence_is_retained(self):
        store = MemoryStore(":memory:")
        first = self._candidates(
            "https://example.org/one",
            "<a href='https://github.com/example/memory'>repo</a>",
            "2026-09-17T00:00:00+00:00",
        )
        second = self._candidates(
            "https://example.org/two",
            "<a href='https://github.com/example/memory'>repo</a>",
            "2026-09-17T01:00:00+00:00",
        )
        first_repo = [item for item in first if item.kind == "repository"]
        second_repo = [item for item in second if item.kind == "repository"]
        self.assertEqual(len(first_repo), 1)
        self.assertEqual(len(second_repo), 1)

        a = persist_research_candidates(store, first_repo)
        b = persist_research_candidates(store, second_repo)
        self.assertEqual(a[0].candidate_id, b[0].candidate_id)
        rows = list_research_candidates(store)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["evidence_count"], 2)
        evidence = list_research_candidate_evidence(store, a[0].candidate_id)
        self.assertEqual({item["source_url"] for item in evidence}, {
            "https://example.org/one", "https://example.org/two"
        })

    def test_persistence_is_idempotent_for_same_snapshot_evidence(self):
        store = MemoryStore(":memory:")
        candidates = self._candidates(
            "https://example.org/article",
            "<p>Tool: Graphiti</p>",
            "2026-09-17T00:00:00+00:00",
        )
        tool = [item for item in candidates if item.kind == "tool"]
        persist_research_candidates(store, tool)
        persist_research_candidates(store, tool)
        rows = list_research_candidates(store)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["evidence_count"], 1)

    def test_review_changes_candidate_status_without_creating_memory(self):
        store = MemoryStore(":memory:")
        candidates = self._candidates(
            "https://example.org/article",
            "<p>Tool: Graphiti</p>",
            "2026-09-17T00:00:00+00:00",
        )
        saved = persist_research_candidates(store, [item for item in candidates if item.kind == "tool"])
        candidate_id = saved[0].candidate_id
        review_research_candidate(store, candidate_id, "accepted")
        self.assertEqual(list_research_candidates(store, "accepted")[0]["status"], "accepted")
        self.assertEqual(store.list_memories(), [])


if __name__ == "__main__":
    unittest.main()
