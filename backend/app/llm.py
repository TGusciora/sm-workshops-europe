"""The only module that calls Claude (ADR-0008).

Every call writes an AI output record, including failed calls and refused calls.
The module never reads, stores or logs OAuth tokens or session data. Sign-in is
handled by the Claude Code CLI. It records only which auth method is in effect.
"""

import logging
import os
from collections.abc import Mapping
from typing import Any, Literal, Protocol

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from app.repository import Repository

logger = logging.getLogger(__name__)

SUBSCRIPTION = "subscription"
API_KEY = "api_key"
API_KEY_VARIABLE = "ANTHROPIC_API_KEY"


class LlmCallError(Exception):
    """A Claude call failed or was refused. The failure is already recorded."""

    def __init__(self, message: str, ai_output_id: int, status_code: int) -> None:
        super().__init__(message)
        self.ai_output_id = ai_output_id
        self.status_code = status_code


class LlmClient(Protocol):
    model_id: str

    async def complete(self, system: str, prompt: str) -> str: ...


def agent_options(model_id: str, system: str) -> ClaudeAgentOptions:
    """One isolated turn: no tools, and no settings, CLAUDE.md files, hooks or MCP
    servers from the machine. The output then depends only on what is recorded."""
    return ClaudeAgentOptions(
        system_prompt=system,
        model=model_id,
        tools=[],
        max_turns=1,
        setting_sources=[],
        strict_mcp_config=True,
    )


class AgentSdkClient:
    """Runs one turn through the Claude Agent SDK, with no tools enabled."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    async def complete(self, system: str, prompt: str) -> str:
        options = agent_options(self.model_id, system)
        result: str | None = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                if message.is_error:
                    raise RuntimeError(message.result or "Claude returned an error")
                result = message.result
        if result is None:
            raise RuntimeError("Claude returned no result")
        return result


def auth_method(
    environ: Mapping[str, str] | None = None,
) -> Literal["subscription", "api_key"]:
    """The auth method the CLI will use: an API key if one is set, else the subscription."""
    env = os.environ if environ is None else environ
    return API_KEY if env.get(API_KEY_VARIABLE) else SUBSCRIPTION


async def call_claude(
    repo: Repository,
    client: LlmClient,
    *,
    kind: str,
    prompt_version: str,
    system: str,
    prompt: str,
    inputs: dict[str, Any],
    environ: Mapping[str, str] | None = None,
) -> tuple[int, str]:
    """Run one Claude call and record it. Returns (ai_output_id, output text)."""
    method = auth_method(environ)
    common: dict[str, Any] = {
        "kind": kind,
        "inputs": inputs,
        "model_id": client.model_id,
        "prompt_version": prompt_version,
        "auth_method": method,
    }
    logger.info("Claude call %s with auth method %s", kind, method)

    if method == API_KEY:
        message = (
            f"{API_KEY_VARIABLE} is set, so Claude would bill the API key instead of the "
            "subscription. Unset it before using this feature (ADR-0008, condition 5)."
        )
        output_id = repo.record_ai_output(
            status="error", output=None, error=message, **common
        )
        raise LlmCallError(message, output_id, status_code=409)

    try:
        text = await client.complete(system, prompt)
    except Exception as exc:
        message = f"Claude call failed: {exc}"
        output_id = repo.record_ai_output(
            status="error", output=None, error=message, **common
        )
        raise LlmCallError(message, output_id, status_code=502) from exc

    output_id = repo.record_ai_output(status="ok", output=text, error=None, **common)
    return output_id, text
