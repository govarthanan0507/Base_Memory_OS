from __future__ import annotations

import argparse
from pathlib import Path

from .candidates import persist_candidates
from .continuity import render_project_reentry_brief, render_reentry_brief
from .conversation import get_messages, list_conversations
from .core import Memory, MemoryStore
from .discovery import scan_workspace
from .importers import import_chatgpt_export, import_json, import_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-os", description="Base Memory OS CLI")
    parser.add_argument("--db", default=".memory-os/memory.db", help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize the memory database")

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

    reentry = sub.add_parser("reentry", help="Render an evidence-based conversation re-entry brief")
    reentry.add_argument("conversation_id")
    reentry.add_argument("--limit", type=int, default=50)

    project_reentry = sub.add_parser("reentry-project", help="Render a project-centric re-entry brief")
    project_reentry.add_argument("project_id")
    project_reentry.add_argument("--limit", type=int, default=50)

    candidates = sub.add_parser("extract-candidates", help="Extract and persist reviewable memory candidates")
    candidates.add_argument("conversation_id")
    candidates.add_argument("--limit", type=int, default=50)

    candidate_list = sub.add_parser("list-candidates", help="List memory candidates awaiting review")
    candidate_list.add_argument("--status", choices=("candidate", "accepted", "rejected", "all"), default="candidate")
    candidate_list.add_argument("--limit", type=int, default=50)

    review = sub.add_parser("review-candidate", help="Accept or reject a memory candidate")
    review.add_argument("candidate_id")
    review.add_argument("decision", choices=("accepted", "rejected"))

    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = MemoryStore(args.db)
    try:
        if args.command == "init":
            print(f"Initialized {Path(args.db).resolve()}")
        elif args.command == "add-memory":
            print(store.add_memory(Memory(args.content, args.type, args.source, args.confidence)))
        elif args.command == "search":
            for row in store.search(args.query, args.limit):
                print(f"[{row['memory_type']}] {row['content']} ({row['source']})")
        elif args.command == "scan-projects":
            projects = scan_workspace(args.root, store)
            for project in projects:
                print(f"{project.status:17} {project.name} — {project.root}")
            print(f"Discovered {len(projects)} project(s). No files were moved or deleted.")
        elif args.command == "import-conversation":
            fmt = args.format or ("json" if args.path.suffix.lower() == ".json" else "markdown")
            if fmt == "json":
                cid = import_json(store, args.path)
            else:
                cid = import_markdown(store, args.path, source=args.source, title=args.title)
            print(cid)
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
        elif args.command == "reentry":
            print(render_reentry_brief(store, args.conversation_id, args.limit))
        elif args.command == "reentry-project":
            print(render_project_reentry_brief(store, args.project_id, args.limit))
        elif args.command == "extract-candidates":
            messages = get_messages(store, args.conversation_id)
            ids = persist_candidates(store, args.conversation_id, messages)
            print(f"Persisted {len(ids)} candidate(s)")
            for candidate_id in ids:
                print(candidate_id)
        elif args.command == "list-candidates":
            for row in store.list_candidates(args.status, args.limit):
                print(f"{row['candidate_id']} [{row['status']}] [{row['memory_type']}] {row['content']}")
        elif args.command == "review-candidate":
            print(store.review_candidate(args.candidate_id, args.decision))
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
