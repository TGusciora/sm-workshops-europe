import asyncio

import pytest
from app.database import connect
from app.llm import LlmCallError, auth_method, call_claude
from app.repository import Repository
from conftest import FakeClient


@pytest.fixture
def repo(tmp_path) -> Repository:
    return Repository(connect(tmp_path / "app.db"))


def run(coro):
    return asyncio.run(coro)


def test_auth_method_is_subscription_without_an_api_key() -> None:
    assert auth_method({}) == "subscription"


def test_auth_method_is_api_key_when_the_variable_is_set() -> None:
    assert auth_method({"ANTHROPIC_API_KEY": "x"}) == "api_key"


def test_successful_call_is_recorded_with_inputs_model_and_auth_method(
    repo: Repository,
) -> None:
    client = FakeClient(["hello"])

    output_id, text = run(
        call_claude(
            repo,
            client,
            kind="test",
            prompt_version="v1",
            system="sys",
            prompt="p",
            inputs={"a": 1},
            environ={},
        )
    )

    record = repo.get_ai_output(output_id)
    assert text == "hello"
    assert record is not None
    assert (record.status, record.output, record.model_id) == (
        "ok",
        "hello",
        "fake-model",
    )
    assert (record.prompt_version, record.auth_method) == ("v1", "subscription")


def test_failed_call_is_recorded_and_raised(repo: Repository) -> None:
    client = FakeClient([RuntimeError("cli exited")])

    with pytest.raises(LlmCallError) as caught:
        run(
            call_claude(
                repo,
                client,
                kind="test",
                prompt_version="v1",
                system="s",
                prompt="p",
                inputs={},
                environ={},
            )
        )

    record = repo.get_ai_output(caught.value.ai_output_id)
    assert record is not None
    assert record.status == "error"
    assert "cli exited" in (record.error or "")
    assert caught.value.status_code == 502


def test_call_is_refused_and_recorded_when_an_api_key_is_set(repo: Repository) -> None:
    client = FakeClient(["never used"])
    secret = "sk-test-secret-value"

    with pytest.raises(LlmCallError) as caught:
        run(
            call_claude(
                repo,
                client,
                kind="test",
                prompt_version="v1",
                system="s",
                prompt="p",
                inputs={},
                environ={"ANTHROPIC_API_KEY": secret},
            )
        )

    assert client.calls == []
    assert caught.value.status_code == 409
    record = repo.get_ai_output(caught.value.ai_output_id)
    assert record is not None
    assert record.auth_method == "api_key"
    # The key itself is never stored in the record.
    stored = repo.conn.execute("SELECT * FROM ai_outputs").fetchall()
    assert all(secret not in str(tuple(row)) for row in stored)
