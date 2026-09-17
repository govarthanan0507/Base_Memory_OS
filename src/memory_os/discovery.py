from __future__ import annotations
import ast, hashlib, os, re
from datetime import datetime, timezone
from pathlib import Path
from .core import Artifact, MemoryStore, Project
PROJECT_MARKERS={"pyproject.toml","package.json","Cargo.toml","go.mod","requirements.txt","Pipfile","poetry.lock","composer.json","pom.xml","build.gradle","CMakeLists.txt","README.md",".git"}
STRONG_PROJECT_MARKERS=PROJECT_MARKERS-{"README.md"}
DEPENDENCY_MARKERS=PROJECT_MARKERS-{"README.md",".git","CMakeLists.txt"}
IGNORED_DIRS={".git",".venv","venv","node_modules","__pycache__",".mypy_cache",".pytest_cache","dist","build"}
CODE_EXTENSIONS={".py",".js",".ts",".tsx",".jsx",".java",".go",".rs",".cpp",".c",".cs",".rb",".php",".swift",".kt"}
MAX_HASH_BYTES=20*1024*1024; MAX_ANALYSIS_BYTES=512*1024
ENTRYPOINT_NAMES={"main.py","app.py","server.py","cli.py","index.js","index.ts","main.go","main.rs","Program.cs"}
TEST_DIR_NAMES={"test","tests","spec","specs"}; TEST_FILE_RE=re.compile(r"(^test_.*\.(py|js|ts|tsx|jsx)$|.*(_test|\.test|\.spec)\.(py|js|ts|tsx|jsx)$)",re.I); TODO_RE=re.compile(r"\b(TODO|FIXME)\b",re.I)

def file_hash(path:Path,chunk_size:int=1024*1024)->str:
    digest=hashlib.sha256()
    with path.open("rb") as fh:
        while chunk:=fh.read(chunk_size): digest.update(chunk)
    return digest.hexdigest()

def _git_evidence(root:Path):
    gd=root/".git"
    if not gd.is_dir(): return {"is_git_repository":False}
    e={"is_git_repository":True}
    try:
        head=(gd/"HEAD").read_text(encoding="utf-8",errors="replace").strip()
        if head.startswith("ref: "):
            ref=head[5:].strip(); e["git_branch"]=ref.removeprefix("refs/heads/"); rp=gd/ref
            if rp.is_file(): e["git_head"]=rp.read_text(encoding="ascii",errors="replace").strip()
            else:
                packed=gd/"packed-refs"
                if packed.is_file():
                    for line in packed.read_text(encoding="ascii",errors="replace").splitlines():
                        if line and not line.startswith(("#","^")):
                            commit,pr=line.split(" ",1)
                            if pr.strip()==ref: e["git_head"]=commit.strip(); break
        elif head: e.update(git_head=head,git_head_state="detached")
    except OSError: e["git_metadata_readable"]=False
    return e

def likely_project_roots(root:Path)->list[Path]:
    root=root.resolve(); candidates=[]
    for current,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        p=Path(current); markers=set(files)|({".git"} if (p/".git").is_dir() else set()); has_code=any(Path(n).suffix.lower() in CODE_EXTENSIONS for n in files)
        if markers&PROJECT_MARKERS or has_code:
            strong=bool(markers&STRONG_PROJECT_MARKERS)
            if strong or has_code: candidates.append((p,strong))
    candidates.sort(key=lambda x:(len(x[0].parts),str(x[0]))); strong=[p for p,s in candidates if s]; selected=[]
    for candidate,_ in candidates:
        if any(candidate in s.parents for s in strong): continue
        if not any(parent in candidate.parents for parent in selected): selected.append(candidate)
    if not selected and (root/".git").is_dir(): selected.append(root)
    return selected

def _import_hints(path:Path):
    try:
        if path.suffix.lower()!=".py" or path.stat().st_size>MAX_ANALYSIS_BYTES:return []
        tree=ast.parse(path.read_text(encoding="utf-8",errors="replace"))
    except (OSError,SyntaxError,UnicodeError):return []
    out=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):out.extend(a.name.split(".")[0] for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module:out.append(n.module.split(".")[0])
    return sorted(set(out))[:20]

def _text_import_hints(path:Path):
    try:
        if path.suffix.lower() not in {".js",".ts",".tsx",".jsx"} or path.stat().st_size>MAX_ANALYSIS_BYTES:return []
        text=path.read_text(encoding="utf-8",errors="replace")
    except OSError:return []
    return sorted({x.split("/")[0] for x in re.findall(r'''(?:from|require\()\s*["']([^"']+)''',text)})[:20]

def _state_evidence(root,code_files):
    tests=[];todo=0;recent=0;now=datetime.now(timezone.utc).timestamp()
    for p in code_files:
        try:
            if p.parent.name.lower() in TEST_DIR_NAMES or TEST_FILE_RE.match(p.name):tests.append(p)
            st=p.stat();recent+=now-st.st_mtime<=30*86400
            if st.st_size<=MAX_ANALYSIS_BYTES:todo+=len(TODO_RE.findall(p.read_text(encoding="utf-8",errors="replace")))
        except (OSError,UnicodeError):pass
    return {"readme_present":(root/"README.md").is_file(),"has_tests":bool(tests),"test_file_count":len(tests),"todo_fixme_count":todo,"recent_code_file_count_30d":recent,"code_activity_ratio_30d":round(recent/len(code_files),3) if code_files else 0.0}

def inspect_project(root:Path)->Project:
    files=[];code=[];markers=[];entry=[];imports=set();total=0
    for current,dirs,names in os.walk(root):
        dirs[:]=[d for d in dirs if d not in IGNORED_DIRS]
        for name in names:
            p=Path(current)/name
            try:st=p.stat()
            except OSError:continue
            files.append(p);total+=st.st_size
            if p.suffix.lower() in CODE_EXTENSIONS:
                code.append(p)
                if name in ENTRYPOINT_NAMES:entry.append(str(p.relative_to(root)))
                imports.update(_import_hints(p));imports.update(_text_import_hints(p))
            if name in PROJECT_MARKERS:markers.append(name)
    summary="";readme=root/"README.md"
    if readme.is_file():
        try:summary=next((x.lstrip("# ").strip() for x in readme.read_text(encoding="utf-8",errors="replace").splitlines() if x.strip() and not x.startswith("```")),"")
        except OSError:pass
    metadata={"file_count":len(files),"code_file_count":len(code),"total_bytes":total,"markers":sorted(set(markers)),"dependency_markers":sorted(set(markers)&DEPENDENCY_MARKERS),"likely_entrypoints":sorted(set(entry)),"import_hints":sorted(imports),"git":_git_evidence(root),"state_evidence":_state_evidence(root,code),"discovery_version":"0.4.0"}
    confidence=.45+(.15 if code else 0)+(.1 if summary else 0)+(.1 if len(markers)>1 else 0)+(.05 if entry else 0)+(.05 if set(markers)&DEPENDENCY_MARKERS else 0)
    return Project(summary or root.name.replace("_"," ").replace("-"," ").strip().title(),str(root),"PARTIALLY BUILT" if code else "DISCOVERED",min(.95,confidence),summary=summary,metadata=metadata)

def scan_workspace(root:str|Path,store:MemoryStore)->list[Project]:
    projects=[]
    for pr in likely_project_roots(Path(root)):
        project=inspect_project(pr);pid=store.add_project(project);projects.append(project)
        for current,dirs,names in os.walk(pr):
            dirs[:]=[d for d in dirs if d not in IGNORED_DIRS]
            for name in names:
                p=Path(current)/name
                try:st=p.stat()
                except OSError:continue
                aid=store.add_artifact(Artifact(name,"code" if p.suffix.lower() in CODE_EXTENSIONS else "file",str(p.resolve()),content_hash=file_hash(p) if st.st_size<=MAX_HASH_BYTES else None,modified_at=datetime.fromtimestamp(st.st_mtime,tz=timezone.utc).isoformat(),metadata={"project_root":str(pr.resolve())}));store.relate(pid,"contains",aid)
    return projects

__all__=["inspect_project","likely_project_roots","scan_workspace","file_hash"]
