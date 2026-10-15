# Feature name

Status: draft
Ticket: `spec/features/<folder>/FNNNN-<slug>.md`
Last reviewed: YYYY-MM-DD

## Purpose

What the hiring manager does in this flow, in one or two sentences.

## Participants

- **Hiring manager**: the person using the application.
- **Frontend**: React single-page application. Talks to the backend over HTTP only.
- **Backend**: Python server on the interviewer's machine.
- **SQLite**: local database under `data/`.
- **Claude API**: the LLM provider. The only external service in the flow.

Add participants only when they appear in the sequence below.

## Sequence

```mermaid
sequenceDiagram
    autonumber
    actor HM as Hiring manager
    participant UI as Frontend
    participant API as Backend
    participant DB as SQLite
    participant LLM as Claude API

    HM->>UI: Action
    UI->>API: Request
    API->>LLM: Prompt with inputs
    LLM-->>API: Proposal
    API->>DB: Store proposal with inputs and model ID
    API-->>UI: Proposal
    UI->>HM: Show proposal for review
    HM->>UI: Approve, edit or reject
    UI->>API: Decision
    API->>DB: Store final result with decision
```

## Human decision points

- Step where the hiring manager decides, and what they can do: approve, edit, reject.

## Records kept

- What is stored, where, and for how long.
- For each AI output: inputs, model ID, prompt version, timestamp.

## Data leaving the machine

- The exact fields sent to the Claude API in each request.

## Open questions

- Question that the diagram depends on.
