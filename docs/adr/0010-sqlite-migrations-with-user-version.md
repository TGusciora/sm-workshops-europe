# ADR-0010: SQLite migrations with user_version

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

ADR-0003 requires versioned migrations for the SQLite schema and left the migration tool as a follow-up. The schema for F0001 to F0003 is small, and the application has one user on one machine.

## Decision

Migrations are plain SQL strings kept in the backend code, in an ordered list. The schema version is stored in SQLite's built-in `user_version` pragma. On startup, the backend applies each migration whose number is higher than the stored version, in one transaction per migration. No migration library is added.

## Consequences

- No new dependency. The schema history is the list in the code and is read in `git log`.
- Migrations are forward-only. A rollback is a new migration.
- If the schema grows to need branching or down-migrations, a new ADR can adopt a migration library such as Alembic.

## Alternatives considered

- Alembic: not chosen now, because it adds a dependency and configuration for a schema of a few tables.
- A `schema_migrations` table: not chosen, because `user_version` does the same job without a table.
