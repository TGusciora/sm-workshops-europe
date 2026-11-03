"""Backend for the Playwright end-to-end tests (ADR-0013).

Started by frontend/playwright.config.ts with:
    uv run uvicorn --app-dir . tests.e2e_app:create_app --factory --host 127.0.0.1 --port 8001

It uses a fresh data directory under E2E_ROOT on every start, and a scripted LLM client
in place of the Claude Agent SDK, so the e2e run is deterministic and needs no subscription.
The real application code is used unchanged; only the settings and the LLM client differ.
"""

import itertools
import json
import os
import shutil
from pathlib import Path

from fastapi import FastAPI

from app.config import Settings
from app.main import create_app as build_app
from app.prompts import PINEAPPLE_REQUIREMENT

JOB_TALK_SYSTEM_START = "You help a hiring manager"
QUESTIONS_SYSTEM_START = "You propose interview questions"
MESSAGE_MARKER = "New message from the hiring manager:\n"
STAGE_MARKER = "Interview stage: "


class ScriptedClient:
    """Answers the two AI features with predictable output. Prompts are not stored."""

    model_id = "scripted-e2e"

    def __init__(self) -> None:
        self._numbers = itertools.count(1)

    async def complete(self, system: str, prompt: str) -> str:
        if system.startswith(JOB_TALK_SYSTEM_START):
            return self._job_talk(prompt)
        if system.startswith(QUESTIONS_SYSTEM_START):
            return self._questions(prompt)
        raise AssertionError(f"unexpected system prompt: {system[:40]!r}")

    def _job_talk(self, prompt: str) -> str:
        request = prompt.split(MESSAGE_MARKER, 1)[1].strip()
        draft = (
            "# Job description\n\n"
            "## Summary\n"
            f"{request}\n\n"
            "## Must-have requirements\n"
            f"{PINEAPPLE_REQUIREMENT}\n"
        )
        return json.dumps({"reply": f"Here is a draft for: {request}", "draft": draft})

    def _questions(self, prompt: str) -> str:
        stage = prompt.split(STAGE_MARKER, 1)[1].splitlines()[0].strip()
        items = []
        for _ in range(5):
            number = next(self._numbers)
            items.append(
                {
                    "question": f"Question {number} for the {stage} stage?",
                    "purpose": f"Purpose {number}",
                    "good_answer": f"A good answer {number} covers the role.",
                }
            )
        return json.dumps(items)


def create_app(client: ScriptedClient | None = None) -> FastAPI:
    root = Path(os.environ.get("E2E_ROOT", "")).expanduser()
    if not str(root):
        raise RuntimeError("E2E_ROOT must be set for the e2e backend")
    if root.exists():
        shutil.rmtree(root)
    data_dir = root / "data"
    hiring_dir = root / "hiring"
    data_dir.mkdir(parents=True)
    hiring_dir.mkdir(parents=True)
    settings = Settings(data_dir=data_dir, hiring_dir=hiring_dir)
    return build_app(settings=settings, client=client or ScriptedClient())
