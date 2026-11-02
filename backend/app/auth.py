"""Bearer-token authentication. Each token belongs to one role."""

import hmac
from collections.abc import Mapping
from typing import Annotated, Literal

from fastapi import Header, HTTPException, Request

Role = Literal["interviewer", "manager"]


def role_for_token(
    tokens: Mapping[str, Role], authorization: str | None
) -> Role | None:
    scheme, _, token = (authorization or "").partition(" ")
    if scheme != "Bearer" or not token:
        return None
    found: Role | None = None
    for known, role in tokens.items():
        # Compare every known token so the time taken does not reveal which one matched.
        if hmac.compare_digest(known.encode(), token.encode()):
            found = role
    return found


def require_role(
    request: Request, authorization: Annotated[str | None, Header()] = None
) -> Role:
    role = role_for_token(request.app.state.settings.api_tokens, authorization)
    if role is None:
        raise HTTPException(
            status_code=401,
            detail="missing or unknown bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return role
