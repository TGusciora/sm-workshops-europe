# ADR-0002: Local web app with an HTTP API

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The application is for one hiring manager, and candidate data must stay on the interviewer's machine (`CLAUDE.md`, Goal). A hosted service would move that data off the machine.

## Decision

The application runs on the interviewer's own machine as two parts: a React and TypeScript single-page frontend, and a Python backend. The frontend talks to the backend only over HTTP. The frontend never calls the Claude API or the Internal system directly.

## Consequences

- Candidate data stays local except for the calls the features need (see ADR-0008).
- The HTTP boundary keeps the backend as the only place that holds credentials and calls external services.
- There is no multi-user access or shared state. Adding either later needs a new ADR.
- The address the backend listens on is not decided yet. It must be decided before the backend first runs.

## Alternatives considered

- Desktop app with an embedded webview: rejected for now, because it adds packaging work before any feature exists.
- Hosted web service: rejected, because it moves candidate data off the machine.
