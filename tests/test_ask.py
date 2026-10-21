import sys
from types import SimpleNamespace

from app import ask as ask_module


def test_main_keeps_chat_history_and_prints_token_counts(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(
                usage_metadata=SimpleNamespace(
                    prompt_token_count=12, candidates_token_count=34
                ),
                text=f"{question}への回答",
            )

    class FakeClient:
        def __init__(self, api_key):
            self.chats = SimpleNamespace(
                create=lambda model, config=None: created_chats.append((model, config))
                or chat
            )

    chat = FakeChat()
    created_chats = []
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module, "TEMPERATURE", 0.4)
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])
    questions = iter(["続けて質問", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    output = capsys.readouterr().out
    assert chat.questions == ["最初の質問", "続けて質問"]
    assert len(created_chats) == 1
    assert created_chats[0][1].temperature == 0.4
    assert output.count("[usage] input=12 output=34") == 2
    assert "続けて質問への回答" in output