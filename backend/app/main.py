"""Application factory. Run with: uv run uvicorn app.main:create_app --factory (from backend/)."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings, default_settings
from app.database import connect
from app.llm import AgentSdkClient, LlmClient, auth_method
from app.repository import Repository
from app.routes import api

logger = logging.getLogger("app")


def create_app(
    settings: Settings | None = None, client: LlmClient | None = None
) -> FastAPI:
    settings = settings or default_settings()
    conn = connect(settings.db_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        logger.info("Claude auth method in effect: %s", auth_method())
        yield

    app = FastAPI(title="Onboarding interview backend", lifespan=lifespan)
    app.state.settings = settings
    app.state.repo = Repository(conn)
    app.state.client = client or AgentSdkClient(settings.model_id)
    app.include_router(api)
    return app
