import unittest

from memory_os.research_content import SourceSnapshot
from memory_os.research_extract import extract_observations


class ResearchExtractTests(unittest.TestCase):
    def test_extracts_title_headings_links_and_urls_without_network(self):
        snapshot = SourceSnapshot(
            "https://example.org/articles/start",
            """<html><head><title>Research Notes</title></head>
            <body><h1>Overview</h1><h2>Overview</h2>
            <a href='/repo'>Repository</a>
            <p>See https://github.com/example/project.</p></body></html>""",
            "2026-09-17T00:00:00+00:00",
            "text/html",
            200,
        )
        observations = extract_observations(snapshot)
        self.assertEqual(observations.title, "Research Notes")
        self.assertEqual(observations.headings, ("Overview",))
        self.assertEqual(observations.links, ("https://example.org/repo",))
        self.assertEqual(observations.urls, ("https://github.com/example/project",))
        self.assertEqual(observations.metadata["content_hash"], snapshot.content_hash)

    def test_ignores_malformed_and_empty_links(self):
        snapshot = SourceSnapshot(
            "https://example.org/",
            "<a href=''>empty</a><a href='https://[bad'>bad</a>",
            "2026-09-17T00:00:00+00:00",
        )
        observations = extract_observations(snapshot)
        self.assertEqual(observations.links, ())

    def test_deduplicates_structural_observations(self):
        snapshot = SourceSnapshot(
            "https://example.org/",
            "<h1>A</h1><h1>A</h1><a href='/x'>x</a><a href='/x'>x</a>",
            "2026-09-17T00:00:00+00:00",
        )
        observations = extract_observations(snapshot)
        self.assertEqual(observations.headings, ("A",))
        self.assertEqual(observations.links, ("https://example.org/x",))


if __name__ == "__main__":
    unittest.main()
