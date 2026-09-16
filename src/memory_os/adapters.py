from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .conversation import Conversation, Message


def _text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        parts = content.get("parts")
        if isinstance(parts, list):
            return "\n".join(str(part) for part in parts if isinstance(part, (str, int, float))).strip()
        text = content.get("text")
        if isinstance(text, str):
            return text.strip()
    if isinstance(content, list):
        return "\n".join(str(part) for part in content if isinstance(part, (str, int, float))).strip()
    return ""


def _iso_from_epoch(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def chatgpt_conversation(data: dict[str, Any]) -> Conversation:
    """Normalize one common ChatGPT export conversation object."""
    mapping = data.get("mapping")
    if not isinstance(mapping, dict):
        raise ValueError("ChatGPT conversation requires a mapping object")

    messages: list[Message] = []
    observed_times: list[str] = []
    ordered = sorted(
        mapping.values(),
        key=lambda node: ((node.get("message") or {}).get("create_time") or 0, str(node.get("id", ""))),
    )
    for node in ordered:
        if not isinstance(node, dict):
            continue
        raw = node.get("message")
        if not isinstance(raw, dict):
            continue
        author = raw.get("author") or {}
        role = str(author.get("role") or "").strip().lower()
        if role not in {"system", "user", "assistant", "tool"}:
            continue
        content = _text_from_content(raw.get("content"))
        if not content:
            continue
        observed_at = _iso_from_epoch(raw.get("create_time"))
        if observed_at:
            observed_times.append(observed_at)
        messages.append(Message(
            role=role,
            content=content,
            sequence=len(messages) + 1,
            observed_at=observed_at,
            external_id=str(node.get("id")) if node.get("id") else None,
            metadata={
                "recipient": raw.get("recipient"),
                "parent_id": node.get("parent"),
                "raw_create_time": raw.get("create_time"),
            },
        ))

    if not messages:
        raise ValueError("ChatGPT conversation contains no supported text messages")
    return Conversation(
        source="chatgpt",
        title=str(data.get("title") or "Untitled conversation"),
        external_id=str(data.get("conversation_id") or data.get("id")) if (data.get("conversation_id") or data.get("id")) else None,
        started_at=min(observed_times) if observed_times else _iso_from_epoch(data.get("create_time")),
        ended_at=max(observed_times) if observed_times else _iso_from_epoch(data.get("update_time")),
        metadata={
            "adapter": "chatgpt",
            "default_model_slug": data.get("default_model_slug"),
            "source_create_time": data.get("create_time"),
            "source_update_time": data.get("update_time"),
        },
        messages=tuple(messages),
    )


def generic_conversation(data: dict[str, Any], *, source: str) -> Conversation:
    """Normalize the project's provider-neutral {title, messages} format."""
    from .importers import conversation_from_json
    normalized = dict(data)
    normalized["source"] = source
    return conversation_from_json(normalized)


__all__ = ["chatgpt_conversation", "generic_conversation"]
