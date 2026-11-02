"""Starts the real stdio MCP server the way .mcp.json does, one process per role."""

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.session import ClientRequestContext, ElicitationFnT
from mcp.client.stdio import stdio_client
from mcp.types import (
    ElicitRequestFormParams,
    ElicitRequestParams,
    ElicitResult,
    TextContent,
)

BACKEND = Path(__file__).resolve().parents[1]
TOKENS = {"interviewer": "iv-test-token", "manager": "mg-test-token"}


def server_params(role: str) -> StdioServerParameters:
    env = {
        **os.environ,
        "PYTHONPATH": str(BACKEND),
        "INTERVIEWER_TOKEN": TOKENS["interviewer"],
        "MANAGER_TOKEN": TOKENS["manager"],
    }
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server", "--role", role],
        env=env,
        cwd=BACKEND,
    )


async def _accept_candidate(
    context: ClientRequestContext, params: ElicitRequestParams
) -> ElicitResult:
    assert isinstance(params, ElicitRequestFormParams)
    assert "candidate_id" in params.requested_schema["properties"]
    return ElicitResult(action="accept", content={"candidate_id": "c-001"})


def test_each_role_lists_only_its_own_tools() -> None:
    async def tool_names(role: str) -> list[str]:
        async with (
            stdio_client(server_params(role)) as (read, write),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            return sorted(tool.name for tool in (await session.list_tools()).tools)

    interviewer = asyncio.run(tool_names("interviewer"))
    manager = asyncio.run(tool_names("manager"))

    assert "screening_get_job_criteria" in interviewer
    assert not any(name.startswith("crm_") for name in interviewer)
    assert "crm_write_interview_note" in manager


def test_missing_argument_is_asked_through_elicitation() -> None:
    async def call() -> str:
        async with (
            stdio_client(server_params("interviewer")) as (read, write),
            ClientSession(
                read, write, elicitation_callback=_accept_candidate
            ) as session,
        ):
            await session.initialize()
            result = await session.call_tool("screening_get_candidate_profile", {})
            return "".join(b.text for b in result.content if isinstance(b, TextContent))

    assert "Ada Example" in asyncio.run(call())


async def _accept_slot(
    context: ClientRequestContext, params: ElicitRequestParams
) -> ElicitResult:
    assert isinstance(params, ElicitRequestFormParams)
    assert params.requested_schema["required"] == ["candidate_id", "slot"]
    content = {"candidate_id": "c-002", "slot": "2026-11-11T09:30"}
    return ElicitResult(action="accept", content=content)


async def _decline(
    context: ClientRequestContext, params: ElicitRequestParams
) -> ElicitResult:
    return ElicitResult(action="decline")


def _call_with(
    callback: ElicitationFnT,
    tool: str,
    arguments: dict[str, str],
    role: str = "interviewer",
) -> str:
    async def run() -> str:
        async with (
            stdio_client(server_params(role)) as (read, write),
            ClientSession(read, write, elicitation_callback=callback) as session,
        ):
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            return "".join(b.text for b in result.content if isinstance(b, TextContent))

    return asyncio.run(run())


def test_two_missing_arguments_are_asked_together() -> None:
    text = _call_with(
        _accept_slot, "scheduling_propose_appointment", {}, role="interviewer"
    )

    assert "proposed" in text
    assert "c-002" in text


def test_declined_question_runs_nothing() -> None:
    text = _call_with(_decline, "screening_get_candidate_profile", {})

    assert "decline" in text
    assert "Ada Example" not in text
