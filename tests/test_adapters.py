from memory_os.adapters import chatgpt_conversation


def test_chatgpt_adapter_normalizes_mapping():
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

    assert conversation.source == "chatgpt"
    assert conversation.external_id == "conv-1"
    assert conversation.title == "Test conversation"
    assert [m.role for m in conversation.messages] == ["user", "assistant"]
    assert [m.content for m in conversation.messages] == ["Hello", "Hello back"]


def test_chatgpt_adapter_rejects_empty_conversation():
    try:
        chatgpt_conversation({"mapping": {}})
    except ValueError as exc:
        assert "no supported text messages" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
