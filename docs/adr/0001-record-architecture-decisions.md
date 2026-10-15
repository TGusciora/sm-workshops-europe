# ADR-0001: Record architecture decisions

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The application has several decisions that future work depends on: the stack, the local-first setup, and the human approval boundary. Without a record, they live only in chat history or in people's heads, and they are hard to revisit safely.

## Decision

Architecture decisions are recorded as numbered ADRs in `docs/adr/`. Decisions that change are superseded by a new ADR, and the old one moves to `docs/adr/archive/`. The rules are in `docs/adr/README.md`.

## Consequences

- Each new dependency or structural choice needs an ADR, as `CLAUDE.md` already requires.
- Superseded decisions stay readable in `archive/`, so the reasoning behind past choices can be traced.
- Writing an ADR costs a few minutes per decision. That is the accepted trade-off.

## Alternatives considered

- Decisions in `CLAUDE.md` only: rejected, because the file would grow into a history and lose the reasoning for each choice.
- Decisions in issue tickets: rejected, because tickets are about work to do, and decisions must outlive the work.
