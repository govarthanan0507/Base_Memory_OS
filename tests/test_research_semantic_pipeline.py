import unittest

from memory_os.research_content import SourceSnapshot
from memory_os.research_extract import extract_observations
from memory_os.research_semantic import extract_semantic_candidates


class ResearchSemanticPipelineTests(unittest.TestCase):
    def test_source_to_snapshot_to_observation_to_candidate_chain_preserves_provenance(self):
        snapshot = SourceSnapshot(
            "https://example.org/article",
            """<title>Memory Research</title>
            <h1>Personal Work Memory</h1>
            <a href='https://github.com/example/memory'>memory repo</a>
            <p>Tool: Graphiti</p>
            <p>Idea: connect research to projects.</p>""",
            "2026-09-17T00:00:00+00:00",
            "text/html",
            200,
        )

        observations = extract_observations(snapshot)
        candidates = extract_semantic_candidates(snapshot, observations)

        self.assertEqual(observations.metadata["content_hash"], snapshot.content_hash)
        self.assertEqual(observations.links, ("https://github.com/example/memory",))
        self.assertEqual(
            [(item.kind, item.value) for item in candidates],
            [
                ("repository", "example/memory"),
                ("tool", "Graphiti"),
                ("idea", "connect research to projects"),
                ("topic", "Memory Research"),
                ("topic", "Personal Work Memory"),
            ],
        )
        for item in candidates:
            self.assertEqual(item.source_url, snapshot.url)
            self.assertEqual(item.content_hash, snapshot.content_hash)
            self.assertEqual(item.captured_at, snapshot.captured_at)
            self.assertEqual(item.metadata["review_status"], "candidate")


if __name__ == "__main__":
    unittest.main()
