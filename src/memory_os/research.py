from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from .core import Artifact, MemoryStore, stable_id, utc_now


@dataclass(frozen=True)
class ResearchSource:
    """An external research source preserved as an artifact.

    ``source_type`` is optional at the identity boundary: when omitted, the
    URL classifier supplies a conservative category. Explicit values remain
    supported for sources whose type cannot be inferred reliably from a URL.
    """

    url: str
    title: str = ""
    source_type: str = ""
    captured_at: str = field(default_factory=utc_now)
    metadata: dict[str, object] = field(default_factory=dict)


def normalize_url(url: str) -> str:
    """Normalize a research URL without discarding semantically meaningful query data."""
    raw = url.strip()
    if not raw:
        raise ValueError("url must be non-empty")
    parts = urlsplit(raw)
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        raise ValueError("url must be an absolute http(s) URL")
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    if not hostname:
        raise ValueError("url must contain a hostname")
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("url contains an invalid port") from exc
    netloc = hostname
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def classify_url(url: str) -> str:
    """Return a conservative source category from the URL host/path."""
    parts = urlsplit(normalize_url(url))
    host = (parts.hostname or "").lower()
    path = parts.path.lower()
    if host in {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"} or "youtube.com/shorts" in f"{host}{path}":
        return "video"
    if host in {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"}:
        return "repository"
    if path.endswith((".pdf", ".doc", ".docx", ".md", ".txt")):
        return "document"
    return "website"


def register_research_source(
    store: MemoryStore,
    source: ResearchSource,
) -> str:
    """Register a deduplicated research source as an artifact and return its stable ID."""
    canonical_url = normalize_url(source.url)
    source_type = source.source_type.strip().lower() or classify_url(canonical_url)
    artifact_id = stable_id("research", canonical_url)
    metadata = {
        **source.metadata,
        "canonical_url": canonical_url,
        "source_type": source_type,
        "captured_at": source.captured_at,
        "provenance": "research_source",
    }
    artifact = Artifact(
        name=source.title.strip() or canonical_url,
        artifact_type=source_type,
        location=canonical_url,
        artifact_id=artifact_id,
        modified_at=source.captured_at,
        metadata=metadata,
    )
    return store.add_artifact(artifact)


__all__ = ["ResearchSource", "classify_url", "normalize_url", "register_research_source"]
