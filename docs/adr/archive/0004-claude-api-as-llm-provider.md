# ADR-0004: Claude API as the LLM provider

Status: Superseded by ADR-0008
Date: 2026-10-15
Supersedes: none
Superseded by: ADR-0008

## Context

The features need a large language model to draft job descriptions, propose interview questions and summarise screening (`CLAUDE.md`, Tech Stack). Candidate-derived text is sent to the provider, so the choice affects candidate data handling.

## Decision

The LLM provider is the Anthropic Claude API, called through the `anthropic` Python SDK. Only the backend calls it. Each call is recorded with its inputs and model ID before its result reaches the hiring manager (ADR-0005).

## Consequences

- Prompts containing candidate-derived text leave the machine. The architecture diagrams list exactly what is sent (`docs/architecture/`).
- Raw CV files are not sent. Only extracted text is, as documented in `candidate-screening.md`.
- Switching provider later touches only the backend module that wraps the SDK, provided every call goes through that module. Keep it that way.
- Model IDs change over time, so the record of each output must store the exact model ID used.

## Alternatives considered

- Other hosted LLM providers: not evaluated in this record. Revisit if the Claude API stops meeting the needs of the features.
- Local open-weight model: rejected for now, because the features need a quality level this record does not assess. Revisit with a new ADR if candidate data handling becomes a stronger constraint.
