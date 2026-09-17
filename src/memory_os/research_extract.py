from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape
from urllib.parse import urljoin

from .research import normalize_url
from .research_content import SourceSnapshot


_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_HEADING_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
_LINK_RE = re.compile(r"<a[^>]+href=[\"']([^\"']+)[\"']", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class ResearchObservations:
    """Deterministic structural observations extracted from captured evidence."""

    source_url: str
    title: str = ""
    headings: tuple[str, ...] = ()
    links: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


def _clean_text(value: str) -> str:
    return " ".join(unescape(_TAG_RE.sub(" ", value)).split())


def extract_observations(snapshot: SourceSnapshot) -> ResearchObservations:
    """Extract bounded, non-semantic structure from a captured text snapshot.

    This function does not call the network and does not claim that an observed
    title, link or heading is authoritative. Relative links are resolved
    against the captured source URL; malformed URLs are ignored.
    """
    content = snapshot.content
    title_match = _TITLE_RE.search(content)
    title = _clean_text(title_match.group(1)) if title_match else ""
    headings = tuple(
        text for _, raw in _HEADING_RE.findall(content)
        if (text := _clean_text(raw))
    )

    links: list[str] = []
    for href in _LINK_RE.findall(content):
        candidate = href.strip()
        if not candidate:
            continue
        try:
            absolute = urljoin(snapshot.url, candidate)
            links.append(normalize_url(absolute))
        except (TypeError, ValueError):
            continue

    urls: list[str] = []
    for raw in _URL_RE.findall(content):
        candidate = raw.rstrip(".,;:)]}>")
        try:
            urls.append(normalize_url(candidate))
        except ValueError:
            continue

    return ResearchObservations(
        source_url=snapshot.url,
        title=title,
        headings=tuple(dict.fromkeys(headings)),
        links=tuple(dict.fromkeys(links)),
        urls=tuple(dict.fromkeys(urls)),
        metadata={
            "provenance": "research_snapshot_observation",
            "content_hash": snapshot.content_hash,
            "captured_at": snapshot.captured_at,
        },
    )


__all__ = ["ResearchObservations", "extract_observations"]
