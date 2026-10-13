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
- **LLM**: Anthropic Claude API, through the `anthropic` SDK.

Notes:

- Use the Python 3.12 language level. Do not use features from later versions.
- Keep the backend and frontend in one repository. The frontend talks to the backend only over HTTP.
- Do not add a new dependency without a reason written in `docs/decisions/`.

## Directory Structure

Folder names are nouns. Each noun names what lives in that folder. When you add a folder, give it a noun name and add a line for it here.

```
.
├── backend/    Python server application
├── frontend/   React and TypeScript single-page application
├── data/       Local runtime data: SQLite database, uploads (not committed)
└── docs/       Documentation and architecture decision records
```

## Commands

Run Python tools through `uv` so they use the project environment.

```
uv sync                  # create or update the environment from pyproject.toml
uv run ruff check        # lint
uv run ruff format       # format
uv run ty check          # type check
uv run pytest            # tests
```

Frontend commands will be added here once the frontend is set up.

## Open Questions

- Product name.
- Exact candidate data fields and retention rules.
- Whether candidate CVs are stored as files in `data/` or only as extracted text.
