from __future__ import annotations

from urllib.parse import urlsplit

from .research import normalize_url


def extract_source_metadata(url: str) -> dict[str, str]:
    """Extract provider-neutral identity hints from a URL without fetching it.

    Returned fields are observations from URL structure only. They are not
    claims about the remote resource's current content.
    """
    canonical = normalize_url(url)
    parts = urlsplit(canonical)
    host = (parts.hostname or "").lower()
    path_parts = [part for part in parts.path.split("/") if part]
    result: dict[str, str] = {"canonical_url": canonical, "host": host}

    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        query = dict(pair.split("=", 1) for pair in parts.query.split("&") if "=" in pair)
        if len(path_parts) >= 2 and path_parts[0].lower() == "shorts":
            result["provider"] = "youtube"
            result["resource_id"] = path_parts[1]
            result["resource_kind"] = "short"
        elif query.get("v"):
            result["provider"] = "youtube"
            result["resource_id"] = query["v"]
            result["resource_kind"] = "video"
    elif host == "youtu.be" and path_parts:
        result["provider"] = "youtube"
        result["resource_id"] = path_parts[0]
        result["resource_kind"] = "video"
    elif host in {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"} and len(path_parts) >= 2:
        result["provider"] = "github" if "github" in host else "gitlab"
        result["owner"] = path_parts[0]
        result["repository"] = path_parts[1].removesuffix(".git")
        result["resource_kind"] = "repository"

    return result


__all__ = ["extract_source_metadata"]
