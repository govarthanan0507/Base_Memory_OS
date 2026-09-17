from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import MemoryStore
from .research import ResearchSource, register_research_source
from .research_content import SourceSnapshot, attach_snapshot_metadata, capture_text, save_snapshot
from .research_metadata import extract_source_metadata


@dataclass(frozen=True)
class ResearchIngestResult:
    """Complete result of a research-source ingestion operation."""

    artifact_id: str
    canonical_url: str
    source_metadata: dict[str, str]
    snapshot: SourceSnapshot | None = None
    snapshot_path: str | None = None


def ingest_research_source(
    store: MemoryStore,
    source: ResearchSource,
    *,
    snapshot_directory: str | Path | None = None,
    capture: bool = False,
    timeout: float = 10.0,
    max_bytes: int = 2_000_000,
) -> ResearchIngestResult:
    """Register a source and optionally capture bounded evidence.

    The stages are deliberately explicit: registration and URL metadata are
    local observations; capture is the only stage that performs network I/O;
    snapshot persistence and provenance attachment happen only after a
    successful capture.
    """
    artifact_id = register_research_source(store, source)
    source_metadata = extract_source_metadata(source.url)

    if not capture:
        return ResearchIngestResult(
            artifact_id=artifact_id,
            canonical_url=source_metadata["canonical_url"],
            source_metadata=source_metadata,
        )

    if snapshot_directory is None:
        raise ValueError("snapshot_directory is required when capture=True")

    snapshot = capture_text(source_metadata["canonical_url"], timeout=timeout, max_bytes=max_bytes)
    snapshot_path = save_snapshot(snapshot, snapshot_directory)
    attach_snapshot_metadata(store, artifact_id, snapshot, snapshot_path)
    return ResearchIngestResult(
        artifact_id=artifact_id,
        canonical_url=source_metadata["canonical_url"],
        source_metadata=source_metadata,
        snapshot=snapshot,
        snapshot_path=str(snapshot_path),
    )


__all__ = ["ResearchIngestResult", "ingest_research_source"]
