# ADR-0003: SQLite as local persistence

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The application stores candidates, proposals, decisions and AI output records. It runs for one user on one machine, and the data must stay local (ADR-0002).

## Decision

Persistence is SQLite, stored as a local file under `data/`. The file is not committed to git.

## Consequences

- No database server to install or run.
- Backups are the user's responsibility. The application does not manage them.
- The schema needs versioned migrations, so the first migration tool choice is a follow-up.
- Uploaded CV files, if kept, are stored under `data/` as well. Whether they are kept is an open question in `CLAUDE.md`.

## Alternatives considered

- PostgreSQL: rejected, because it adds a server for a single-user local app.
- Plain JSON files: rejected, because the records need queries and transactional writes for the approval workflow.
