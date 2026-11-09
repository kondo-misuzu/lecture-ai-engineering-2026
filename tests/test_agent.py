"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent

BASE_TOOLS = {"search_glossary", "get_lecture_summary", "make_quiz", "save_learning_log"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    # 承認が必要なツール（requires_approval=True）は、実行されずに承認待ちになるので戻り値が無い
    assert isinstance(result.output, DeferredToolRequests)
    waiting = len(result.output.approvals)
    assert {call.tool_name for call in result.output.approvals} == {"save_learning_log"}
    assert len(_parts(result, ToolReturnPart)) + waiting == len(_parts(result, ToolCallPart))
    assert result.output


def test_learning_log_is_written_only_after_approval(tmp_path, monkeypatch):
    log_dir = tmp_path / "learning_log"
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", log_dir)
    model = TestModel(call_tools=["save_learning_log"])

    pending = agent.run_sync("学んだことを記録して", model=model)

    assert isinstance(pending.output, DeferredToolRequests)
    assert len(pending.output.approvals) == 1
    assert pending.output.approvals[0].tool_name == "save_learning_log"
    assert not log_dir.exists()

    deferred_results = pending.output.build_results(
        approvals={pending.output.approvals[0].tool_call_id: True}
    )
    result = agent.run_sync(
        message_history=pending.all_messages(),
        deferred_tool_results=deferred_results,
        model=model,
    )

    assert isinstance(result.output, str)
    assert len(list(log_dir.glob("*.md"))) == 1


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"
