from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .logging_setup import close_logging, configure_logging, get_logger
from .research import ResearchSource
from .research_pipeline import ingest_research_source
from .service import MemoryOSService, default_data_dir

logger = get_logger(__name__)

# Exceptions expected from normal invalid-input use (bad ID, missing file,
# malformed import payload) — caught with a clean one-line message rather
# than a raw traceback. Anything else is logged with a full traceback and
# re-raised: an unexpected bug should still be loud, not swallowed.
_EXPECTED_ERRORS = (KeyError, FileNotFoundError, ValueError)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-os", description="Base Memory OS CLI")
    parser.add_argument("--db", default=None, help="SQLite database path (default: OS-appropriate app-data directory)")
    parser.add_argument("--verbose", action="store_true", help="Also log DEBUG-level detail and echo log lines to stderr")
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
    classify = sub.add_parser("classify-folder", help="Scan a designated folder and propose artifact-project mappings")
    classify.add_argument("folder", type=Path)
    review_artifact = sub.add_parser("review-artifact-candidate", help="Accept or reject an artifact-project candidate")
    review_artifact.add_argument("candidate_id")
    review_artifact.add_argument("decision", choices=("accepted", "rejected"))
    signal = sub.add_parser("emotional-signal", help="Extract a behavioral/emotional signal from a conversation's own language")
    signal.add_argument("conversation_id")
    sub.add_parser("gui", help="Launch the desktop application (requires the 'gui' extra: pip install base-memory-os[gui])")
    focus = sub.add_parser("focus-guidance", help="Report idea-hopping and cross-project completion signals")
    focus.add_argument("--window", type=int, default=8)
    focus.add_argument("--limit", type=int, default=50)
    return parser


def _project_report(service: MemoryOSService, project_id: str, limit: int) -> str:
    store = service.store
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


def _research_command(service: MemoryOSService, args: argparse.Namespace) -> None:
    source = ResearchSource(url=args.url, title=args.title, source_type=args.type)
    result = ingest_research_source(
        service.store,
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


def _dispatch(service: MemoryOSService, args: argparse.Namespace) -> None:
    if args.command == "init":
        logger.info("init: database at %s", service.db_path.resolve())
        print(f"Initialized {service.db_path.resolve()}")
    elif args.command == "dashboard":
        print(service.dashboard_text())
    elif args.command == "add-memory":
        memory_id = service.add_memory(args.content, args.type, args.source, args.confidence)
        logger.info("add-memory: stored %s (type=%s, source=%s)", memory_id, args.type, args.source)
        print(memory_id)
    elif args.command == "search":
        for row in service.search_memories(args.query, args.limit):
            print(f"[{row['memory_type']}] {row['content']} ({row['source']})")
    elif args.command == "scan-projects":
        projects = service.scan_projects(args.root)
        logger.info("scan-projects: discovered %d project(s) under %s", len(projects), args.root)
        for project in projects:
            git = project.metadata.get("git", {})
            suffix = f" — git:{git.get('git_branch')}@{git.get('git_head')}" if git.get("is_git_repository") else ""
            print(f"{project.status:17} {project.name} — {project.root}{suffix}")
        print(f"Discovered {len(projects)} project(s). No files were moved or deleted.")
    elif args.command == "project-report":
        print(_project_report(service, args.project_id, args.limit))
    elif args.command == "project-evidence-view":
        print(service.project_evidence_text(args.project_id, args.limit))
    elif args.command == "import-conversation":
        conversation_id = service.import_conversation(
            args.path, fmt=args.format, source=args.source, title=args.title
        )
        logger.info("import-conversation: imported %s from %s", conversation_id, args.path)
        print(conversation_id)
    elif args.command == "import-chatgpt-export":
        count = service.import_chatgpt_export(args.path)
        logger.info("import-chatgpt-export: imported %d conversation(s) from %s", count, args.path)
        print(f"Imported {count} conversation(s)")
    elif args.command == "show-conversation":
        for row in service.get_messages(args.conversation_id):
            print(f"{row['sequence']:04d} [{row['role']}] {row['content']}")
    elif args.command == "list-conversations":
        for row in service.list_conversations(args.limit):
            print(f"{row['conversation_id']}  [{row['source']}] {row['title']}")
    elif args.command == "relate":
        service.relate(args.source_id, args.relation, args.target_id)
        logger.info("relate: %s --%s--> %s", args.source_id, args.relation, args.target_id)
        print(f"Related {args.source_id} --{args.relation}--> {args.target_id}")
    elif args.command == "link-project-conversation":
        result = service.link_project_conversation(args.project_id, args.conversation_id)
        logger.info("link-project-conversation: %s <-> %s", args.conversation_id, args.project_id)
        print(result)
    elif args.command == "reentry":
        print(service.reentry_text(args.conversation_id, args.limit))
    elif args.command == "reentry-project":
        print(service.project_brief_text(args.project_id, args.limit))
    elif args.command == "timeline-project":
        print(service.project_timeline_text(args.project_id, args.limit))
    elif args.command == "extract-candidates":
        ids = service.extract_candidates(args.conversation_id, project_id=args.project_id)
        logger.info("extract-candidates: persisted %d candidate(s) for %s", len(ids), args.conversation_id)
        print(f"Persisted {len(ids)} candidate(s)")
        for candidate_id in ids:
            print(candidate_id)
    elif args.command == "list-candidates":
        for row in service.list_candidates(args.status, args.limit):
            print(f"{row['candidate_id']} [{row['status']}] [{row['memory_type']}] {row['content']}")
    elif args.command == "review-candidate":
        result = service.review_candidate(args.candidate_id, args.decision)
        logger.info("review-candidate: %s -> %s", args.candidate_id, args.decision)
        print(result)
    elif args.command == "project-evidence":
        event_ids = service.project_evidence(args.conversation_id, args.project_id, candidate_ids=args.candidate_ids)
        logger.info("project-evidence: projected %d event(s) for %s -> %s", len(event_ids), args.conversation_id, args.project_id)
        print(f"Projected {len(event_ids)} accepted candidate event(s)")
        for event_id in event_ids:
            print(event_id)
    elif args.command in {"add-research-source", "capture-research-source"}:
        _research_command(service, args)
    elif args.command == "classify-folder":
        result = service.classify_folder(args.folder)
        logger.info(
            "classify-folder: %s -> %d artifact(s), %d candidate(s), %d unclassified, %d skipped",
            args.folder, result.artifacts_registered, result.candidates_created,
            result.unclassified_count, len(result.skipped),
        )
        print(
            f"Registered {result.artifacts_registered} artifact(s): "
            f"{result.candidates_created} candidate(s) proposed, "
            f"{result.unclassified_count} unclassified, {len(result.skipped)} skipped"
        )
    elif args.command == "review-artifact-candidate":
        result = service.review_artifact_candidate(args.candidate_id, args.decision)
        logger.info("review-artifact-candidate: %s -> %s", args.candidate_id, args.decision)
        print(result)
    elif args.command == "emotional-signal":
        print(service.emotional_signal_text(args.conversation_id))
    elif args.command == "gui":
        # Lazy import: the base CLI has zero required dependencies, and
        # PySide6 (the 'gui' extra) should never be required just to run
        # any other command.
        try:
            from .gui import run_app
        except ImportError as exc:
            raise ValueError(
                "the desktop application requires the optional 'gui' extra: "
                "pip install base-memory-os[gui]"
            ) from exc
        logger.info("gui: launched")
        run_app(service)
    elif args.command == "focus-guidance":
        logger.info("focus-guidance: window=%d limit=%d", args.window, args.limit)
        print(service.focus_guidance_text(window=args.window, limit=args.limit))


def main() -> int:
    args = build_parser().parse_args()
    db_path = Path(args.db) if args.db else default_data_dir() / "memory.db"
    configure_logging(db_path, verbose=args.verbose)
    service = MemoryOSService(db_path)
    try:
        _dispatch(service, args)
    except _EXPECTED_ERRORS as exc:
        logger.warning("command %s failed: %s", args.command, exc, exc_info=True)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception:
        logger.exception("command %s failed with an unexpected error", args.command)
        raise
    finally:
        service.close()
        close_logging()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
