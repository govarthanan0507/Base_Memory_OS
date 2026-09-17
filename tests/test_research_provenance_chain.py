import unittest

from memory_os.core import MemoryStore
from memory_os.research_content import SourceSnapshot, attach_snapshot_metadata, save_snapshot
from memory_os.research_extract import extract_observations
from memory_os.research_pipeline import ingest_research_source
from memory_os.research_semantic import extract_semantic_candidates


class ResearchProvenanceChainTests(unittest.TestCase):
    def test_capture_evidence_to_candidates_keeps_exact_snapshot_identity(self):
        store = MemoryStore(":memory:")
        result = ingest_research_source(
            store,
            "https://example.org/article",
            title="Research article",
            capture=False,
        )
        snapshot = SourceSnapshot(
            result.canonical_url,
            "<title>Agent Memory</title><h1>Continuity</h1>"
            "<p>Repository: https://github.com/example/memory</p>"
            "<p>Tool: Graphiti</p>",
            "2026-09-17T00:00:00+00:00",
            "text/html",
            200,
        )
        path = save_snapshot(snapshot, "/tmp/base-memory-os-test-snapshots")
        attach_snapshot_metadata(store, result.artifact_id, snapshot, path)

        observations = extract_observations(snapshot)
        candidates = extract_semantic_candidates(snapshot, observations)
        self.assertTrue(candidates)
        for candidate in candidates:
            self.assertEqual(candidate.source_url, snapshot.url)
            self.assertEqual(candidate.content_hash, snapshot.content_hash)
            self.assertEqual(candidate.captured_at, snapshot.captured_at)
            self.assertEqual(candidate.metadata["review_status"], "candidate")

        row = store.conn.execute(
            "SELECT metadata_json FROM artifacts WHERE artifact_id=?",
            (result.artifact_id,),
        ).fetchone()
        self.assertIn(snapshot.content_hash, row["metadata_json"])


if __name__ == "__main__":
    unittest.main()
