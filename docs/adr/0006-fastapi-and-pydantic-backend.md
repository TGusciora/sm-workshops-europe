# ADR-0006: FastAPI and Pydantic for the backend

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The backend is a Python 3.12 server that exposes the HTTP API to the frontend (ADR-0002). It validates request and response data and calls the Claude API through the Agent SDK (ADR-0008). `pyproject.toml` already declares `fastapi` and `pydantic>=2`, and `CLAUDE.md` requires a written reason for each dependency.

**Note:** this record was written after the dependencies were added. The rationale below is inferred from the stack, and the author should confirm it before relying on it.

## Decision

The backend uses FastAPI for the HTTP layer and Pydantic v2 for data models and validation.

## Consequences

- Request and response shapes are defined once, as Pydantic models, and checked at the HTTP boundary.
- The API schema is generated from the same models, which the frontend can use as its reference.
- FastAPI and Pydantic are pinned through `uv.lock`. Upgrading either is a change that needs a check of the models.

## Alternatives considered

- Flask with manual validation: not chosen, because validation would be written by hand for every endpoint.
- Django: not chosen, because the application does not need its admin, ORM or templating.
