# ADR-0007: Python and frontend tooling

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The project needs one set of tools for environments, linting, type checking and tests, on both the backend and the frontend. `CLAUDE.md` names the tools, and `pyproject.toml` already declares the Python dev tools.

**Note:** this record was written after the Python dev tools were added. The rationale below is inferred from the stack, and the author should confirm it before relying on it.

## Decision

- Python: `uv` manages the environment and dependencies, `ruff` lints and formats, `ty` type checks, and `pytest` runs tests. All Python commands run through `uv run`.
- Frontend: TypeScript with React, built with Vite. Tests use Vitest and React Testing Library.

## Consequences

- One command per check, documented in `CLAUDE.md` under Commands.
- `ty` is newer than the other tools. If it blocks work, a new ADR can replace it with a different type checker.
- The frontend tooling is not yet installed. Its dependencies need an ADR-backed reason when they are added.

## Alternatives considered

- `pip` with `venv`, `black`, `mypy`: not chosen, because `uv` and `ruff` cover these in one tool each and keep the environment in `uv.lock`.
- Jest for frontend tests: not chosen, because Vitest works with Vite without extra configuration.
