import json
from pathlib import Path

import pytest
from app.config import Settings
from app.main import create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeClient:
    """Stands in for the Agent SDK. Replies are scripted; prompts are recorded."""

    model_id = "fake-model"

    def __init__(self, replies: list[str | Exception] | None = None) -> None:
        self.replies: list[str | Exception] = list(replies or [])
        self.calls: list[tuple[str, str]] = []

    async def complete(self, system: str, prompt: str) -> str:
        self.calls.append((system, prompt))
        if not self.replies:
            raise AssertionError("FakeClient has no scripted reply left")
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def job_talk_reply(draft: str, reply: str = "Here is a draft.") -> str:
    return json.dumps({"reply": reply, "draft": draft})


def questions_reply(count: int = 2) -> str:
    items = [
        {
            "question": f"Question {n}?",
            "purpose": f"Purpose {n}",
            "good_answer": f"Good answer {n}",
        }
        for n in range(1, count + 1)
    ]
    return json.dumps(items)


@pytest.fixture(autouse=True)
def no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data", hiring_dir=tmp_path / "hiring")


@pytest.fixture
def fake_client() -> FakeClient:
    return FakeClient()


@pytest.fixture
def app(settings: Settings, fake_client: FakeClient) -> FastAPI:
    return create_app(settings, client=fake_client)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
