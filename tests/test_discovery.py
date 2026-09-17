import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore
from memory_os.discovery import inspect_project, likely_project_roots, scan_workspace


class DiscoveryTests(unittest.TestCase):
    def test_scan_is_read_only_and_links_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as db_tmp:
            root = Path(tmp)
            project = root / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo Project\n", encoding="utf-8")
            (project / "main.py").write_text("print('hello')\n", encoding="utf-8")
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            store = MemoryStore(Path(db_tmp) / "memory.db")
            try:
                projects = scan_workspace(root, store)
                after = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
                self.assertEqual(before, after)
                self.assertEqual(len(projects), 1)
                self.assertEqual(store.counts(), {"memories": 0, "memory_candidates": 0, "projects": 1, "project_events": 1, "artifacts": 2, "artifact_events": 2, "relations": 2})
            finally:
                store.close()

    def test_inspect_project_reports_structure_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            root.mkdir()
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (root / "main.py").write_text("import sqlite3\nimport pathlib\n# TODO: wire CLI\n", encoding="utf-8")
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_main.py").write_text("def test_smoke(): pass\n", encoding="utf-8")
            project = inspect_project(root)
            self.assertEqual(project.status, "PARTIALLY BUILT")
            self.assertIn("pyproject.toml", project.metadata["dependency_markers"])
            self.assertIn("main.py", project.metadata["likely_entrypoints"])
            self.assertIn("sqlite3", project.metadata["import_hints"])
            evidence = project.metadata["state_evidence"]
            self.assertTrue(evidence["readme_present"] is False)
            self.assertTrue(evidence["has_tests"])
            self.assertEqual(evidence["test_file_count"], 1)
            self.assertEqual(evidence["todo_fixme_count"], 1)

    def test_git_metadata_is_read_without_running_project_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            (root / ".git" / "refs" / "heads").mkdir(parents=True)
            (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            (root / ".git" / "refs" / "heads" / "main").write_text("0123456789abcdef\n", encoding="ascii")
            project = inspect_project(root)
            self.assertTrue(project.metadata["git"]["is_git_repository"])
            self.assertEqual(project.metadata["git"]["git_branch"], "main")
            self.assertEqual(project.metadata["git"]["git_head"], "0123456789abcdef")

    def test_artifact_change_is_historical_and_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace" / "demo"
            root.mkdir(parents=True)
            source = root / "app.py"
            source.write_text("print('one')\n", encoding="utf-8")
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                scan_workspace(root.parent, store)
                artifact_id = store.conn.execute("SELECT artifact_id FROM artifacts WHERE location=?", (str(source.resolve()),)).fetchone()[0]
                self.assertEqual(len(store.list_artifact_events(artifact_id)), 1)
                source.write_text("print('two')\n", encoding="utf-8")
                scan_workspace(root.parent, store)
                events = store.list_artifact_events(artifact_id)
                self.assertEqual(len(events), 2)
                self.assertEqual(events[0]["event_type"], "changed")
                self.assertNotEqual(events[0]["old_hash"], events[0]["new_hash"])
                scan_workspace(root.parent, store)
                self.assertEqual(len(store.list_artifact_events(artifact_id)), 2)
            finally:
                store.close()

    def test_scan_is_repeatable_by_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace" / "demo"
            root.mkdir(parents=True)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "app.py").write_text("print('ok')\n", encoding="utf-8")
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                first = scan_workspace(root.parent, store)
                counts_after_first = store.counts()
                second = scan_workspace(root.parent, store)
                counts_after_second = store.counts()
                self.assertEqual(len(first), 1)
                self.assertEqual(len(second), 1)
                self.assertEqual(counts_after_first["projects"], counts_after_second["projects"])
                self.assertEqual(counts_after_first["artifacts"], counts_after_second["artifacts"])
                self.assertEqual(counts_after_second["artifact_events"], counts_after_first["artifact_events"])
            finally:
                store.close()

    def test_workspace_readme_does_not_swallow_strong_child_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outer = root / "outer"
            inner = outer / "inner"
            inner.mkdir(parents=True)
            (outer / "README.md").write_text("# Workspace\n", encoding="utf-8")
            (inner / "pyproject.toml").write_text("[project]\nname='inner'\n", encoding="utf-8")
            self.assertEqual(likely_project_roots(root), [inner.resolve()])

    def test_git_root_is_kept_when_it_is_the_workspace_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            self.assertEqual(likely_project_roots(root), [root.resolve()])

    def test_monorepo_keeps_strong_nested_project_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "monorepo"
            backend = root / "packages" / "backend"
            frontend = root / "packages" / "frontend"
            backend.mkdir(parents=True)
            frontend.mkdir(parents=True)
            (root / "package.json").write_text("{\"name\":\"workspace\"}\n", encoding="utf-8")
            (backend / "pyproject.toml").write_text("[project]\nname='backend'\n", encoding="utf-8")
            (backend / "main.py").write_text("print('backend')\n", encoding="utf-8")
            (frontend / "package.json").write_text("{\"name\":\"frontend\"}\n", encoding="utf-8")
            (frontend / "index.js").write_text("console.log('frontend')\n", encoding="utf-8")
            roots = likely_project_roots(root)
            self.assertEqual(roots, [root.resolve(), backend.resolve(), frontend.resolve()])


if __name__ == "__main__":
    unittest.main()
