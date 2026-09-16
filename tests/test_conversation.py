import json
import tempfile
import unittest
from pathlib import Path

from memory_os.conversation import get_messages
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


if __name__ == "__main__":
    unittest.main()
