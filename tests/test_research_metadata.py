import unittest

from memory_os.research_metadata import extract_source_metadata


class ResearchMetadataTests(unittest.TestCase):
    def test_youtube_video_identity_from_url(self):
        metadata = extract_source_metadata("HTTPS://WWW.YOUTUBE.COM/watch?v=abc123#comments")
        self.assertEqual(metadata["provider"], "youtube")
        self.assertEqual(metadata["resource_id"], "abc123")
        self.assertEqual(metadata["resource_kind"], "video")
        self.assertNotIn("#", metadata["canonical_url"])

    def test_youtube_short_identity_from_url(self):
        metadata = extract_source_metadata("https://youtube.com/shorts/xyz789")
        self.assertEqual(metadata["provider"], "youtube")
        self.assertEqual(metadata["resource_id"], "xyz789")
        self.assertEqual(metadata["resource_kind"], "short")

    def test_repository_identity_from_url(self):
        metadata = extract_source_metadata("https://github.com/Example/Project.git/")
        self.assertEqual(metadata["provider"], "github")
        self.assertEqual(metadata["owner"], "Example")
        self.assertEqual(metadata["repository"], "Project")
        self.assertEqual(metadata["resource_kind"], "repository")

    def test_unknown_site_returns_only_safe_url_hints(self):
        metadata = extract_source_metadata("https://example.org/article")
        self.assertEqual(metadata["canonical_url"], "https://example.org/article")
        self.assertEqual(metadata["host"], "example.org")
        self.assertNotIn("resource_id", metadata)


if __name__ == "__main__":
    unittest.main()
