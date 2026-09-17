from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memory_os.cli import main
from memory_os.research_content import SourceSnapshot


class ResearchCliTests(unittest.TestCase):
    def test_add_research_source_outputs_identity_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            with patch("memory_os.research_content.urlopen") as mocked:
                with patch("sys.argv", ["memory-os", "--db", db, "add-research-source", "https://youtu.be/abc123"]):
                    self.assertEqual(main(), 0)
            mocked.assert_not_called()

    def test_capture_research_source_outputs_snapshot(self):
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
                return b"captured evidence"

        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "memory.db")
            snapshot_dir = Path(tmp) / "snapshots"
            with patch("memory_os.research_content.urlopen", return_value=Response()):
                with patch("sys.argv", [
                    "memory-os", "--db", db, "capture-research-source",
                    "https://example.org/research", "--snapshot-dir", str(snapshot_dir),
                ]):
                    self.assertEqual(main(), 0)
            self.assertEqual(len(list(snapshot_dir.glob("*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
