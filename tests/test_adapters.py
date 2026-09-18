import unittest

from memory_os.adapters import chatgpt_conversation


class AdapterTests(unittest.TestCase):
    def test_chatgpt_adapter_normalizes_mapping(self):
        data = {
            "title": "Test conversation",
            "conversation_id": "conv-1",
            "default_model_slug": "test-model",
            "mapping": {
                "node-2": {
                    "id": "node-2",
                    "message": {
                        "author": {"role": "assistant"},
                        "create_time": 2,
                        "content": {"parts": ["Hello back"]},
                    },
                },
                "node-1": {
                    "id": "node-1",
                    "message": {
                        "author": {"role": "user"},
                        "create_time": 1,
                        "content": {"parts": ["Hello"]},
                    },
                },
            },
        }

        conversation = chatgpt_conversation(data)

        self.assertEqual(conversation.source, "chatgpt")
        self.assertEqual(conversation.external_id, "conv-1")
        self.assertEqual(conversation.title, "Test conversation")
        self.assertEqual([m.role for m in conversation.messages], ["user", "assistant"])
        self.assertEqual([m.content for m in conversation.messages], ["Hello", "Hello back"])

    def test_chatgpt_adapter_rejects_empty_conversation(self):
        with self.assertRaises(ValueError) as ctx:
            chatgpt_conversation({"mapping": {}})
        self.assertIn("no supported text messages", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
