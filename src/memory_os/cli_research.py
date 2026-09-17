from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import MemoryStore
from .research import ResearchSource
from .research_pipeline import ingest_research_source


def build_research_parser(parser: argparse.ArgumentParser) -> None:
    add = parser.add_parser("add-research-source", help="Register a research URL and derive safe URL metadata")
    add.add_argument("url")
    add.add_argument("--title", default="")
    add.add_argument("--type", default="")
    add.add_argument("--source", default="manual")
    capture = parser.add_parser("capture-research-source", help="Register and capture bounded research evidence")
    capture.add_argument("url")
    capture.add_argument("--title", default="")
    capture.add_argument("--type", default="")
    capture.add_argument("--snapshot-dir", type=Path, required=True)
    capture.add_argument("--timeout", type=float, default=10.0)
    capture.add_argument("--max-bytes", type=int, default=2_000_000)


def handle_research_command(args: argparse.Namespace, store: MemoryStore) -> bool:
    if args.command not in {"add-research-source", "capture-research-source"}:
        return False
    source = ResearchSource(url=args.url, title=args.title, source_type=args.type)
    result = ingest_research_source(
        store,
        source,
        capture=args.command == "capture-research-source",
        snapshot_directory=getattr(args, "snapshot_dir", None),
        timeout=getattr(args, "timeout", 10.0),
        max_bytes=getattr(args, "max_bytes", 2_000_000),
    )
    payload = {
        "artifact_id": result.artifact_id,
        "canonical_url": result.canonical_url,
        "source_metadata": result.source_metadata,
        "snapshot_path": result.snapshot_path,
        "content_hash": result.snapshot.content_hash if result.snapshot else None,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return True


__all__ = ["build_research_parser", "handle_research_command"]
