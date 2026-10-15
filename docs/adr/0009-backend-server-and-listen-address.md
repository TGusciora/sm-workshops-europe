# ADR-0009: Backend server and listen address

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

ADR-0002 left the address the backend listens on undecided, and required it to be decided before the backend first runs. FastAPI needs an ASGI server to run, and its test client needs `httpx`. Neither is in `pyproject.toml` yet, and `CLAUDE.md` requires a written reason for each new dependency.

## Decision

- The backend listens on `127.0.0.1` only, on port `8000` by default. It does not listen on other interfaces. The frontend dev server proxies `/api` to this address.
- The ASGI server is `uvicorn`. It runs the FastAPI app and nothing else. It is a runtime dependency.
- `httpx` is a development dependency. FastAPI's `TestClient` uses it in the backend tests.

## Consequences

- Candidate data is reachable only from the interviewer's machine, as ADR-0002 intends.
- Running on another machine or interface needs a new ADR and a change to the run command.
- `uvicorn` and `httpx` are pinned through `uv.lock`.

## Alternatives considered

- Listen on `0.0.0.0`: rejected, because it exposes candidate data to the local network.
- Hypercorn or Gunicorn: not chosen, because `uvicorn` is the server the FastAPI documentation uses and it needs no extra configuration.
