"""Tool servers and the role rules for them. Two search layers: servers by capability,
then tools inside one server. A role only ever sees what its tools allow."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from app.auth import Role

Handler = Callable[[dict[str, Any]], Any]


def fields_schema(**properties: str) -> dict[str, Any]:
    """The arguments a tool needs, as JSON Schema. Every field listed is required."""
    return {
        "type": "object",
        "properties": {
            name: {"type": "string", "description": text}
            for name, text in properties.items()
        },
        "required": list(properties),
    }


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    roles: frozenset[Role]
    handler: Handler
    schema: dict[str, Any] = field(default_factory=fields_schema)

    def missing(self, arguments: dict[str, Any]) -> list[str]:
        return [n for n in self.schema["required"] if arguments.get(n) in (None, "")]

    def elicitation(self, missing: list[str]) -> dict[str, Any]:
        """The question asked of the user, in MCP elicitation's message and requestedSchema shape."""
        properties = {n: self.schema["properties"][n] for n in missing}
        return {
            "message": f"{self.name} needs: {', '.join(missing)}",
            "requestedSchema": {
                "type": "object",
                "properties": properties,
                "required": missing,
            },
        }


@dataclass(frozen=True)
class ToolServer:
    name: str
    description: str
    capabilities: tuple[str, ...]
    tools: tuple[Tool, ...]

    def tools_for(self, role: Role) -> list[Tool]:
        return [tool for tool in self.tools if role in tool.roles]


def matches(query: str, *fields: str) -> bool:
    """Every word of the query must appear in the fields. An empty query matches all."""
    haystack = " ".join(fields).lower()
    return all(word in haystack for word in query.lower().split())


class ToolRegistry:
    def __init__(self, servers: Iterable[ToolServer]) -> None:
        self._servers = {server.name: server for server in servers}

    def search_servers(self, role: Role, capability: str = "") -> list[ToolServer]:
        """Layer 1: servers this role can use whose capabilities match the query."""
        return [
            server
            for server in self._servers.values()
            if server.tools_for(role)
            and matches(
                capability, *server.capabilities, server.name, server.description
            )
        ]

    def search_tools(
        self, role: Role, server_name: str, query: str = ""
    ) -> list[Tool] | None:
        """Layer 2: tools inside one server. None when the server is not visible to the role."""
        server = self._visible(role, server_name)
        if server is None:
            return None
        return [
            tool
            for tool in server.tools_for(role)
            if matches(query, tool.name, tool.description)
        ]

    def visible_tools(self, role: Role) -> list[tuple[str, Tool]]:
        """Every tool this role may use, paired with the name of its server."""
        return [
            (server.name, tool)
            for server in self._servers.values()
            for tool in server.tools_for(role)
        ]

    def find_tool(self, role: Role, server_name: str, tool_name: str) -> Tool | None:
        server = self._visible(role, server_name)
        if server is None:
            return None
        return next((t for t in server.tools_for(role) if t.name == tool_name), None)

    def _visible(self, role: Role, server_name: str) -> ToolServer | None:
        server = self._servers.get(server_name)
        if server is None or not server.tools_for(role):
            return None
        return server
