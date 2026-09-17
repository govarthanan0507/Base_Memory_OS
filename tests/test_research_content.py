import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory_os.core import MemoryStore
from memory_os.research import ResearchSource, register_research_source
from memory_os.research_content import SourceSnapshot, attach_snapshot_metadata, capture_text, save_snapshot


class ResearchContentTests(unittest.TestCase):
    def test_snapshot_hash_is_deterministic(self):
        first = SourceSnapshot("https://example.org", "hello", "2026-09-17T00:00:00+00:00")
        second = SourceSnapshot("https://example.org", "hello", "2026-09-18T00:00:00+00:00")
        self.assertEqual(first.content_hash, second.content_hash)

    def test_save_snapshot_preserves_content_and_provenance(self):
        snapshot = SourceSnapshot("https://example.org/article", "hello", "2026-09-17T00:00:00+00:00", "text/html", 200)
        with tempfile.TemporaryDirectory() as tmp:
            path = save_snapshot(snapshot, tmp)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["content"], "hello")
            self.assertEqual(payload["content_hash"], snapshot.content_hash)
            self.assertEqual(payload["provenance"], "research_source_snapshot")

    def test_attach_snapshot_metadata_requires_existing_artifact_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                artifact_id = register_research_source(store, ResearchSource("https://example.org/article"))
                snapshot = SourceSnapshot("https://example.org/article", "hello", "2026-09-17T00:00:00+00:00")
                path = Path(tmp) / "snapshot.json"
                attach_snapshot_metadata(store, artifact_id, snapshot, path)
                attach_snapshot_metadata(store, artifact_id, snapshot, path)
                row = store.conn.execute("SELECT metadata_json FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
                metadata = json.loads(row["metadata_json"])
                self.assertEqual(len(metadata["snapshots"]), 1)
            finally:
                store.close()

    def test_capture_text_rejects_oversized_response(self):
        class Headers:
            def get_content_type(self):
                return "text/plain"
            def get_content_charset(self):
                return "utf-8"

        class Response:
            headers = Headers()
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, size):
                return b"x" * size

        with patch("memory_os.research_content.urlopen", return_value=Response()):
            with self.assertRaises(ValueError):
                capture_text("https://example.org", max_bytes=3)


if __name__ == "__main__":
    unittest.main()
