from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from .core import MemoryStore


@dataclass(frozen=True)
class SourceSnapshot:
    """A locally captured representation of an external research source."""

    url: str
    content: str
    captured_at: str
    content_type: str = "text/plain"
    status_code: int | None = None
    content_hash: str = field(init=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "content_hash", hashlib.sha256(self.content.encode("utf-8")).hexdigest())


def capture_text(url: str, *, timeout: float = 10.0, max_bytes: int = 2_000_000) -> SourceSnapshot:
    """Fetch a bounded UTF-8/text response and return it as evidence.

    This helper deliberately does not summarize or interpret the response.
    The caller remains responsible for deciding whether and when external
    content should be captured.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")

    from .research import normalize_url
    from .core import utc_now

    canonical_url = normalize_url(url)
    request = Request(canonical_url, headers={"User-Agent": "Base-Memory-OS/0.1"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError(f"response exceeds max_bytes={max_bytes}")
        content_type = response.headers.get_content_type() if response.headers else "text/plain"
        charset = response.headers.get_content_charset() if response.headers else None
        encoding = charset or "utf-8"
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ValueError("response could not be decoded as text") from exc
        status = getattr(response, "status", None)
    return SourceSnapshot(canonical_url, text, utc_now(), content_type, status)


def save_snapshot(snapshot: SourceSnapshot, directory: str | Path) -> Path:
    """Persist a source snapshot as evidence without replacing the source artifact."""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"{snapshot.content_hash}.json"
    payload = {
        "url": snapshot.url,
        "captured_at": snapshot.captured_at,
        "content_type": snapshot.content_type,
        "status_code": snapshot.status_code,
        "content_hash": snapshot.content_hash,
        "content": snapshot.content,
        "metadata": snapshot.metadata,
        "provenance": "research_source_snapshot",
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return target


def attach_snapshot_metadata(store: MemoryStore, artifact_id: str, snapshot: SourceSnapshot, path: str | Path) -> None:
    """Attach snapshot provenance to an existing artifact."""
    row = store.conn.execute("SELECT metadata_json FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
    if row is None:
        raise KeyError(artifact_id)
    metadata = json.loads(row["metadata_json"])
    snapshots = list(metadata.get("snapshots", []))
    record = {
        "path": str(path),
        "captured_at": snapshot.captured_at,
        "content_hash": snapshot.content_hash,
        "content_type": snapshot.content_type,
        "status_code": snapshot.status_code,
        "provenance": "research_source_snapshot",
    }
    if record not in snapshots:
        snapshots.append(record)
    metadata["snapshots"] = snapshots
    store.conn.execute("UPDATE artifacts SET metadata_json=? WHERE artifact_id=?", (json.dumps(metadata, sort_keys=True), artifact_id))
    store.conn.commit()


__all__ = ["SourceSnapshot", "attach_snapshot_metadata", "capture_text", "save_snapshot"]
