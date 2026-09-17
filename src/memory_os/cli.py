from __future__ import annotations

import argparse
import json
from pathlib import Path

from .candidates import persist_candidates
from .continuity import render_project_reentry_brief, render_reentry_brief
from .continuity_os import render_continuity_dashboard
from .conversation import get_messages, list_conversations
from .core import Memory, MemoryStore
from .discovery import scan_workspace
from .evidence import link_conversation_to_project, record_conversation_candidates_as_project_events
from .importers import import_chatgpt_export, import_json, import_markdown
from .project_evidence import render_project_evidence
from .research import ResearchSource
from .research_pipeline import ingest_research_source
from .timeline import render_project_timeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-os", description="Base Memory OS CLI")
    parser.add_argument("--db", default=".memory-os/memory.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize the memory database")
    sub.add_parser("dashboard", help="Render the compact work-continuity dashboard")
    add = sub.add_parser("add-memory", help="Store a durable memory")
    add.add_argument("content")
    add.add_argument("--type", default="episodic")
    add.add_argument("--source", default="manual")
    add.add_argument("--confidence", type=float, default=1.0)
    search = sub.add_parser("search", help="Search stored memories")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    scan = sub.add_parser("scan-projects", help="Read-only project/file discovery")
    scan.add_argument("root", type=Path)
    report = sub.add_parser("project-report", help="Render deterministic structural evidence for a project")
    report.add_argument("project_id")
    report.add_argument("--limit", type=int, default=100)
    evidence_view = sub.add_parser("project-evidence-view", help="Render a compact evidence-labelled project view")
    evidence_view.add_argument("project_id")
    evidence_view.add_argument("--limit", type=int, default=50)
    imp = sub.add_parser("import-conversation", help="Import a local conversation transcript")
    imp.add_argument("path", type=Path)
    imp.add_argument("--format", choices=("json", "markdown"), default=None)
    imp.add_argument("--source", default="local")
    imp.add_argument("--title", default=None)
    chatgpt = sub.add_parser("import-chatgpt-export", help="Import a ChatGPT conversations.json export")
    chatgpt.add_argument("path", type=Path)
    show = sub.add_parser("show-conversation", help="Show normalized messages")
    show.add_argument("conversation_id")
    conversations = sub.add_parser("list-conversations", help="List imported conversations")
    conversations.add_argument("--limit", type=int, default=50)
    relate = sub.add_parser("relate", help="Create a relationship between two known IDs")
    relate.add_argument("source_id")
    relate.add_argument("relation")
    relate.add_argument("target_id")
    link = sub.add_parser("link-project-conversation", help="Explicitly link a project to a conversation")
    link.add_argument("project_id")
    link.add_argument("conversation_id")
    reentry = sub.add_parser("reentry", help="Render an evidence-based conversation re-entry brief")
    reentry.add_argument("conversation_id")
    reentry.add_argument("--limit", type=int, default=50)
    project_reentry = sub.add_parser("reentry-project", help="Render a project-centric re-entry brief")
    project_reentry.add_argument("project_id")
    project_reentry.add_argument("--limit", type=int, default=50)
    timeline = sub.add_parser("timeline-project", help="Render the recorded activity timeline for a project")
    timeline.add_argument("project_id")
    timeline.add_argument("--limit", type=int, default=100)
    candidates = sub.add_parser("extract-candidates", help="Extract and persist reviewable memory candidates")
    candidates.add_argument("conversation_id")
    candidates.add_argument("--limit", type=int, default=50)
    candidates.add_argument("--project-id", default=None)
    candidate_list = sub.add_parser("list-candidates", help="List memory candidates")
    candidate_list.add_argument("--status", choices=("candidate", "accepted", "rejected", "all"), default="candidate")
    candidate_list.add_argument("--limit", type=int, default=50)
    review = sub.add_parser("review-candidate", help="Accept or reject a memory candidate")
    review.add_argument("candidate_id")
    review.add_argument("decision", choices=("accepted", "rejected"))
    project_evidence = sub.add_parser("project-evidence", help="Project accepted conversation candidates into project history")
    project_evidence.add_argument("conversation_id")
    project_evidence.add_argument("project_id")
    project_evidence.add_argument("--candidate-id", action="append", dest="candidate_ids", default=None)
    research_add = sub.add_parser("add-research-source", help="Register a research URL and derive safe URL metadata")
    research_add.add_argument("url")
    research_add.add_argument("--title", default="")
    research_add.add_argument("--type", default="")
    research_capture = sub.add_parser("capture-research-source", help="Register and capture bounded research evidence")
    research_capture.add_argument("url")
    research_capture.add_argument("--title", default="")
    research_capture.add_argument("--type", default="")
    research_capture.add_argument("--snapshot-dir", type=Path, required=True)
    research_capture.add_argument("--timeout", type=float, default=10.0)
    research_capture.add_argument("--max-bytes", type=int, default=2_000_000)
    return parser


def _project_report(store: MemoryStore, project_id: str, limit: int) -> str:
    project = store.conn.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
    if project is None:
        raise KeyError(project_id)
    artifacts = store.conn.execute(
        "SELECT a.* FROM artifacts a JOIN relations r ON r.target_id=a.artifact_id "
        "WHERE r.source_id=? AND r.relation='contains' ORDER BY a.location LIMIT ?", (project_id, limit)
    ).fetchall()
    events = store.list_project_events(project_id, limit=limit)
    conversations = store.conn.execute(
        "SELECT r.target_id FROM relations r WHERE r.source_id=? AND r.relation='has_conversation' ORDER BY r.created_at",
        (project_id,),
    ).fetchall()
    lines = [f"# {project['name']}", "", f"- ID: `{project_id}`", f"- Root: `{project['root']}`",
             f"- Status: **{project['status']}**", f"- Confidence: {project['confidence']:.2f}"]
    if project["summary"]:
        lines += [f"- Summary: {project['summary']}"]
    metadata = json.loads(project["metadata_json"])
    lines += ["", "## Structural evidence", "", "```json", json.dumps(metadata, indent=2, sort_keys=True), "```",
              "", "## Linked conversations", ""]
    lines.extend(f"- `{row['target_id']}`" for row in conversations)
    lines += ["", "## Artifacts", ""]
    lines.extend(f"- `{row['location']}` [{row['artifact_type']}] hash={row['content_hash'] or 'unhashed'}" for row in artifacts)
    lines += ["", "## Project events", ""]
    lines.extend(f"- {row['timestamp']} — **{row['event_type']}** — {row['summary']}" for row in events)
    return "\n".join(lines)


def _research_command(store: MemoryStore, args: argparse.Namespace) -> None:
    source = ResearchSource(url=args.url, title=args.title, source_type=args.type)
    result = ingest_research_source(
        store,
        source,
        capture=args.command == "capture-research-source",
        snapshot_directory=getattr(args, "snapshot_dir", None),
        timeout=getattr(args, "timeout", 10.0),
        max_bytes=getattr(args, "max_bytes", 2_000_000),
    )
    print(json.dumps({
        "artifact_id": result.artifact_id,
        "canonical_url": result.canonical_url,
        "source_metadata": result.source_metadata,
        "snapshot_path": result.snapshot_path,
        "content_hash": result.snapshot.content_hash if result.snapshot else None,
    }, indent=2, sort_keys=True))


def main() -> int:
    args = build_parser().parse_args()
    store = MemoryStore(args.db)
    try:
        if args.command == "init":
            print(f"Initialized {Path(args.db).resolve()}")
        elif args.command == "dashboard":
            print(render_continuity_dashboard(store))
        elif args.command == "add-memory":
            print(store.add_memory(Memory(args.content, args.type, args.source, args.confidence)))
        elif args.command == "search":
            for row in store.search(args.query, args.limit):
                print(f"[{row['memory_type']}] {row['content']} ({row['source']})")
        elif args.command == "scan-projects":
            projects = scan_workspace(args.root, store)
            for project in projects:
                git = project.metadata.get("git", {})
                suffix = f" — git:{git.get('git_branch')}@{git.get('git_head')}" if git.get("is_git_repository") else ""
                print(f"{project.status:17} {project.name} — {project.root}{suffix}")
            print(f"Discovered {len(projects)} project(s). No files were moved or deleted.")
        elif args.command == "project-report":
            print(_project_report(store, args.project_id, args.limit))
        elif args.command == "project-evidence-view":
            print(render_project_evidence(store, args.project_id, args.limit))
        elif args.command == "import-conversation":
            fmt = args.format or ("json" if args.path.suffix.lower() == ".json" else "markdown")
            print(import_json(store, args.path) if fmt == "json" else import_markdown(store, args.path, source=args.source, title=args.title))
        elif args.command == "import-chatgpt-export":
            print(f"Imported {import_chatgpt_export(store, args.path)} conversation(s)")
        elif args.command == "show-conversation":
            for row in get_messages(store, args.conversation_id):
                print(f"{row['sequence']:04d} [{row['role']}] {row['content']}")
        elif args.command == "list-conversations":
            for row in list_conversations(store, args.limit):
                print(f"{row['conversation_id']}  [{row['source']}] {row['title']}")
        elif args.command == "relate":
            store.relate(args.source_id, args.relation, args.target_id)
            print(f"Related {args.source_id} --{args.relation}--> {args.target_id}")
        elif args.command == "link-project-conversation":
            print(link_conversation_to_project(store, args.conversation_id, args.project_id))
        elif args.command == "reentry":
            print(render_reentry_brief(store, args.conversation_id, args.limit))
        elif args.command == "reentry-project":
            print(render_project_reentry_brief(store, args.project_id, args.limit))
        elif args.command == "timeline-project":
            print(render_project_timeline(store, args.project_id, args.limit))
        elif args.command == "extract-candidates":
            messages = get_messages(store, args.conversation_id)
            ids = persist_candidates(store, args.conversation_id, messages, project_id=args.project_id)
            print(f"Persisted {len(ids)} candidate(s)")
            for candidate_id in ids:
                print(candidate_id)
        elif args.command == "list-candidates":
            for row in store.list_candidates(args.status, args.limit):
                print(f"{row['candidate_id']} [{row['status']}] [{row['memory_type']}] {row['content']}")
        elif args.command == "review-candidate":
            print(store.review_candidate(args.candidate_id, args.decision))
        elif args.command == "project-evidence":
            event_ids = record_conversation_candidates_as_project_events(store, args.conversation_id, args.project_id, candidate_ids=args.candidate_ids)
            print(f"Projected {len(event_ids)} accepted candidate event(s)")
            for event_id in event_ids:
                print(event_id)
        elif args.command in {"add-research-source", "capture-research-source"}:
            _research_command(store, args)
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
