from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .core import MemoryStore


def conversation_id(source: str, external_id: str | None, title: str) -> str:
    return hashlib.sha256("\x1f".join((source, external_id or title)).encode()).hexdigest()[:24]


def message_id(conversation: str, sequence: int, role: str, content: str, external_id: str | None = None) -> str:
    return hashlib.sha256("\x1f".join((conversation, external_id or str(sequence), role, content)).encode()).hexdigest()[:24]


@dataclass(frozen=True)
class Message:
    role: str
    content: str
    sequence: int
    observed_at: str | None = None
    external_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    message_id: str | None = None


@dataclass(frozen=True)
class Conversation:
    source: str
    title: str
    messages: tuple[Message, ...]
    external_id: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    source_location: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def conversation_id(self) -> str:
        return conversation_id(self.source, self.external_id, self.title)


def ensure_schema(store: MemoryStore) -> None:
    store.conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY, source TEXT NOT NULL, external_id TEXT,
            title TEXT NOT NULL, started_at TEXT, ended_at TEXT, source_location TEXT,
            metadata_json TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_conversations_source_external
            ON conversations(source, external_id) WHERE external_id IS NOT NULL;
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL, sequence INTEGER NOT NULL,
            role TEXT NOT NULL, content TEXT NOT NULL, observed_at TEXT, external_id TEXT,
            metadata_json TEXT NOT NULL, UNIQUE(conversation_id, sequence, role, content)
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, sequence);
    """)
    store.conn.commit()


def _merge_json(existing_json: str | None, incoming: dict[str, Any]) -> str:
    return json.dumps({**json.loads(existing_json or "{}"), **incoming}, sort_keys=True)


def persist_conversation(store: MemoryStore, conversation: Conversation) -> str:
    ensure_schema(store)
    cid = conversation.conversation_id
    store.conn.execute("BEGIN")
    try:
        existing = store.conn.execute("SELECT * FROM conversations WHERE conversation_id=?", (cid,)).fetchone()
        if existing is None:
            store.conn.execute("INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cid, conversation.source, conversation.external_id, conversation.title, conversation.started_at,
                 conversation.ended_at, conversation.source_location, json.dumps(conversation.metadata, sort_keys=True)))
        else:
            store.conn.execute("UPDATE conversations SET title=?, started_at=?, ended_at=?, source_location=?, metadata_json=? WHERE conversation_id=?",
                (conversation.title, conversation.started_at or existing["started_at"], conversation.ended_at or existing["ended_at"],
                 conversation.source_location or existing["source_location"], _merge_json(existing["metadata_json"], conversation.metadata), cid))
        for msg in conversation.messages:
            if not msg.role.strip() or not msg.content.strip():
                raise ValueError("message role and content must be non-empty")
            mid = msg.message_id or message_id(cid, msg.sequence, msg.role, msg.content, msg.external_id)
            existing_msg = store.conn.execute("SELECT * FROM messages WHERE message_id=?", (mid,)).fetchone()
            if existing_msg is None:
                store.conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (mid, cid, msg.sequence, msg.role, msg.content, msg.observed_at, msg.external_id, json.dumps(msg.metadata, sort_keys=True)))
            else:
                store.conn.execute("UPDATE messages SET observed_at=?, external_id=?, metadata_json=? WHERE message_id=?",
                    (msg.observed_at or existing_msg["observed_at"], msg.external_id or existing_msg["external_id"],
                     _merge_json(existing_msg["metadata_json"], msg.metadata), mid))
        store.conn.commit()
    except Exception:
        store.conn.rollback()
        raise
    return cid


def get_conversation(store: MemoryStore, cid: str) -> dict[str, Any]:
    ensure_schema(store)
    row = store.conn.execute("SELECT * FROM conversations WHERE conversation_id=?", (cid,)).fetchone()
    if row is None:
        raise KeyError(f"conversation not found: {cid}")
    return dict(row)


def list_conversations(store: MemoryStore, limit: int = 50) -> list[dict[str, Any]]:
    ensure_schema(store)
    if limit < 1:
        return []
    return [dict(row) for row in store.conn.execute("SELECT * FROM conversations ORDER BY COALESCE(ended_at, started_at, rowid) DESC LIMIT ?", (limit,))]


def get_messages(store: MemoryStore, cid: str) -> list[dict[str, Any]]:
    ensure_schema(store)
    return [dict(row) for row in store.conn.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence", (cid,))]


__all__ = ["Conversation", "Message", "ensure_schema", "get_conversation", "get_messages", "list_conversations", "message_id", "persist_conversation"]
