import os
import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore, Project
from memory_os.project_classification import classify_artifacts_against_projects, list_candidate_details


class ProjectClassificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.store = MemoryStore(self.tmp_path / "memory.db")
        self.scan_dir = self.tmp_path / "downloads"
        self.scan_dir.mkdir()

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_scan_registers_artifacts_and_proposes_a_matching_candidate(self):
        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        (self.scan_dir / "video_understanding_notes.md").write_text(
            "Notes for the video understanding project.", encoding="utf-8"
        )

        result = classify_artifacts_against_projects(self.scan_dir, self.store)

        self.assertEqual(result.artifacts_registered, 1)
        self.assertEqual(result.candidates_created, 1)
        self.assertEqual(result.unclassified_count, 0)
        candidates = self.store.list_artifact_project_candidates("candidate")
        self.assertEqual(len(candidates), 1)
        self.assertGreaterEqual(candidates[0]["confidence"], 0.3)

    def test_file_with_no_matching_project_is_unclassified_not_forced(self):
        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        (self.scan_dir / "zzz_randomly_named_file.bin").write_bytes(b"\x00\x01binary-ish")

        result = classify_artifacts_against_projects(self.scan_dir, self.store)

        self.assertEqual(result.artifacts_registered, 1)
        self.assertEqual(result.candidates_created, 0)
        self.assertEqual(result.unclassified_count, 1)

    def test_unreadable_file_is_skipped_and_scan_continues(self):
        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        unreadable = self.scan_dir / "video_understanding_secret.md"
        readable = self.scan_dir / "video_understanding_open.md"
        unreadable.write_text("secret", encoding="utf-8")
        readable.write_text("video understanding notes", encoding="utf-8")
        os.chmod(unreadable, 0o000)
        try:
            if os.access(unreadable, os.R_OK):
                self.skipTest("running as a user that bypasses file permissions (e.g. root)")
            result = classify_artifacts_against_projects(self.scan_dir, self.store)
        finally:
            os.chmod(unreadable, 0o644)

        # Same resolved-root comparison as the symlink test above -
        # the scan records paths relative to its own resolved root.
        expected = str(Path(self.scan_dir).resolve() / "video_understanding_secret.md")
        self.assertIn(expected, result.skipped)
        self.assertEqual(result.artifacts_registered, 1)

    def test_symlink_escaping_scan_root_is_skipped_not_followed(self):
        outside = self.tmp_path / "outside"
        outside.mkdir()
        secret = outside / "video_understanding_leak.md"
        secret.write_text("this should not be reachable via the scan root", encoding="utf-8")
        link = self.scan_dir / "escape_link.md"
        try:
            link.symlink_to(secret)
        except OSError:
            self.skipTest("symlinks not supported in this environment")

        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        result = classify_artifacts_against_projects(self.scan_dir, self.store)

        # The scan resolves its root before walking (required for the
        # symlink-escape check itself), so every path it records is
        # relative to that resolved root - compare against the same
        # resolved form, not the raw `link` path. On most platforms
        # these are identical strings; on Windows, tempfile can hand
        # back an 8.3 short-form path (e.g. RUNNER~1) that `.resolve()`
        # normalizes to its long form, so an unresolved comparison can
        # legitimately differ in spelling while naming the same file.
        expected = str(Path(self.scan_dir).resolve() / "escape_link.md")
        self.assertIn(expected, result.skipped)
        self.assertEqual(result.artifacts_registered, 0)

    def test_missing_folder_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            classify_artifacts_against_projects(self.tmp_path / "does-not-exist", self.store)

    def test_rescan_of_unchanged_rejected_file_does_not_resurface(self):
        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        target = self.scan_dir / "video_understanding_notes.md"
        target.write_text("video understanding notes", encoding="utf-8")

        classify_artifacts_against_projects(self.scan_dir, self.store)
        candidate = self.store.list_artifact_project_candidates("candidate")[0]
        self.store.review_artifact_project_candidate(candidate["candidate_id"], "rejected")

        classify_artifacts_against_projects(self.scan_dir, self.store)

        self.assertEqual(self.store.list_artifact_project_candidates("candidate"), [])
        self.assertEqual(len(self.store.list_artifact_project_candidates("rejected")), 1)

    def test_no_network_import_anywhere_in_module(self):
        import memory_os.project_classification as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        for banned in ("socket", "urllib", "requests", "http.client"):
            self.assertNotIn(banned, source)

    def test_list_candidate_details_joins_artifact_and_project_names(self):
        self.store.add_project(Project("Video Understanding", str(self.tmp_path / "video-understanding")))
        (self.scan_dir / "video_understanding_notes.md").write_text(
            "video understanding notes", encoding="utf-8"
        )
        classify_artifacts_against_projects(self.scan_dir, self.store)

        details = list_candidate_details(self.store, "candidate")

        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["artifact_name"], "video_understanding_notes.md")
        self.assertEqual(details[0]["project_name"], "Video Understanding")
        self.assertGreaterEqual(details[0]["confidence"], 0.3)
        self.assertIn("candidate_id", details[0])


if __name__ == "__main__":
    unittest.main()
