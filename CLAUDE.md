# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

A locally run application for the hiring manager that helps onboard new hires through the interview process. It is a working name; rename it when a product name is chosen.

## Goal

The application is for the hiring manager. Its goal is to give the hiring manager all the tools needed to run the hiring process as effectively as possible and onboard the best people available.

Basic functionalities to achieve in a semi-autonomous way:

1. Login to the internal system.
2. Talk with the user about jobs.
3. Talk with the user about interview questions.
4. Do candidate screening.

The application runs on the interviewer's own machine. Candidate data never leaves it except for the calls to the LLM provider that the features need.

## Vision

A **semi-autonomous** interview process. The system does the repetitive preparation work on its own, and humans make every decision that affects a candidate.

- The system proposes: questions, screening summaries, scores with reasons, follow-up suggestions.
- Humans approve, edit, or reject every proposal before it is used or stored as final.
- Nothing is sent to a candidate automatically.
- Every AI-produced output records the inputs and the model used, so a recommendation can be traced and reviewed.

Design for this boundary first. A feature that removes the human from a decision about a candidate is out of scope.

## Tech Stack

- **Backend**: Python dependencies, tool versions, and the Python version are defined in @pyproject.toml. Environment and dependency management is done with `uv`.
- **Linting**: `ruff`. **Type checking**: `ty`. **Tests**: `pytest`.
- **Frontend**: TypeScript with React, built with Vite. Tests with Vitest and React Testing Library.
- **Persistence**: SQLite, as a local file under `data/`.
- **LLM**: Claude, through the Claude Agent SDK, which runs the Claude Code CLI signed in with the hiring manager's subscription. Local, single-user use only (ADR-0008).

Notes:

- Use the Python 3.12 language level. Do not use features from later versions.
- Keep the backend and frontend in one repository. The frontend talks to the backend only over HTTP.
- Do not add a new dependency without a reason written in an ADR in `docs/adr/`.

## Architecture

The component diagram for the chosen stack is in `docs/architecture/system-overview.md`. Each main functionality has a sequence diagram in `docs/architecture/`, starting from `docs/architecture/README.md`.

Update the matching diagram in the same change when a flow or a component changes.

## Directory Structure

Folder names are nouns. Each noun names what lives in that folder. When you add a folder, give it a noun name and add a line for it here.

```
.
├── .claude/    Claude Code settings; agents/ holds project subagents (e.g. executor, which builds features); rules/ holds path-scoped rules (e.g. for hiring/); skills/ holds project skills (e.g. /spec)
├── backend/    Python server application (FastAPI, SQLite access, Claude wrapper)
├── frontend/   React and TypeScript single-page application
├── data/       Local runtime data: SQLite database, uploads (not committed; created on first run)
├── docs/       Documentation, architecture diagrams (docs/architecture/) and architecture decision records (docs/adr/, history in docs/adr/archive/)
├── spec/       Specifications: business specs with Mermaid diagrams (spec/business/), and feature tickets, one file per ticket, grouped by status folder (spec/features/)
└── hiring/     Job descriptions, one folder per position (e.g. hiring/ceo/ceo.md)
```

## Current State

As of 2026-10-15.

- Done: project guidance (this file), the CEO job description in `hiring/ceo/`, the ticket structure in `spec/features/`, and the architecture documents in `docs/architecture/`.
- Backend: built under `backend/` (F0001 to F0003). Dependencies are declared in `pyproject.toml` (`claude-agent-sdk`, `fastapi`, `pydantic`, `uvicorn`; dev: `httpx`, `pytest`, `ruff`, `ty`). The `anthropic` dependency was replaced by the Claude Agent SDK (ADR-0008). All Claude calls go through `backend/app/llm.py`.
- Frontend: built under `frontend/` (F0001 to F0003). React, TypeScript and Vite, with Vitest tests. Dependencies are listed in ADR-0011.
- Tickets: Phase 1 tickets F0001 (foundation), F0002 (talk about jobs) and F0003 (talk about interview questions) are in `spec/features/done/`. Start with `spec/features/README.md`.
- Decisions: ADRs are in `docs/adr/`. ADR-0006 and ADR-0007 record the current dependencies, and their rationale still needs confirming. ADR-0009 (server and listen address), ADR-0010 (SQLite migrations) and ADR-0011 (frontend dependencies) were added with Phase 1. Add an ADR before adding any new dependency.

## Commands

Run Python tools through `uv` so they use the project environment.

```
uv sync                  # create or update the environment from pyproject.toml
uv run ruff check        # lint
uv run ruff format       # format
uv run ty check          # type check
uv run pytest            # tests
```

Run the backend and the frontend locally (two terminals):

```
cd backend && uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
cd frontend && npm install && npm run dev       # http://127.0.0.1:5173, proxies /api to the backend
```

The LLM features need the Claude Code CLI installed and signed in, and `ANTHROPIC_API_KEY` unset (ADR-0008).

Frontend commands (run in `frontend/`):

```
npm install             # install dependencies from package-lock.json
npm test                # Vitest (vitest run)
npm run typecheck      # tsc --noEmit
npm run build           # typecheck and production build
```

## Open Questions

- Product name.
- Exact candidate data fields and retention rules.
- Whether candidate CVs are stored as files in `data/` or only as extracted text.
