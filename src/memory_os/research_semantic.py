from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from .research import normalize_url
from .research_extract import ResearchObservations
from .research_content import SourceSnapshot


_GITHUB_RE = re.compile(r"https?://(?:www\.)?github\.com/[^\s<>\"']+", re.IGNORECASE)
_GITLAB_RE = re.compile(r"https?://(?:www\.)?gitlab\.com/[^\s<>\"']+", re.IGNORECASE)
_TOOL_RE = re.compile(r"\b(?:tool|library|framework|platform|service|software)\s*[:\-]?\s*([A-Za-z][A-Za-z0-9_.+\-/ ]{1,80})", re.IGNORECASE)
_IDEA_RE = re.compile(r"\b(?:idea|project|approach|concept)\s*[:\-]\s*([^.!?\n]{3,160})", re.IGNORECASE)


@dataclass(frozen=True)
class ResearchCandidate:
    """A reviewable semantic candidate grounded in one captured source."""

    kind: str
    value: str
    evidence: str
    source_url: str
    content_hash: str
    captured_at: str
    confidence: float = 0.5
    metadata: dict[str, str] = field(default_factory=dict)


def _candidate(kind: str, value: str, evidence: str, snapshot: SourceSnapshot, confidence: float) -> ResearchCandidate:
    return ResearchCandidate(
        kind=kind,
        value=value.strip(),
        evidence=evidence.strip(),
        source_url=snapshot.url,
        content_hash=snapshot.content_hash,
        captured_at=snapshot.captured_at,
        confidence=confidence,
        metadata={
            "provenance": "research_snapshot_semantic_candidate",
            "review_status": "candidate",
        },
    )


def _repository_candidates(observations: ResearchObservations, snapshot: SourceSnapshot) -> list[ResearchCandidate]:
    results: list[ResearchCandidate] = []
    for url in (*observations.links, *observations.urls):
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        if host not in {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"}:
            continue
        try:
            canonical = normalize_url(url)
        except ValueError:
            continue
        path = [part for part in urlsplit(canonical).path.split("/") if part]
        if len(path) < 2:
            continue
        name = f"{path[0]}/{path[1].removesuffix('.git')}"
        results.append(_candidate("repository", name, canonical, snapshot, 0.98))
    return results


def _tool_candidates(snapshot: SourceSnapshot) -> list[ResearchCandidate]:
    results: list[ResearchCandidate] = []
    for match in _TOOL_RE.finditer(snapshot.content):
        value = " ".join(match.group(1).split()).strip(" ,:;")
        if value:
            results.append(_candidate("tool", value, match.group(0), snapshot, 0.65))
    return results


def _idea_candidates(snapshot: SourceSnapshot) -> list[ResearchCandidate]:
    results: list[ResearchCandidate] = []
    for match in _IDEA_RE.finditer(snapshot.content):
        value = " ".join(match.group(1).split())
        if value:
            results.append(_candidate("idea", value, match.group(0), snapshot, 0.60))
    return results


def _topic_candidates(observations: ResearchObservations, snapshot: SourceSnapshot) -> list[ResearchCandidate]:
    """Expose source topics as candidates, not authoritative summaries."""
    results: list[ResearchCandidate] = []
    if observations.title:
        results.append(_candidate("topic", observations.title, observations.title, snapshot, 0.55))
    for heading in observations.headings:
        if heading and heading != observations.title:
            results.append(_candidate("topic", heading, heading, snapshot, 0.50))
    return results


def extract_semantic_candidates(snapshot: SourceSnapshot, observations: ResearchObservations) -> tuple[ResearchCandidate, ...]:
    """Extract conservative, reviewable candidates from preserved research evidence.

    This is deliberately heuristic and deterministic. It does not call a model,
    browse the network, verify claims, or turn a candidate into durable memory.
    Every result points back to the exact captured snapshot hash and timestamp.
    """
    candidates = [
        *_repository_candidates(observations, snapshot),
        *_tool_candidates(snapshot),
        *_idea_candidates(snapshot),
        *_topic_candidates(observations, snapshot),
    ]
    unique: dict[tuple[str, str, str], ResearchCandidate] = {}
    for item in candidates:
        key = (item.kind, item.value.casefold(), item.evidence)
        unique.setdefault(key, item)
    return tuple(unique.values())


__all__ = ["ResearchCandidate", "extract_semantic_candidates"]
