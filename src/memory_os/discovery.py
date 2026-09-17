from __future__ import annotations

import ast
import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .core import Artifact, MemoryStore, Project

PROJECT_MARKERS = {"pyproject.toml", "package.json", "Cargo.toml", "go.mod", "requirements.txt", "Pipfile", "poetry.lock", "composer.json", "pom.xml", "build.gradle", "CMakeLists.txt", "README.md", ".git"}
STRONG_PROJECT_MARKERS = PROJECT_MARKERS - {"README.md"}
DEPENDENCY_MARKERS = {"pyproject.toml", "package.json", "Cargo.toml", "go.mod", "requirements.txt", "Pipfile", "poetry.lock", "composer.json", "pom.xml", "build.gradle"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp", ".c", ".cs", ".rb", ".php", ".swift", ".kt"}
MAX_HASH_BYTES = 20 * 1024 * 1024
MAX_ANALYSIS_BYTES = 512 * 1024
ENTRYPOINT_NAMES = {"main.py", "app.py", "server.py", "cli.py", "index.js", "index.ts", "main.go", "main.rs", "Program.cs"}
TEST_DIR_NAMES = {"test", "tests", "spec", "specs"}
TEST_FILE_RE = re.compile(r"(^test_.*\.(py|js|ts|tsx|jsx)$|.*(_test|\.test|\.spec)\.(py|js|ts|tsx|jsx)$)", re.I)
TODO_RE = re.compile(r"\b(TODO|FIXME)\b", re.I)


def file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _git_evidence(root: Path) -> dict[str, str | bool]:
    git_dir = root / ".git"
    if not git_dir.is_dir():
        return {"is_git_repository": False}
    evidence: dict[str, str | bool] = {"is_git_repository": True}
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
        if head.startswith("ref: "):
            ref = head[6:].strip()
            evidence["git_branch"] = ref.removeprefix("refs/heads/")
            ref_path = git_dir / ref
            if ref_path.is_file():
                evidence["git_head"] = ref_path.read_text(encoding="ascii", errors="replace").strip()
            else:
                packed = git_dir / "packed-refs"
                if packed.is_file():
                    for line in packed.read_text(encoding="ascii", errors="replace").splitlines():
                        if line and not line.startswith("#") and not line.startswith("^"):
                            commit, packed_ref = line.split(" ", 1)
                            if packed_ref.strip() == ref:
                                evidence["git_head"] = commit.strip()
                                break
        elif head:
            evidence["git_head"] = head
            evidence["git_head_state"] = "detached"
    except OSError:
        evidence["git_metadata_readable"] = False
    return evidence


def likely_project_roots(root: Path) -> list[Path]:
    """Return non-overlapping project roots, preferring strong project markers.

    README-only directories are treated as project roots only when they contain
    code or no stronger project root exists below them. This prevents a
    workspace-level README from swallowing real child projects.
    """
    root = root.resolve()
    candidates: list[tuple[Path, bool]] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        current_path = Path(current)
        markers = set(files) | ({".git"} if (current_path / ".git").is_dir() else set())
        if markers & PROJECT_MARKERS:
            strong = bool(markers & STRONG_PROJECT_MARKERS)
            has_code = any(Path(name).suffix.lower() in CODE_EXTENSIONS for name in files)
            if strong or has_code:
                candidates.append((current_path, strong))

    candidates.sort(key=lambda item: (len(item[0].parts), str(item[0])))
    strong_roots = [path for path, strong in candidates if strong]
    selected: list[Path] = []
    for candidate, _strong in candidates:
        # A weaker outer README/code root is not selected if it contains a
        # stronger descendant. The descendant is the more useful project unit.
        if any(candidate in strong_root.parents for strong_root in strong_roots):
            continue
        if not any(parent in candidate.parents for parent in selected):
            selected.append(candidate)
    # If the scan itself is a strong project root, keep it rather than requiring
    # a child project marker.
    if not selected and (root / ".git").is_dir():
        selected.append(root)
    return selected


def _import_hints(path: Path) -> list[str]:
    try:
        if path.suffix.lower() != ".py" or path.stat().st_size > MAX_ANALYSIS_BYTES:
            return []
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, UnicodeError):
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return sorted(set(imports))[:20]


def _text_import_hints(path: Path) -> list[str]:
    try:
        if path.suffix.lower() not in {".js", ".ts", ".tsx", ".jsx"} or path.stat().st_size > MAX_ANALYSIS_BYTES:
            return []
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    found = re.findall(r'''(?:from|require\()\s*["']([^"']+)''', text)
    return sorted({item.split("/")[0] for item in found})[:20]


def _iso_mtime(path: Path, stat: os.stat_result) -> str:
    return datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()


def _state_evidence(root: Path, files: list[Path], code_files: list[Path]) -> dict[str, object]:
    test_files = []
    todo_count = 0
    recent_code_files = 0
    now = datetime.now(timezone.utc).timestamp()
    for path in code_files:
        try:
            if path.parent.name.lower() in TEST_DIR_NAMES or TEST_FILE_RE.match(path.name):
                test_files.append(path)
            stat = path.stat()
            if now - stat.st_mtime <= 30 * 24 * 60 * 60:
                recent_code_files += 1
            if stat.st_size <= MAX_ANALYSIS_BYTES:
                todo_count += len(TODO_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
        except (OSError, UnicodeError):
            continue
    return {
        "readme_present": (root / "README.md").is_file(),
        "has_tests": bool(test_files),
        "test_file_count": len(test_files),
        "todo_fixme_count": todo_count,
        "recent_code_file_count_30d": recent_code_files,
        "code_activity_ratio_30d": round(recent_code_files / len(code_files), 3) if code_files else 0.0,
    }


def inspect_project(root: Path) -> Project:
    files, code_files, markers, entrypoints, imports = [], [], [], [], set()
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
                if name in ENTRYPOINT_NAMES:
                    entrypoints.append(str(path.relative_to(root)))
                imports.update(_import_hints(path))
                imports.update(_text_import_hints(path))
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
    git = _git_evidence(root)
    state_evidence = _state_evidence(root, files, code_files)
    status = "PARTIALLY BUILT" if code_files else "DISCOVERED"
    metadata = {
        "file_count": len(files),
        "code_file_count": len(code_files),
        "total_bytes": total_bytes,
        "markers": sorted(set(markers)),
        "dependency_markers": sorted(set(markers) & DEPENDENCY_MARKERS),
        "likely_entrypoints": sorted(set(entrypoints)),
        "import_hints": sorted(imports),
        "git": git,
        "state_evidence": state_evidence,
        "discovery_version": "0.4.0",
    }
    evidence = 0.45 + (0.15 if code_files else 0) + (0.1 if summary else 0) + (0.1 if len(markers) > 1 else 0)
    evidence += min(0.1, 0.05 if entrypoints else 0) + min(0.1, 0.05 if (set(markers) & DEPENDENCY_MARKERS) else 0)
    confidence = min(0.95, evidence)
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
                modified_at = _iso_mtime(path, stat)
                artifact_id = store.add_artifact(Artifact(name=name, artifact_type="code" if path.suffix.lower() in CODE_EXTENSIONS else "file", location=str(path.resolve()), content_hash=file_hash(path) if stat.st_size <= MAX_HASH_BYTES else None, modified_at=modified_at, metadata={"project_root": str(project_root.resolve())}))
                store.relate(project_id, "contains", artifact_id)
    return projects


__all__ = ["inspect_project", "likely_project_roots", "scan_workspace", "file_hash"]
