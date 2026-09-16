from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .core import Artifact, MemoryStore, Project

PROJECT_MARKERS = {"pyproject.toml", "package.json", "Cargo.toml", "go.mod", "requirements.txt", "Pipfile", "poetry.lock", "composer.json", "pom.xml", "build.gradle", "CMakeLists.txt", "README.md", ".git"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp", ".c", ".cs", ".rb", ".php", ".swift", ".kt"}
MAX_HASH_BYTES = 20 * 1024 * 1024


def file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def likely_project_roots(root: Path) -> list[Path]:
    root = root.resolve()
    candidates = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        markers = set(files) | ({".git"} if (Path(current) / ".git").is_dir() else set())
        if markers & PROJECT_MARKERS:
            candidates.append(Path(current))
    candidates.sort(key=lambda p: (len(p.parts), str(p)))
    selected = []
    for candidate in candidates:
        if not any(parent in candidate.parents for parent in selected):
            selected.append(candidate)
    return selected


def inspect_project(root: Path) -> Project:
    files, code_files, markers = [], [], []
    total_bytes = 0
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for name in names:
            path = Path(current) / name
            try:
                stat = path.stat()
            except OSError:
                continue
            files.append(path)
            total_bytes += stat.st_size
            if path.suffix.lower() in CODE_EXTENSIONS:
                code_files.append(path)
            if name in PROJECT_MARKERS:
                markers.append(name)
    summary = ""
    readme = root / "README.md"
    if readme.is_file():
        try:
            lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
            summary = next((line.lstrip("# ").strip() for line in lines if line.strip() and not line.startswith("```")), "")
        except OSError:
            pass
    name = summary or root.name.replace("_", " ").replace("-", " ").strip().title()
    status = "PARTIALLY BUILT" if code_files else "DISCOVERED"
    metadata = {"file_count": len(files), "code_file_count": len(code_files), "total_bytes": total_bytes, "markers": sorted(set(markers)), "discovery_version": "0.1.1"}
    confidence = min(0.95, 0.45 + (0.15 if code_files else 0) + (0.1 if summary else 0) + (0.1 if len(markers) > 1 else 0))
    return Project(name=name, root=str(root), status=status, confidence=confidence, summary=summary, metadata=metadata)


def scan_workspace(root: str | Path, store: MemoryStore) -> list[Project]:
    roots = likely_project_roots(Path(root))
    projects = []
    for project_root in roots:
        project = inspect_project(project_root)
        project_id = store.add_project(project)
        projects.append(project)
        for current, dirs, names in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for name in names:
                path = Path(current) / name
                try:
                    stat = path.stat()
                except OSError:
                    continue
                artifact_id = store.add_artifact(Artifact(name=name, artifact_type="code" if path.suffix.lower() in CODE_EXTENSIONS else "file", location=str(path.resolve()), content_hash=file_hash(path) if stat.st_size <= MAX_HASH_BYTES else None, modified_at=str(stat.st_mtime), metadata={"project_root": str(project_root.resolve())}))
                store.relate(project_id, "contains", artifact_id)
    return projects


__all__ = ["inspect_project", "likely_project_roots", "scan_workspace", "file_hash"]
