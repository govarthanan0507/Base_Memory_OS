import tempfile
import unittest
from pathlib import Path

from memory_os.core import MemoryStore
from memory_os.discovery import likely_project_roots, scan_workspace


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
                self.assertEqual(store.counts(), {"memories": 0, "projects": 1, "artifacts": 2, "relations": 2})
            finally:
                store.close()

    def test_nested_project_does_not_duplicate_outer_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outer = root / "outer"
            inner = outer / "inner"
            inner.mkdir(parents=True)
            (outer / "README.md").write_text("# Outer\n", encoding="utf-8")
            (inner / "pyproject.toml").write_text("[project]\nname='inner'\n", encoding="utf-8")
            self.assertEqual(likely_project_roots(root), [outer.resolve()])


if __name__ == "__main__":
    unittest.main()
