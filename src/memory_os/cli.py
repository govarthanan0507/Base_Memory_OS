from __future__ import annotations

import argparse
from pathlib import Path

from .core import Memory, MemoryStore
from .discovery import scan_workspace


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

    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = MemoryStore(args.db)
    try:
        if args.command == "init":
            print(f"Initialized {Path(args.db).resolve()}")
        elif args.command == "add-memory":
            memory_id = store.add_memory(Memory(args.content, args.type, args.source, args.confidence))
            print(memory_id)
        elif args.command == "search":
            for row in store.search(args.query, args.limit):
                print(f"[{row['memory_type']}] {row['content']} ({row['source']})")
        elif args.command == "scan-projects":
            projects = scan_workspace(args.root, store)
            for project in projects:
                print(f"{project.status:17} {project.name} — {project.root}")
            print(f"Discovered {len(projects)} project(s). No files were moved or deleted.")
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
