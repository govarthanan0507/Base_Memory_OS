import unittest

from memory_os.research_content import SourceSnapshot
from memory_os.research_extract import extract_observations
from memory_os.research_semantic import extract_semantic_candidates


class ResearchSemanticTests(unittest.TestCase):
    def test_extracts_repositories_tools_ideas_and_topics_with_provenance(self):
        snapshot = SourceSnapshot(
            "https://example.org/research",
            """<html><head><title>Agent Memory</title></head><body>
            <h1>Personal Memory</h1><h2>Continuity</h2>
            <p>Repository: https://github.com/example/memory.</p>
            <p>Tool: Graphiti</p>
            <p>Idea: connect conversations to projects.</p>
            </body></html>""",
            "2026-09-17T00:00:00+00:00",
            "text/html",
            200,
        )
        observations = extract_observations(snapshot)
        candidates = extract_semantic_candidates(snapshot, observations)

        by_kind = {(item.kind, item.value): item for item in candidates}
        self.assertIn(("repository", "example/memory"), by_kind)
        self.assertIn(("tool", "Graphiti"), by_kind)
        self.assertIn(("idea", "connect conversations to projects"), by_kind)
        self.assertIn(("topic", "Agent Memory"), by_kind)
        self.assertEqual(by_kind[("repository", "example/memory")].content_hash, snapshot.content_hash)
        self.assertEqual(by_kind[("tool", "Graphiti")].metadata["review_status"], "candidate")

    def test_duplicate_repository_links_do_not_duplicate_candidates(self):
        snapshot = SourceSnapshot(
            "https://example.org/",
            "<a href='https://github.com/example/memory'>one</a> "
            "<a href='https://github.com/example/memory'>two</a>",
            "2026-09-17T00:00:00+00:00",
        )
        observations = extract_observations(snapshot)
        candidates = extract_semantic_candidates(snapshot, observations)
        repositories = [item for item in candidates if item.kind == "repository"]
        self.assertEqual(len(repositories), 1)

    def test_unknown_source_does_not_invent_repository_or_tool_metadata(self):
        snapshot = SourceSnapshot(
            "https://example.org/",
            "<title>Plain Notes</title><p>No structured provider references.</p>",
            "2026-09-17T00:00:00+00:00",
        )
        observations = extract_observations(snapshot)
        candidates = extract_semantic_candidates(snapshot, observations)
        self.assertEqual([item.kind for item in candidates], ["topic"])


if __name__ == "__main__":
    unittest.main()
