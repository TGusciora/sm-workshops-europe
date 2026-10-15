# Architecture Decision Records

Decisions that shape the application, one file per decision. A decision is recorded here before or when it is implemented, and a new dependency needs one (see `CLAUDE.md`).

## Folders

- `docs/adr/`: decisions in force.
- `docs/adr/archive/`: decisions that were superseded or deprecated. This is the history.
- `docs/adr/_template/`: the ADR template. Copy it, do not edit it per decision.

## Rules

1. Number ADRs with the next free four-digit number, for example `0009-<slug>.md`. Never reuse a number, even for a withdrawn ADR.
2. Every ADR has these header lines: `Status`, `Date`, `Supersedes`, `Superseded by`.
3. To change a decision, write a new ADR. Set its `Supersedes` line to the old ADR, for example `Supersedes: ADR-0003`. Do not rewrite the old decision.
4. In the same change, update the old ADR and move it to `archive/`:
   - set `Status: Superseded by ADR-NNNN`,
   - set `Superseded by: ADR-NNNN`,
   - move the file into `docs/adr/archive/`.
   Its content stays as it was written.
5. A decision that is dropped without a replacement becomes `Status: Deprecated` and moves to `archive/`. Its `Superseded by` line stays `none`.
6. A new ADR can supersede more than one ADR. Every superseded ADR gets rule 4. Put all of them on the `Supersedes` line, separated by commas.
7. A new ADR can be written as `Proposed` while it is still being decided. Do not supersede an ADR until the new one is `Accepted`.
8. Update the index below when an ADR is added or archived.

## Index: decisions in force

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-local-web-app-with-http-api.md) | Local web app with an HTTP API | Accepted |
| [0003](0003-sqlite-local-persistence.md) | SQLite as local persistence | Accepted |
| [0005](0005-human-approval-for-every-ai-output.md) | Human approval for every AI output | Accepted |
| [0006](0006-fastapi-and-pydantic-backend.md) | FastAPI and Pydantic for the backend | Accepted |
| [0007](0007-python-and-frontend-tooling.md) | Python and frontend tooling | Accepted |
| [0008](0008-claude-agent-sdk-for-llm-calls.md) | Claude Agent SDK for LLM calls | Accepted |
| [0009](0009-backend-server-and-listen-address.md) | Backend server and listen address | Accepted |
| [0010](0010-sqlite-migrations-with-user-version.md) | SQLite migrations with user_version | Accepted |
| [0011](0011-frontend-dependencies.md) | Frontend dependencies | Accepted |

## Index: archive

| ADR | Title | Status |
| --- | --- | --- |
| [0004](archive/0004-claude-api-as-llm-provider.md) | Claude API as the LLM provider | Superseded by ADR-0008 |
