"""HTTP routes for tool servers. Every route needs a bearer token; the role decides what is visible."""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import Role, require_role
from app.tool_servers import ToolRegistry

tool_api = APIRouter(prefix="/api/tool-servers")
RoleDep = Annotated[Role, Depends(require_role)]


class ToolServerOut(BaseModel):
    name: str
    description: str
    capabilities: list[str]


class ToolOut(BaseModel):
    name: str
    description: str


class CallIn(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class CallOut(BaseModel):
    # input_required: a required argument is missing; answer `elicitation` and call again.
    status: Literal["completed", "input_required"] = "completed"
    result: Any = None
    elicitation: dict[str, Any] | None = None


def _registry(request: Request) -> ToolRegistry:
    registry: ToolRegistry = request.app.state.tools
    return registry


@tool_api.get("", response_model=list[ToolServerOut])
def search_servers(
    request: Request, role: RoleDep, capability: str = ""
) -> list[ToolServerOut]:
    servers = _registry(request).search_servers(role, capability)
    return [
        ToolServerOut(
            name=s.name, description=s.description, capabilities=list(s.capabilities)
        )
        for s in servers
    ]


@tool_api.get("/{server}/tools", response_model=list[ToolOut])
def search_tools(
    server: str, request: Request, role: RoleDep, q: str = ""
) -> list[ToolOut]:
    tools = _registry(request).search_tools(role, server, q)
    if tools is None:
        raise HTTPException(status_code=404, detail=f"server {server!r} not found")
    return [ToolOut(name=t.name, description=t.description) for t in tools]


@tool_api.post("/{server}/tools/{tool}/call", response_model=CallOut)
def call_tool(
    server: str, tool: str, body: CallIn, request: Request, role: RoleDep
) -> CallOut:
    found = _registry(request).find_tool(role, server, tool)
    if found is None:
        raise HTTPException(status_code=404, detail=f"tool {server}/{tool} not found")
    missing = found.missing(body.arguments)
    if missing:
        return CallOut(status="input_required", elicitation=found.elicitation(missing))
    try:
        result = found.handler(body.arguments)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return CallOut(result=result)
