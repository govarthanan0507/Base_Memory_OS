import json
import tempfile
import unittest
from pathlib import Path

from memory_os.conversation import get_conversation, get_messages
from memory_os.core import MemoryStore
from memory_os.importers import import_json, import_markdown


class ConversationTests(unittest.TestCase):
    def test_json_import_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chat.json"
            source.write_text(json.dumps({
                "id": "chat-1",
                "source": "chatgpt",
                "title": "Test chat",
                "messages": [
                    {"id": "m1", "role": "user", "content": "Where did I leave this?"},
                    {"id": "m2", "role": "assistant", "content": "In the memory project."},
                ],
            }), encoding="utf-8")
            store = MemoryStore(root / "db" / "memory.db")
            try:
                cid1 = import_json(store, source)
                cid2 = import_json(store, source)
                self.assertEqual(cid1, cid2)
                self.assertEqual(len(get_messages(store, cid1)), 2)
            finally:
                store.close()

    def test_reimport_merges_richer_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chat.json"
            base = {
                "id": "chat-1", "source": "chatgpt", "title": "Test chat",
                "messages": [{"id": "m1", "role": "user", "content": "Hello"}],
            }
            source.write_text(json.dumps(base), encoding="utf-8")
            store = MemoryStore(root / "db.sqlite")
            try:
                cid = import_json(store, source)
                richer = {
                    **base,
                    "started_at": "2026-09-10T10:00:00+00:00",
                    "ended_at": "2026-09-10T10:30:00+00:00",
                    "source_location": "/exports/chat-1.json",
                    "metadata": {"workspace": "memory-os"},
                    "messages": [{
                        "id": "m1", "role": "user", "content": "Hello",
                        "observed_at": "2026-09-10T10:01:00+00:00",
                        "metadata": {"node_id": "node-1"},
                    }],
                }
                source.write_text(json.dumps(richer), encoding="utf-8")
                self.assertEqual(import_json(store, source), cid)
                conversation = get_conversation(store, cid)
                self.assertEqual(conversation["started_at"], richer["started_at"])
                self.assertEqual(conversation["source_location"], richer["source_location"])
                self.assertIn("workspace", json.loads(conversation["metadata_json"]))
                message = get_messages(store, cid)[0]
                self.assertEqual(message["observed_at"], richer["messages"][0]["observed_at"])
                self.assertIn("node_id", json.loads(message["metadata_json"]))
            finally:
                store.close()

    def test_chatgpt_epoch_timestamps_are_normalized(self):
        from memory_os.adapters import chatgpt_conversation

        conversation = chatgpt_conversation({
            "id": "chat-time",
            "title": "Timestamped chat",
            "create_time": 1000,
            "update_time": 2000,
            "mapping": {
                "a": {"id": "a", "message": {"author": {"role": "user"}, "content": {"parts": ["first"]}, "create_time": 1000}},
                "b": {"id": "b", "message": {"author": {"role": "assistant"}, "content": {"parts": ["second"]}, "create_time": 2000}},
            },
        })
        self.assertEqual(conversation.started_at, "1970-01-01T00:16:40+00:00")
        self.assertEqual(conversation.ended_at, "1970-01-01T00:33:20+00:00")
        self.assertEqual(conversation.messages[0].observed_at, conversation.started_at)
        self.assertEqual(conversation.messages[1].observed_at, conversation.ended_at)
        self.assertEqual(conversation.messages[0].metadata["raw_create_time"], 1000)

    def test_generic_import_metadata_can_survive_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp) / "db.sqlite")
            try:
                source = Path(tmp) / "rich.json"
                source.write_text(json.dumps({
                    "id": "rich-1",
                    "source": "test-agent",
                    "title": "Rich conversation",
                    "started_at": "2026-01-01T10:00:00+00:00",
                    "ended_at": "2026-01-01T10:30:00+00:00",
                    "metadata": {"provider_version": "x1"},
                    "messages": [{
                        "id": "m1", "role": "user", "content": "hello",
                        "observed_at": "2026-01-01T10:00:00+00:00",
                        "metadata": {"channel": "desktop"},
                    }],
                }), encoding="utf-8")
                cid = import_json(store, source)
                conversation = get_conversation(store, cid)
                messages = get_messages(store, cid)
                self.assertEqual(json.loads(conversation["metadata_json"])["provider_version"], "x1")
                self.assertEqual(json.loads(messages[0]["metadata_json"])["channel"], "desktop")
            finally:
                store.close()

    def test_invalid_json_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = MemoryStore(root / "db.sqlite")
            try:
                from memory_os.conversation import Conversation, Message, persist_conversation
                bad = Conversation(source="test", title="bad", messages=(Message("user", "ok", 1), Message("", "broken", 2)))
                with self.assertRaises(ValueError):
                    persist_conversation(store, bad)
                tables = store.conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                self.assertEqual(tables, 0)
            finally:
                store.close()

    def test_markdown_import_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "chat.md"
            original = "user:\nHello\nassistant:\nHi there\n"
            source.write_text(original, encoding="utf-8")
            store = MemoryStore(root / "db.sqlite")
            try:
                cid = import_markdown(store, source, source="claude")
                rows = get_messages(store, cid)
                self.assertEqual([r["role"] for r in rows], ["user", "assistant"])
                self.assertEqual(source.read_text(encoding="utf-8"), original)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
