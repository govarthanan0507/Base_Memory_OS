import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory_os.core import MemoryStore
from memory_os.research import ResearchSource
from memory_os.research_pipeline import ingest_research_source


class ResearchPipelineTests(unittest.TestCase):
    def test_registration_pipeline_persists_url_metadata_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                with patch("memory_os.research_pipeline.capture_text") as capture:
                    result = ingest_research_source(
                        store,
                        ResearchSource("HTTPS://WWW.YOUTUBE.COM/watch?v=abc123"),
                    )
                capture.assert_not_called()
                self.assertEqual(result.source_metadata["provider"], "youtube")
                artifact = store.list_artifacts()[0]
                metadata = json.loads(artifact["metadata_json"])
                self.assertEqual(metadata["resource_id"], "abc123")
                self.assertEqual(metadata["resource_kind"], "video")
            finally:
                store.close()

    def test_capture_pipeline_persists_snapshot_and_provenance(self):
        from memory_os.research_content import SourceSnapshot

        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                snapshot = SourceSnapshot(
                    "https://example.org/article",
                    "captured evidence",
                    "2026-09-17T00:00:00+00:00",
                    "text/plain",
                    200,
                )
                with patch("memory_os.research_pipeline.capture_text", return_value=snapshot):
                    result = ingest_research_source(
                        store,
                        ResearchSource("https://example.org/article"),
                        snapshot_directory=Path(tmp) / "snapshots",
                        capture=True,
                    )
                self.assertEqual(result.snapshot_path, str(Path(tmp) / "snapshots" / f"{snapshot.content_hash}.json"))
                self.assertTrue(Path(result.snapshot_path).exists())
                artifact = store.list_artifacts()[0]
                metadata = json.loads(artifact["metadata_json"])
                self.assertEqual(len(metadata["snapshots"]), 1)
                self.assertEqual(metadata["snapshots"][0]["content_hash"], snapshot.content_hash)
            finally:
                store.close()

    def test_capture_requires_snapshot_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                with self.assertRaises(ValueError):
                    ingest_research_source(
                        store,
                        ResearchSource("https://example.org/article"),
                        capture=True,
                    )
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
