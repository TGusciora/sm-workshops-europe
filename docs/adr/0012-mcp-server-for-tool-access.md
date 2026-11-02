# ADR-0012: MCP server for tool access

Status: Accepted
Date: 2026-11-02
Supersedes: none
Superseded by: none

## Context

The tool servers (screening, scheduling, crm) are in-process mocks behind our own HTTP routes (`backend/app/tool_routes.py`). The hiring manager wants to test them as MCP capabilities, connected through `.mcp.json`, so that Claude Code can use them. A tool that asks for a missing argument must ask the user through MCP elicitation.

CLAUDE.md requires an ADR before any new dependency is added.

## Decision

Add the official `mcp` Python SDK (`mcp` on PyPI, `mcp.server.mcpserver.MCPServer`) and run a stdio MCP server, `backend/app/mcp_server.py`, one process per role. Each process gets only its own role token from the environment (`INTERVIEWER_TOKEN` or `MANAGER_TOKEN`), checks it with the same `role_for_token` used by the HTTP routes, and registers only the tools that role may use. Missing required arguments are asked through `ctx.elicit`, using a flat schema built from the tool's argument schema.

The LLM calls in `backend/app/llm.py` stay as they are (ADR-0008). This ADR does not connect the LLM to these servers.

## Consequences

- One new dependency, `mcp`, pinned in `pyproject.toml` and `uv.lock`.
- `.mcp.json` gets one entry per role. Tokens are expanded from the shell with `${VAR}`, so no secret is written into the file.
- Stdio runs locally and needs no network port, which fits ADR-0002 and ADR-0009.
- Elicitation is limited to flat primitive fields, so all tool arguments stay strings.
- Each role process holds only its own token and sees only its own tools.

## Alternatives considered

- Keep only the HTTP routes and write a custom MCP wire protocol: more code and no MCP client compatibility.
- Streamable HTTP on localhost: works, but needs a port and a second process to start, and the token would still need to reach `.mcp.json`.
- One MCP process with both tokens: a manager token would sit in the interviewer's process, which defeats the role split.
