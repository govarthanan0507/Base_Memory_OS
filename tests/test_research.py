import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore
from memory_os.research import ResearchSource, classify_url, normalize_url, register_research_source


class ResearchSourceTests(unittest.TestCase):
    def test_normalize_url_preserves_query_but_removes_fragment_and_default_port(self):
        self.assertEqual(
            normalize_url(" HTTPS://Example.COM:443/path/?q=one#section "),
            "https://example.com/path?q=one",
        )

    def test_classify_common_research_sources(self):
        self.assertEqual(classify_url("https://www.youtube.com/watch?v=abc"), "video")
        self.assertEqual(classify_url("https://github.com/example/project"), "repository")
        self.assertEqual(classify_url("https://example.org/paper.pdf"), "document")
        self.assertEqual(classify_url("https://example.org/article"), "website")

    def test_registration_is_deduplicated_by_canonical_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "memory.db")
            try:
                first = register_research_source(
                    store,
                    ResearchSource("https://Example.org/research/#top", title="Research"),
                )
                second = register_research_source(
                    store,
                    ResearchSource("https://example.org/research", title="Same source"),
                )
                self.assertEqual(first, second)
                artifacts = store.list_artifacts()
                self.assertEqual(len(artifacts), 1)
                self.assertEqual(artifacts[0]["location"], "https://example.org/research")
                self.assertEqual(artifacts[0]["metadata_json"].count("canonical_url"), 1)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
