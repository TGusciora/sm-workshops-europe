# F0001: Foundation

## Goal

The backend and frontend run locally, talk over HTTP, and have the shared pieces every feature needs: persistence, the AI output record, and a single wrapper for Claude calls.

## Context

Phase 1 foundation. Everything else in Phase 1 depends on this ticket.

- Architecture: `../../../docs/architecture/system-overview.md`
- Decisions: ADR-0002 (local web app), ADR-0003 (SQLite), ADR-0005 (human approval), ADR-0006 (FastAPI and Pydantic), ADR-0007 (tooling)
- LLM calls: ADR-0008 (accepted). Calls go through the Claude Agent SDK. The wrapper still hides the SDK from the features, so the auth method can change if ADR-0008 is superseded.

## Acceptance criteria

- [x] `backend/` has a FastAPI app with a health endpoint, and `uv run pytest` covers it.
- [x] `frontend/` has a Vite, React and TypeScript app that calls the health endpoint through the backend, with a Vitest test.
- [x] The backend listens on the address decided in ADR-0002's open question. It does not listen on other addresses by default.
- [x] SQLite is created under `data/` on first run, with a migration mechanism. The migration tool is chosen and recorded in an ADR.
- [x] An AI output record table stores: inputs, model ID, prompt version, timestamp, the auth method used (subscription login or API key, never a token), and a link to a later human decision.
- [x] Every Claude call goes through one backend module. That module writes an AI output record for every call, including failed calls.
- [x] At startup and before each call, the wrapper checks whether `ANTHROPIC_API_KEY` is set. It records the auth method in effect (ADR-0008, condition 5).
- [x] The application never reads, stores or logs OAuth tokens or session data (ADR-0008, condition 2).
- [x] Add the Claude Agent SDK dependency and remove the unused `anthropic` dependency from `pyproject.toml`. Both changes are covered by ADR-0008.
- [x] Tests for the Claude wrapper use a fake client. No test calls the real Claude service.
- [x] `uv run ruff check`, `uv run ruff format --check`, `uv run ty check` and `uv run pytest` pass.

## Human decisions

- None in this ticket directly. The hiring manager decides the listen address and the migration tool, both recorded as ADRs.

## AI outputs

- None produced to a user yet. The AI output record and the wrapper are built here, and the features in F0002 and F0003 use them.

## Out of scope

- Any feature screen or prompt. Those are F0002 and F0003.
- Login to the Internal system.
- CV upload and candidate data.

## Open questions

- Listen address (ADR-0002). Decided: `127.0.0.1` only, port 8000, in ADR-0009.
- SQLite migration tool. Decided: forward-only SQL migrations tracked with `PRAGMA user_version`, no library, in ADR-0010.
- Claude Agent SDK version and auth detection. Decided: `claude-agent-sdk` 0.2.167, pinned in `uv.lock`. The wrapper checks whether `ANTHROPIC_API_KEY` is set before each call. If it is set, the call is refused with a 409 and recorded as `api_key`. It never falls back silently.
- Auth method is recorded in every AI output record. The startup log also shows it.

## Notes

Split this ticket if the frontend and backend skeletons become large. Keep the AI output record and the wrapper together.
