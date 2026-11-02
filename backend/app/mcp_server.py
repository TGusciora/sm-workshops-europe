"""Stdio MCP server for one role (ADR-0012). .mcp.json starts one process per role:
    python -m app.mcp_server --role interviewer
The role's token comes from its environment variable. The server exposes only the tools
that role may use. A missing required argument is asked for with MCP elicitation."""

import argparse
import inspect
import os
import sys
from collections.abc import Awaitable, Callable
from typing import Any

from mcp.server.mcpserver import Context, MCPServer
from pydantic import BaseModel, Field, create_model

from app.auth import Role, role_for_token
from app.config import TOKEN_VARIABLES, default_settings
from app.mock_servers import build_registry
from app.tool_servers import Tool, ToolRegistry


def _answer_model(tool: Tool, missing: list[str]) -> type[BaseModel]:
    fields: dict[str, Any] = {
        name: (str, Field(description=tool.schema["properties"][name]["description"]))
        for name in missing
    }
    return create_model(f"{tool.name}_answer", **fields)


def _tool_function(tool: Tool) -> Callable[..., Awaitable[Any]]:
    """A callable whose signature lists the tool's arguments, so MCP derives the input schema."""

    async def run(**kwargs: Any) -> Any:
        ctx: Context = kwargs.pop("ctx")
        arguments = dict(kwargs)
        missing = tool.missing(arguments)
        if missing:
            answer = await ctx.elicit(
                message=tool.elicitation(missing)["message"],
                schema=_answer_model(tool, missing),
            )
            if answer.action != "accept":
                return {"status": answer.action, "missing": missing}
            arguments.update(answer.data.model_dump())
        return tool.handler(arguments)

    properties = list(tool.schema["properties"])
    parameters = [
        inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context),
        *(
            inspect.Parameter(
                name, inspect.Parameter.KEYWORD_ONLY, default="", annotation=str
            )
            for name in properties
        ),
    ]
    setattr(run, "__signature__", inspect.Signature(parameters))  # noqa: B010
    run.__annotations__ = {
        "ctx": Context,
        **dict.fromkeys(properties, str),
        "return": Any,
    }
    return run


def build_server(role: Role, registry: ToolRegistry) -> MCPServer:
    server = MCPServer(f"onboarding-{role}")
    for server_name, tool in registry.visible_tools(role):
        server.add_tool(
            _tool_function(tool),
            name=f"{server_name}_{tool.name}",
            description=tool.description,
        )
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Onboarding tools as an MCP server")
    parser.add_argument(
        "--role", choices=sorted(set(TOKEN_VARIABLES.values())), required=True
    )
    role: Role = parser.parse_args().role

    variable = next(name for name, r in TOKEN_VARIABLES.items() if r == role)
    token = os.environ.get(variable, "")
    settings = default_settings()
    # The token must belong to this role, using the same check as the HTTP routes.
    if not token or role_for_token(settings.api_tokens, f"Bearer {token}") != role:
        sys.exit(f"{variable} is not set or does not belong to role {role!r}")

    build_server(role, build_registry(settings)).run()


if __name__ == "__main__":
    main()
